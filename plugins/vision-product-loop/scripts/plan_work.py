#!/usr/bin/env python3
"""Plan sprint-sized Vision Product Loop work for an applied project."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import discover_project  # noqa: E402
import scaffold_knowledge_map  # noqa: E402


DEFAULT_STATE_PATH = Path(".vision-loop") / "state.json"
TASK_END_SCRIPT_PRIORITY = (
    "web:typecheck",
    "web:test",
    "test",
    "agent:eval",
    "gateway:eval",
    "agent:eval:multi-step",
    "eval:all",
)


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def slugify(text: str, fallback: str = "task") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:72].strip("-") or fallback


def markdown_sections(path: Path, heading_level: int = 2) -> list[dict[str, str]]:
    if not path.is_file():
        return []

    marker = "#" * heading_level
    sections: list[dict[str, str]] = []
    current_title: str | None = None
    current_body: list[str] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{marker} ") and not line.startswith(f"{marker}#"):
            if current_title:
                sections.append(
                    {
                        "title": current_title,
                        "body": "\n".join(current_body).strip(),
                    }
                )
            current_title = line.removeprefix(f"{marker} ").strip()
            current_body = []
        elif current_title:
            current_body.append(line)

    if current_title:
        sections.append({"title": current_title, "body": "\n".join(current_body).strip()})

    return sections


def section_is_done(section: dict[str, str]) -> bool:
    body = section.get("body", "")
    match = re.search(r"(?im)^status:\s*(.+)$", body)
    if not match:
        return False
    status = match.group(1).lower()
    return bool(re.search(r"\b(done|closed|complete)\b", status))


def extract_line(body: str, label: str) -> str:
    pattern = re.compile(rf"(?im)^{re.escape(label)}:\s*(.+)$")
    match = pattern.search(body)
    return match.group(1).strip() if match else ""


def open_state_gaps(root: Path, state_path: Path) -> list[dict[str, Any]]:
    state = load_json(state_path if state_path.is_absolute() else root / state_path)
    if not state:
        return []
    gaps = state.get("gaps", [])
    if not isinstance(gaps, list):
        return []
    return [
        gap
        for gap in gaps
        if isinstance(gap, dict)
        and str(gap.get("status", "open")).lower() not in {"closed", "done", "complete"}
    ]


def open_todos(root: Path) -> list[dict[str, str]]:
    return [
        section
        for section in markdown_sections(root / "TODOS.md")
        if not section_is_done(section)
    ]


def choose_task_source(root: Path, state_path: Path, goal: str | None) -> dict[str, str]:
    if goal:
        return {
            "source": "user-goal",
            "title": goal,
            "vision_anchor": "User-provided goal for this planning run.",
            "context": "",
        }

    gaps = open_state_gaps(root, state_path)
    if gaps:
        gap = gaps[0]
        return {
            "source": "loop-state-gap",
            "title": str(gap.get("id") or gap.get("title") or "Open vision gap"),
            "vision_anchor": str(gap.get("vision_anchor") or gap.get("evidence") or ""),
            "context": str(gap.get("recommendation") or ""),
        }

    todos = open_todos(root)
    if todos:
        todo = todos[0]
        body = todo.get("body", "")
        return {
            "source": "todos",
            "title": todo["title"],
            "vision_anchor": extract_line(body, "Why") or "Open project TODO.",
            "context": extract_line(body, "Context"),
        }

    return {
        "source": "vision",
        "title": "Plan the next vision-backed product task",
        "vision_anchor": "No open loop-state gap or TODO was found; select the next highest-leverage acceptance gap from VISION.md.",
        "context": "",
    }


def package_script_commands(discovery: dict[str, Any]) -> dict[str, str]:
    commands: dict[str, str] = {}
    for harness in discovery.get("harnesses", []):
        if not isinstance(harness, dict):
            continue
        if harness.get("kind") != "package-script":
            continue
        name = str(harness.get("name", ""))
        command = str(harness.get("command", ""))
        if name and command:
            commands[name] = command
    return commands


def task_end_commands(discovery: dict[str, Any]) -> list[str]:
    scripts = package_script_commands(discovery)
    commands: list[str] = []
    for name in TASK_END_SCRIPT_PRIORITY:
        command = scripts.get(name)
        if command:
            commands.append(command)
    return commands or ["Run the strongest project-local validation harness."]


def build_subtasks(task_id: str, source: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "id": f"{task_id}-brief",
            "title": "Write the task brief and acceptance checks",
            "done_when": "Operator outcome, non-goals, impacted surfaces, and task-close evidence are explicit.",
            "validation": "review",
            "broad_tests": "defer_to_task_close",
        },
        {
            "id": f"{task_id}-map",
            "title": "Map implementation boundaries before editing",
            "done_when": "Code areas, data flow, docs, skills, and harnesses are named with risks.",
            "validation": "inspection_or_focused_probe",
            "broad_tests": "defer_to_task_close",
        },
        {
            "id": f"{task_id}-build",
            "title": "Implement the bounded product change",
            "done_when": "The requested behavior is implemented without expanding the task promise.",
            "validation": "focused_check_only_if_it_directly_de-risks_the_subtask",
            "broad_tests": "defer_to_task_close",
        },
        {
            "id": f"{task_id}-close",
            "title": "Close the task with evidence and reflection",
            "done_when": "Task-close harnesses pass or failures are explained, and remaining gaps are recorded.",
            "validation": "task_end_validation",
            "broad_tests": "run_now",
        },
    ]


def plan_work(
    root: Path,
    goal: str | None = None,
    state_path: Path = DEFAULT_STATE_PATH,
    max_files: int = 2000,
    enforce_knowledge_map_gate: bool = True,
) -> dict[str, Any]:
    """Return a sprint/task/subtask plan with task-end validation cadence.

    When `enforce_knowledge_map_gate` is true (default) and `docs/adr/` holds
    no product ADRs, the returned plan carries a top-level `gate` block and
    omits the sprint scaffold so callers refuse to advance to Build before the
    architecture grill has happened.
    """
    root = root.resolve()
    if enforce_knowledge_map_gate:
        gate = scaffold_knowledge_map.knowledge_map_gate(root)
        if gate is not None:
            return {
                "root": str(root),
                "planning_granularity": "sprint_task_subtask",
                "test_cadence": "task_end",
                "gate": gate,
            }
    discovery = discover_project.discover_project(root, max_files=max_files)
    source = choose_task_source(root, state_path, goal)
    task_id = slugify(source["title"])
    commands = task_end_commands(discovery)

    task = {
        "id": task_id,
        "title": source["title"],
        "source": source["source"],
        "vision_anchor": source["vision_anchor"],
        "context": source["context"],
        "subtasks": build_subtasks(task_id, source),
        "validation": {
            "cadence": "task_end",
            "subtask_policy": (
                "Do not run broad regression, typecheck, or eval suites at every subtask. "
                "Use inspection or a focused probe only when it directly de-risks the subtask."
            ),
            "task_close_commands": commands,
        },
    }

    return {
        "root": str(root),
        "planning_granularity": "sprint_task_subtask",
        "test_cadence": "task_end",
        "sprint": {
            "id": f"{task_id}-sprint",
            "goal": f"Close one coherent product task: {source['title']}",
            "tasks": [task],
            "definition_of_done": [
                "All subtasks are complete.",
                "Task-close validation has run once for the full task.",
                "Evidence and remaining gaps are recorded in the project loop state.",
            ],
        },
        "discovery_summary": {
            "docs": discovery.get("docs", []),
            "agent_count": len(discovery.get("agents", [])),
            "architecture": discovery.get("architecture", []),
            "harness_count": len(discovery.get("harnesses", [])),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plan sprint/task/subtask work for an applied Vision Product Loop project."
    )
    parser.add_argument("--root", default=".", help="Project root to plan against.")
    parser.add_argument("--goal", help="Optional task goal to plan instead of selecting from state or TODOs.")
    parser.add_argument(
        "--state",
        default=str(DEFAULT_STATE_PATH),
        help="Loop state path, relative to --root unless absolute.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=2000,
        help="Maximum files to inspect while discovering project signals.",
    )
    parser.add_argument("--json", action="store_true", help="Print plan JSON.")
    parser.add_argument(
        "--skip-knowledge-map-gate",
        action="store_true",
        help=(
            "Bypass the knowledge-map gate. Use only for diagnostics; the loop "
            "should normally refuse to plan Build work without recorded ADRs."
        ),
    )
    args = parser.parse_args()

    plan = plan_work(
        Path(args.root),
        goal=args.goal,
        state_path=Path(args.state),
        max_files=args.max_files,
        enforce_knowledge_map_gate=not args.skip_knowledge_map_gate,
    )
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
