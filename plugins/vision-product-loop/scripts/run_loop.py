#!/usr/bin/env python3
"""Run the Vision Product Loop operating cycle against a project.

This runner handles deterministic orchestration. Product judgment still belongs
to the Codex skill, but this script gives the loop a concrete control plane:
Research, Build, Verify, Test, Reflect, then write durable state.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import discover_project  # noqa: E402
import self_check  # noqa: E402
import vision_checklist  # noqa: E402


PLUGIN_NAME = "vision-product-loop"
DEFAULT_PLUGIN_ROOT = Path("plugins") / PLUGIN_NAME
DEFAULT_STATE_PATH = Path(".vision-loop") / "state.json"
DEFAULT_VISION_FILE = Path("VISION.md")


BASE_EVIDENCE_CHECKS = (
    "vision_exists",
    "self_check_exists",
    "manifest_json",
    "skill_exists",
    "readme_exists",
    "self_check_tests_exist",
    "capability_rubric_loaded",
    "applied_project_proof",
)


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def evidence_passed(evidence: list[dict[str, Any]], check: str) -> bool:
    return any(item.get("check") == check and item.get("passed") for item in evidence)


def required_evidence_passed(
    evidence: list[dict[str, Any]],
    require_validation: bool,
) -> bool:
    required = list(BASE_EVIDENCE_CHECKS)
    if require_validation:
        required.append("validation_tests")
    return all(evidence_passed(evidence, check) for check in required)


def build_harness_registry(require_validation: bool) -> list[dict[str, Any]]:
    harnesses = [
        {
            "id": "plugin-self-check",
            "kind": "command",
            "command": "python3 plugins/vision-product-loop/scripts/self_check.py --json",
            "proves": [
                "VISION.md exists",
                "plugin manifest loads",
                "main skill exists",
                "capability rubric markers are satisfied",
                "applied project proof is recorded before completion",
            ],
            "pass_condition": "exit code 0 when a gap is selected or the vision is complete",
        }
    ]
    if require_validation:
        harnesses.append(
            {
                "id": "plugin-unittest-suite",
                "kind": "command",
                "command": "python3 -m unittest discover -s plugins/vision-product-loop/tests",
                "proves": [
                    "plugin helper scripts satisfy regression tests",
                    "rubric-backed capability tests still pass",
                ],
                "pass_condition": "exit code 0",
            }
        )
    return harnesses


def checklist_summary(root: Path) -> dict[str, Any]:
    checklist = vision_checklist.build_checklist(root, root / DEFAULT_VISION_FILE, 12)
    return {
        "vision_file": relative_to_root(Path(checklist.vision_file), root),
        "headings": checklist.headings,
        "missing_sections": checklist.missing_sections,
        "acceptance_candidate_count": len(checklist.acceptance_candidates),
    }


def phase_event(phase: str, summary: str, **extra: Any) -> dict[str, Any]:
    event = {
        "phase": phase,
        "summary": summary,
    }
    event.update(extra)
    return event


def build_final_state(
    root: Path,
    iteration: int,
    self_state: dict[str, Any],
    discovery: dict[str, Any],
    checklist: dict[str, Any],
    loop_events: list[dict[str, Any]],
    status: str,
    stop_reason: str,
    reflection: str,
    next_actions: list[str],
    require_validation: bool,
) -> dict[str, Any]:
    gaps = self_state.get("gaps", [])
    return {
        "vision_file": str(DEFAULT_VISION_FILE),
        "phase": "reflect",
        "iteration": iteration,
        "current_task": "Run the Vision Product Loop operating cycle against VISION.md.",
        "subtasks": [],
        "current_slice": "Run the Vision Product Loop operating cycle against VISION.md.",
        "gaps": gaps,
        "selected_gap": self_state.get("selected_gap"),
        "harnesses": build_harness_registry(require_validation),
        "evidence": self_state.get("evidence", []),
        "discovery": {
            "docs": discovery.get("docs", []),
            "agents": discovery.get("agents", []),
            "architecture": discovery.get("architecture", []),
            "harness_count": len(discovery.get("harnesses", [])),
        },
        "checklist": checklist,
        "loop_events": loop_events,
        "reflection": reflection,
        "status": status,
        "stop_reason": stop_reason,
        "remaining_gaps": gaps,
        "next_actions": next_actions,
        "root": str(root),
    }


def run_loop(
    root: Path,
    plugin_root: Path,
    state_path: Path,
    slice_budget: int = 5,
    run_tests: bool = True,
) -> tuple[dict[str, Any], int]:
    """Run deterministic loop phases and write durable loop state."""
    root = root.resolve()
    plugin_root = plugin_root.resolve()
    state_path = state_path.resolve()
    previous_state = load_json(state_path)
    loop_events: list[dict[str, Any]] = []

    if slice_budget < 1:
        raise ValueError("slice_budget must be at least 1")

    for iteration in range(1, slice_budget + 1):
        discovery = discover_project.discover_project(root)
        checklist = checklist_summary(root)
        loop_events.append(
            phase_event(
                "research",
                "Read VISION.md, project context, discovery output, prior state, and capability evidence.",
                docs=discovery.get("docs", []),
                harness_count=len(discovery.get("harnesses", [])),
                previous_status=(previous_state or {}).get("status"),
                checklist_missing_sections=checklist["missing_sections"],
            )
        )

        self_state, self_exit_code = self_check.run_self_check(
            root,
            plugin_root,
            state_path,
            run_tests=run_tests,
        )
        gaps = self_state.get("gaps", [])
        evidence = self_state.get("evidence", [])

        if gaps:
            loop_events.append(
                phase_event(
                    "build",
                    "A concrete gap was selected; hand control back to the Codex skill to patch the selected slice.",
                    selected_gap=self_state.get("selected_gap", {}).get("id"),
                )
            )
            loop_events.append(
                phase_event(
                    "reflect",
                    "The loop found a gap that needs an implementation slice before completion.",
                    stop_reason="gap_selected",
                )
            )
            final_state = build_final_state(
                root,
                iteration,
                self_state,
                discovery,
                checklist,
                loop_events,
                "planning",
                "gap_selected",
                f"Selected gap {self_state.get('selected_gap', {}).get('id')}; run another build slice.",
                [
                    "Address the selected gap.",
                    "Rerun run_loop.py with the same slice budget.",
                ],
                run_tests,
            )
            write_json(state_path, final_state)
            return final_state, 0

        loop_events.append(
            phase_event(
                "build",
                "No scaffold patch was needed in this iteration; the current artifacts satisfy the rubric markers.",
                changed_files=[],
            )
        )
        loop_events.append(
            phase_event(
                "verify",
                "Verified bootstrap checks and applied-project evidence against VISION.md.",
                self_check_exit_code=self_exit_code,
                direct_evidence_passed=required_evidence_passed(
                    evidence,
                    require_validation=False,
                ),
            )
        )
        loop_events.append(
            phase_event(
                "test",
                "Ran regression validation when requested.",
                validation_required=run_tests,
                validation_passed=(
                    evidence_passed(evidence, "validation_tests") if run_tests else None
                ),
            )
        )

        if required_evidence_passed(evidence, require_validation=run_tests):
            loop_events.append(
                phase_event(
                    "reflect",
                    "No gaps remain in the current rubric and the strongest requested evidence passed.",
                    stop_reason="vision_complete",
                )
            )
            final_state = build_final_state(
                root,
                iteration,
                self_state,
                discovery,
                checklist,
                loop_events,
                "complete",
                "vision_complete",
                (
                    "VISION.md is realized by the current plugin scaffold under the "
                    "capability rubric and requested validation evidence."
                ),
                [],
                run_tests,
            )
            write_json(state_path, final_state)
            return final_state, 0

        loop_events.append(
            phase_event(
                "reflect",
                "The self-check found no rubric gaps, but required evidence did not pass.",
                stop_reason="validation_failed",
            )
        )
        final_state = build_final_state(
            root,
            iteration,
            self_state,
            discovery,
            checklist,
            loop_events,
            "blocked",
            "validation_failed",
            "The loop cannot mark the vision complete until required evidence passes.",
            ["Inspect failing evidence and rerun run_loop.py."],
            run_tests,
        )
        write_json(state_path, final_state)
        return final_state, 2

    final_state = {
        "vision_file": str(DEFAULT_VISION_FILE),
        "phase": "reflect",
        "iteration": slice_budget,
        "current_task": "Run the Vision Product Loop operating cycle against VISION.md.",
        "subtasks": [],
        "status": "blocked",
        "stop_reason": "slice_budget_exhausted",
        "loop_events": loop_events,
        "next_actions": ["Increase --slice-budget or reduce the next slice size."],
    }
    write_json(state_path, final_state)
    return final_state, 3


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Vision Product Loop operating cycle."
    )
    parser.add_argument("--root", default=".", help="Project root containing VISION.md.")
    parser.add_argument(
        "--plugin-root",
        default=str(DEFAULT_PLUGIN_ROOT),
        help="Plugin root to inspect.",
    )
    parser.add_argument(
        "--state",
        default=str(DEFAULT_STATE_PATH),
        help="Machine-readable loop state file to write.",
    )
    parser.add_argument(
        "--slice-budget",
        type=int,
        default=5,
        help="Maximum autonomous loop slices to run.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip plugin unittest validation during the Test phase.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full state JSON instead of a compact summary.",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    plugin_root = (root / args.plugin_root).resolve()
    state_path = (root / args.state).resolve()

    state, exit_code = run_loop(
        root,
        plugin_root,
        state_path,
        slice_budget=args.slice_budget,
        run_tests=not args.skip_tests,
    )

    if args.json:
        print(json.dumps(state, indent=2))
    else:
        print(f"status: {state['status']}")
        print(f"stop_reason: {state['stop_reason']}")
        print(f"state: {state_path}")
        print(f"iteration: {state.get('iteration', 0)}")

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
