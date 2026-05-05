#!/usr/bin/env python3
"""Run the generated toy-project regression proof for Vision Product Loop."""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any

import create_harness
import discover_project
import plan_harness


TOY_VISION = """# Product Promise

This toy project checks that the Vision Product Loop can start from a vision, discover that no harness exists, create the smallest missing proof harness, run it, and record evidence.

It is bootstrap evidence only. It does not prove the loop shipped a useful change in a real target project.

## Primary Users

- Builders validating the Vision Product Loop plugin.

## Acceptance Checks

- The target project has a `VISION.md`.
- The loop discovers no initial harness.
- The loop creates a smoke-check harness.
- The created harness runs successfully.
"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def prepare_target(target: Path, force: bool) -> None:
    if target.exists() and any(target.iterdir()):
        if not force:
            raise FileExistsError(f"{target} is not empty. Pass --force to recreate it.")
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    (target / "VISION.md").write_text(TOY_VISION, encoding="utf-8")


def run_command(root: Path, command: str) -> dict[str, Any]:
    result = subprocess.run(
        shlex.split(command),
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "passed": result.returncode == 0,
    }


def run_toy_proof(target: Path, force: bool = False) -> dict[str, Any]:
    target = target.resolve()
    prepare_target(target, force)

    initial_discovery = discover_project.discover_project(target)
    harness_plan = plan_harness.plan_harness(initial_discovery)
    creation = create_harness.create_harness(target, harness_plan, apply=True)
    command_result = run_command(target, creation["command"])
    final_discovery = discover_project.discover_project(target)

    proof = {
        "target": str(target),
        "vision_file": "VISION.md",
        "initial_harness_count": len(initial_discovery["harnesses"]),
        "plan": harness_plan,
        "creation": creation,
        "command_result": command_result,
        "final_harness_count": len(final_discovery["harnesses"]),
        "passed": (
            initial_discovery["harnesses"] == []
            and creation["strategy"] == "create-minimal-harness"
            and command_result["passed"]
            and len(final_discovery["harnesses"]) > 0
        ),
    }
    write_json(target / ".vision-loop" / "toy-proof.json", proof)
    return proof


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a toy project and prove the loop can create and run a harness."
    )
    parser.add_argument(
        "--target",
        default=".vision-loop/toy-project",
        help="Target directory for the generated toy project.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recreate the target directory if it already contains files.",
    )
    args = parser.parse_args()

    proof = run_toy_proof(Path(args.target), force=args.force)
    print(json.dumps(proof, indent=2))
    raise SystemExit(0 if proof["passed"] else 1)


if __name__ == "__main__":
    main()
