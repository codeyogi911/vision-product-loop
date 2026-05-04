#!/usr/bin/env python3
"""Self-check harness for the Vision Product Loop plugin.

The skill owns product judgment. This script handles repeatable mechanics:
read the canonical vision, inspect the plugin scaffold, write machine state,
and make sure at least one next gap is available unless the loop is complete.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


PLUGIN_NAME = "vision-product-loop"
DEFAULT_PLUGIN_ROOT = Path("plugins") / PLUGIN_NAME
DEFAULT_STATE_PATH = Path(".vision-loop") / "state.json"
DEFAULT_VISION_FILE = Path("VISION.md")
DEFAULT_RUBRIC_FILE = Path("capability_rubric.json")


@dataclass
class Gap:
    id: str
    title: str
    evidence: str
    recommendation: str
    file: str | None = None


@dataclass
class Evidence:
    check: str
    passed: bool
    detail: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def contains_all(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return all(needle.lower() in lowered for needle in needles)


def resolve_artifact(root: Path, plugin_root: Path, artifact: str) -> Path:
    if artifact.startswith("root:"):
        return root / artifact.removeprefix("root:")
    if artifact.startswith("plugin:"):
        return plugin_root / artifact.removeprefix("plugin:")
    raise ValueError(f"Unsupported artifact location: {artifact}")


def add_gap(
    gaps: list[Gap],
    gap_id: str,
    title: str,
    evidence: str,
    recommendation: str,
    file: Path | None = None,
) -> None:
    gaps.append(
        Gap(
            id=gap_id,
            title=title,
            evidence=evidence,
            recommendation=recommendation,
            file=str(file) if file else None,
        )
    )


def inspect_manifest(manifest_path: Path, gaps: list[Gap], evidence: list[Evidence]) -> None:
    if not manifest_path.is_file():
        evidence.append(Evidence("manifest_exists", False, f"Missing {manifest_path}"))
        add_gap(
            gaps,
            "missing-plugin-manifest",
            "Plugin manifest is missing",
            f"{manifest_path} does not exist.",
            "Create .codex-plugin/plugin.json with the plugin name and skills path.",
            manifest_path,
        )
        return

    try:
        manifest = load_json(manifest_path)
    except json.JSONDecodeError as exc:
        evidence.append(Evidence("manifest_json", False, str(exc)))
        add_gap(
            gaps,
            "invalid-plugin-manifest-json",
            "Plugin manifest is not valid JSON",
            str(exc),
            "Fix the manifest so Codex can load the plugin metadata.",
            manifest_path,
        )
        return

    evidence.append(Evidence("manifest_json", True, f"Loaded {manifest_path}"))
    if manifest.get("name") != PLUGIN_NAME:
        add_gap(
            gaps,
            "manifest-name-mismatch",
            "Manifest name does not match plugin folder",
            f"Expected {PLUGIN_NAME!r}, found {manifest.get('name')!r}.",
            "Set plugin.json name to vision-product-loop.",
            manifest_path,
        )
    if manifest.get("skills") != "./skills/":
        add_gap(
            gaps,
            "manifest-skills-path-missing",
            "Manifest does not expose the skills directory",
            f"Expected skills path './skills/', found {manifest.get('skills')!r}.",
            "Set the manifest skills field to ./skills/.",
            manifest_path,
        )


def inspect_skill(skill_path: Path, gaps: list[Gap], evidence: list[Evidence]) -> None:
    if not skill_path.is_file():
        evidence.append(Evidence("skill_exists", False, f"Missing {skill_path}"))
        add_gap(
            gaps,
            "missing-main-skill",
            "Main plugin skill is missing",
            f"{skill_path} does not exist.",
            "Create skills/vision-product-loop/SKILL.md.",
            skill_path,
        )
        return

    skill_text = read_text(skill_path)
    evidence.append(Evidence("skill_exists", True, f"Loaded {skill_path}"))

    skill_requirements = (
        (
            "skill-canonical-vision-md",
            "Skill does not clearly treat uppercase VISION.md as canonical",
            ("VISION.md",),
            "Update the skill to prefer project-root VISION.md as the durable product contract.",
        ),
        (
            "skill-machine-loop-state",
            "Skill does not define machine-readable loop state",
            (".vision-loop/state.json",),
            "Update the skill to use .vision-loop/state.json for operational loop state.",
        ),
        (
            "skill-owned-loop",
            "Skill does not clearly own the loop",
            ("skill owns the loop",),
            "State that scripts are helpers and the Codex skill drives judgment and iteration.",
        ),
        (
            "skill-self-check-harness",
            "Skill does not mention the self-check harness",
            ("self-check", "harness"),
            "Document scripts/self_check.py as the first deterministic harness.",
        ),
        (
            "skill-shortest-evidence-path",
            "Skill does not encode the shortest evidence path bias",
            ("shortest evidence path",),
            "Add the slice-selection rule from VISION.md.",
        ),
        (
            "skill-missing-tools-generation",
            "Skill does not say to create missing proof tools",
            ("create", "missing", "harness"),
            "Tell the skill to create the smallest missing harness, skill, script, or evaluator needed to prove progress.",
        ),
        (
            "skill-autonomy-boundary",
            "Skill does not capture the autonomy boundary",
            ("stop and ask", "destructive", "marketplace"),
            "Add the boundary for edits, network-dependent tools, publishing, and destructive changes.",
        ),
        (
            "skill-batch-loop-execution",
            "Skill does not describe multi-slice batch execution",
            ("slice budget", "why it stopped"),
            "Teach the skill to run multiple autonomous slices in one pass and explain why it stops.",
        ),
        (
            "skill-end-to-end-realization",
            "Skill does not clearly describe end-to-end project realization",
            ("end to end", "provide", "select", "orchestrate"),
            "Add the proper-scaffold contract: the plugin should provide, select, create, or orchestrate whatever tools are needed to reach the vision.",
        ),
    )

    for gap_id, title, needles, recommendation in skill_requirements:
        if not contains_all(skill_text, needles):
            add_gap(
                gaps,
                gap_id,
                title,
                f"Missing required marker(s): {', '.join(needles)}.",
                recommendation,
                skill_path,
            )


def inspect_readme(readme_path: Path, gaps: list[Gap], evidence: list[Evidence]) -> None:
    if not readme_path.is_file():
        evidence.append(Evidence("readme_exists", False, f"Missing {readme_path}"))
        add_gap(
            gaps,
            "missing-readme",
            "Plugin README is missing",
            f"{readme_path} does not exist.",
            "Add README usage docs for the self-loop workflow.",
            readme_path,
        )
        return

    readme_text = read_text(readme_path)
    evidence.append(Evidence("readme_exists", True, f"Loaded {readme_path}"))
    if "self_check.py" not in readme_text and "self-check" not in readme_text.lower():
        add_gap(
            gaps,
            "readme-self-check-docs",
            "README does not document the self-check harness",
            "README lacks self-check usage.",
            "Add the self-check command and explain .vision-loop/state.json.",
            readme_path,
        )
    if not contains_all(readme_text, ("slice budget", "why it stopped")):
        add_gap(
            gaps,
            "readme-batch-loop-docs",
            "README does not document batch loop execution",
            "README lacks slice budget and stop-reason guidance.",
            "Document how the plugin can run multiple slices in one pass and report why it stopped.",
            readme_path,
        )
    if not contains_all(readme_text, ("end to end", "provide", "select", "orchestrate")):
        add_gap(
            gaps,
            "readme-end-to-end-docs",
            "README does not document end-to-end realization",
            "README lacks the adaptive product-building contract.",
            "Explain that the plugin can provide, select, create, or orchestrate the tools needed to realize the vision end to end.",
            readme_path,
        )


def inspect_tests(plugin_root: Path, gaps: list[Gap], evidence: list[Evidence]) -> None:
    tests_path = plugin_root / "tests" / "test_self_check.py"
    if tests_path.is_file():
        evidence.append(Evidence("self_check_tests_exist", True, f"Loaded {tests_path}"))
        return

    evidence.append(Evidence("self_check_tests_exist", False, f"Missing {tests_path}"))
    add_gap(
        gaps,
        "missing-self-check-tests",
        "Self-check harness has no regression tests",
        f"{tests_path} does not exist.",
        "Add tests that prove the harness writes .vision-loop/state.json and reports concrete gaps.",
        tests_path,
    )


def inspect_capability_rubric(
    root: Path,
    plugin_root: Path,
    gaps: list[Gap],
    evidence: list[Evidence],
) -> None:
    rubric_path = plugin_root / DEFAULT_RUBRIC_FILE
    if not rubric_path.is_file():
        evidence.append(Evidence("capability_rubric_exists", False, f"Missing {rubric_path}"))
        add_gap(
            gaps,
            "missing-capability-rubric",
            "Capability rubric is missing",
            f"{rubric_path} does not exist.",
            "Add capability_rubric.json so the self-check can evaluate product-level capabilities.",
            rubric_path,
        )
        return

    try:
        rubric = load_json(rubric_path)
    except json.JSONDecodeError as exc:
        evidence.append(Evidence("capability_rubric_json", False, str(exc)))
        add_gap(
            gaps,
            "invalid-capability-rubric-json",
            "Capability rubric is not valid JSON",
            str(exc),
            "Fix capability_rubric.json.",
            rubric_path,
        )
        return

    capabilities = rubric.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        evidence.append(
            Evidence("capability_rubric_has_capabilities", False, "No capabilities found")
        )
        add_gap(
            gaps,
            "empty-capability-rubric",
            "Capability rubric has no capabilities",
            "capability_rubric.json must include a non-empty capabilities array.",
            "Define capability checks for the product loop.",
            rubric_path,
        )
        return

    evidence.append(
        Evidence(
            "capability_rubric_loaded",
            True,
            f"Loaded {len(capabilities)} capabilities from {rubric_path}",
        )
    )

    for capability in capabilities:
        capability_id = capability.get("id", "unnamed")
        requirements = capability.get("requirements", [])
        if not isinstance(requirements, list) or not requirements:
            add_gap(
                gaps,
                f"capability-{capability_id}-has-no-requirements",
                f"Capability {capability_id} has no requirements",
                "Capability entries need at least one requirement.",
                "Add concrete artifact requirements to the capability rubric.",
                rubric_path,
            )
            continue

        for requirement in requirements:
            requirement_id = requirement.get("id", "unnamed")
            artifact = requirement.get("artifact")
            needles = tuple(requirement.get("all", []))
            if not artifact or not needles:
                add_gap(
                    gaps,
                    f"capability-{capability_id}-{requirement_id}-invalid",
                    f"Capability requirement {requirement_id} is invalid",
                    "Requirement must include artifact and non-empty all markers.",
                    "Fix the capability rubric requirement shape.",
                    rubric_path,
                )
                continue

            try:
                artifact_path = resolve_artifact(root, plugin_root, artifact)
            except ValueError as exc:
                add_gap(
                    gaps,
                    f"capability-{capability_id}-{requirement_id}-artifact-location",
                    f"Capability requirement {requirement_id} uses an unsupported artifact",
                    str(exc),
                    "Use root:<path> or plugin:<path> artifact locations.",
                    rubric_path,
                )
                continue

            if not artifact_path.is_file():
                add_gap(
                    gaps,
                    f"capability-{capability_id}-{requirement_id}-missing-artifact",
                    f"Capability {capability_id} is missing an artifact",
                    f"{artifact_path} does not exist.",
                    f"Create {artifact_path.name} or update the capability rubric.",
                    artifact_path,
                )
                continue

            artifact_text = read_text(artifact_path)
            missing = [needle for needle in needles if needle.lower() not in artifact_text.lower()]
            if missing:
                add_gap(
                    gaps,
                    f"capability-{capability_id}-{requirement_id}-missing-markers",
                    f"Capability {capability_id} is not satisfied",
                    f"{artifact_path} is missing marker(s): {', '.join(missing)}.",
                    "Update the artifact or adjust the rubric if the requirement is wrong.",
                    artifact_path,
                )


def run_validation_tests(root: Path, plugin_root: Path, gaps: list[Gap]) -> Evidence:
    command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(plugin_root / "tests"),
    ]
    result = subprocess.run(
        command,
        cwd=root,
        env={**os.environ, "VISION_LOOP_SKIP_VALIDATION_CAPTURE": "1"},
        text=True,
        capture_output=True,
        check=False,
    )
    output = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    detail = f"{' '.join(command)} exited {result.returncode}"
    if output:
        detail = f"{detail}: {output[-800:]}"
    passed = result.returncode == 0
    if not passed:
        add_gap(
            gaps,
            "validation-tests-failing",
            "Validation tests are failing",
            detail,
            "Fix the plugin tests or implementation before claiming progress.",
            plugin_root / "tests",
        )
    return Evidence("validation_tests", passed, detail)


def inspect_toy_project_proof(root: Path, evidence: list[Evidence]) -> None:
    proof_path = root / ".vision-loop" / "toy-project" / ".vision-loop" / "toy-proof.json"
    if not proof_path.is_file():
        return
    try:
        proof = load_json(proof_path)
    except json.JSONDecodeError as exc:
        evidence.append(Evidence("toy_project_proof", False, str(exc)))
        return
    target = proof.get("target", str(proof_path.parent.parent))
    passed = bool(proof.get("passed", False))
    final_harness_count = proof.get("final_harness_count", 0)
    evidence.append(
        Evidence(
            "toy_project_proof",
            passed,
            f"{target} passed={passed} final_harness_count={final_harness_count}",
        )
    )


def build_state(
    root: Path,
    vision_file: Path,
    gaps: list[Gap],
    evidence: list[Evidence],
    previous_state: dict[str, Any] | None,
) -> tuple[dict[str, Any], int]:
    selected_gap = asdict(gaps[0]) if gaps else None
    if gaps:
        status = "planning"
        stop_reason = "gap_selected"
        exit_code = 0
        next_actions = [
            f"Address selected gap: {gaps[0].id}",
            "Rerun the self-check harness.",
            "Let the skill choose the next highest-leverage gap.",
        ]
    elif previous_state and previous_state.get("status") == "complete":
        status = "complete"
        stop_reason = "vision_complete"
        exit_code = 0
        next_actions = []
    else:
        status = "blocked"
        stop_reason = "gap_detection_exhausted"
        exit_code = 2
        next_actions = [
            "Mark .vision-loop/state.json status as complete or improve gap detection.",
        ]

    state = {
        "vision_file": str(vision_file.relative_to(root)),
        "phase": "reflect" if evidence else "research",
        "iteration": 0,
        "current_slice": (
            "Read VISION.md, inspect the current plugin, produce a gap list, "
            "choose one gap, patch files, run validation, and update loop state."
        ),
        "gaps": [asdict(gap) for gap in gaps],
        "selected_gap": selected_gap,
        "harnesses": [
            {
                "id": "plugin-self-check",
                "kind": "command",
                "command": "python3 plugins/vision-product-loop/scripts/self_check.py --json",
                "proves": [
                    "VISION.md exists",
                    "plugin manifest loads",
                    "main skill exists",
                    "capability rubric markers are satisfied",
                ],
                "pass_condition": "exit code 0 when a gap is selected or vision is complete; exit code 2 when gap detection is exhausted",
            }
        ],
        "evidence": [asdict(item) for item in evidence],
        "reflection": (
            f"{len(gaps)} gap(s) found; stop_reason={stop_reason}."
            if gaps
            else f"No rubric gaps found; stop_reason={stop_reason}."
        ),
        "status": status,
        "stop_reason": stop_reason,
        "remaining_gaps": [asdict(gap) for gap in gaps],
        "next_actions": next_actions,
    }
    return state, exit_code


def run_self_check(
    root: Path,
    plugin_root: Path,
    state_path: Path,
    run_tests: bool = False,
) -> tuple[dict[str, Any], int]:
    vision_file = root / DEFAULT_VISION_FILE
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    skill_path = plugin_root / "skills" / PLUGIN_NAME / "SKILL.md"
    readme_path = plugin_root / "README.md"
    self_path = plugin_root / "scripts" / "self_check.py"

    gaps: list[Gap] = []
    evidence: list[Evidence] = []

    if vision_file.is_file():
        vision_text = read_text(vision_file)
        evidence.append(Evidence("vision_exists", True, f"Loaded {vision_file}"))
        if "self-check harness" not in vision_text.lower():
            add_gap(
                gaps,
                "vision-self-check-contract-missing",
                "Vision does not describe the self-check harness",
                "VISION.md lacks the self-check harness contract.",
                "Add the self-check harness requirement to VISION.md.",
                vision_file,
            )
    else:
        evidence.append(Evidence("vision_exists", False, f"Missing {vision_file}"))
        add_gap(
            gaps,
            "missing-vision-md",
            "Canonical VISION.md is missing",
            f"{vision_file} does not exist.",
            "Create project-root VISION.md before running the loop.",
            vision_file,
        )

    if self_path.is_file():
        evidence.append(Evidence("self_check_exists", True, f"Loaded {self_path}"))
    else:
        evidence.append(Evidence("self_check_exists", False, f"Missing {self_path}"))
        add_gap(
            gaps,
            "missing-self-check-harness",
            "Self-check harness is missing",
            f"{self_path} does not exist.",
            "Create scripts/self_check.py.",
            self_path,
        )

    inspect_manifest(manifest_path, gaps, evidence)
    inspect_skill(skill_path, gaps, evidence)
    inspect_readme(readme_path, gaps, evidence)
    inspect_tests(plugin_root, gaps, evidence)
    inspect_capability_rubric(root, plugin_root, gaps, evidence)
    inspect_toy_project_proof(root, evidence)
    if run_tests:
        evidence.append(run_validation_tests(root, plugin_root, gaps))

    previous_state = load_json(state_path) if state_path.is_file() else None
    state, exit_code = build_state(root, vision_file, gaps, evidence, previous_state)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return state, exit_code


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Vision Product Loop self-check harness."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root containing VISION.md.",
    )
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
        "--json",
        action="store_true",
        help="Print full state JSON instead of a compact summary.",
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run plugin unittest validation and record validation evidence.",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    plugin_root = (root / args.plugin_root).resolve()
    state_path = (root / args.state).resolve()

    state, exit_code = run_self_check(root, plugin_root, state_path, args.run_tests)

    if args.json:
        print(json.dumps(state, indent=2))
    else:
        print(f"status: {state['status']}")
        print(f"state: {state_path}")
        print(f"gaps: {len(state['gaps'])}")
        if state["selected_gap"]:
            print(f"selected_gap: {state['selected_gap']['id']}")

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
