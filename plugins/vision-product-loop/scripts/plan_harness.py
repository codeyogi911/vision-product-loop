#!/usr/bin/env python3
"""Plan the shortest evidence path from project discovery data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def architecture_names(discovery: dict[str, Any]) -> set[str]:
    return {Path(item).name for item in discovery.get("architecture", [])}


def existing_harnesses(discovery: dict[str, Any]) -> list[dict[str, Any]]:
    harnesses = discovery.get("harnesses", [])
    if not isinstance(harnesses, list):
        return []
    return [item for item in harnesses if isinstance(item, dict)]


def recommended_new_harness(discovery: dict[str, Any]) -> dict[str, str]:
    architecture = architecture_names(discovery)
    if "package.json" in architecture:
        return {
            "kind": "new-package-script",
            "name": "test:vision",
            "command": "npm run test:vision",
            "purpose": "Create the smallest Node-based smoke or acceptance harness for the current vision slice.",
        }
    if "pyproject.toml" in architecture:
        return {
            "kind": "new-python-test",
            "name": "test_vision_slice.py",
            "command": "python3 -m pytest",
            "purpose": "Create the smallest Python test for the current vision slice.",
        }
    return {
        "kind": "new-scripted-check",
        "name": "vision_smoke_check",
        "command": "python3 scripts/vision_smoke_check.py",
        "purpose": "Create a tiny project-local script that proves or falsifies the current vision slice.",
    }


def plan_harness(discovery: dict[str, Any]) -> dict[str, Any]:
    """Return a harness plan optimized for the shortest evidence path."""
    harnesses = existing_harnesses(discovery)
    if harnesses:
        return {
            "strategy": "reuse-existing-harness",
            "reason": "Existing harnesses are the shortest evidence path.",
            "harnesses": harnesses,
            "recommended": harnesses[0],
            "next_action": "Run the selected existing harness against the current vision slice.",
        }

    recommendation = recommended_new_harness(discovery)
    return {
        "strategy": "create-minimal-harness",
        "reason": "No existing harnesses were discovered, so the shortest evidence path is to create the smallest proof tool for the current slice.",
        "harnesses": [],
        "recommended": recommendation,
        "next_action": "Create the recommended harness, then run it before claiming progress.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plan the shortest evidence path from discovery JSON."
    )
    parser.add_argument(
        "--discovery",
        required=True,
        help="Path to JSON output from discover_project.py.",
    )
    args = parser.parse_args()

    discovery = load_json(Path(args.discovery))
    print(json.dumps(plan_harness(discovery), indent=2))


if __name__ == "__main__":
    main()
