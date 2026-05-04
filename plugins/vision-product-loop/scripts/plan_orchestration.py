#!/usr/bin/env python3
"""Plan local work and optional delegation for a vision loop slice."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def task_is_blocking(task: dict[str, Any]) -> bool:
    return bool(task.get("blocking", False))


def task_crosses_boundary(task: dict[str, Any]) -> bool:
    markers = {
        "network",
        "publish",
        "marketplace",
        "delete",
        "destructive",
        "product-promise",
    }
    task_text = " ".join(
        str(value).lower() for value in (task.get("id"), task.get("title"), task.get("kind"))
    )
    return any(marker in task_text for marker in markers)


def plan_orchestration(
    tasks: list[dict[str, Any]],
    allow_delegation: bool = False,
) -> dict[str, Any]:
    """Return an orchestration plan under the autonomy_boundary."""
    local: list[dict[str, Any]] = []
    delegate: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []

    for task in tasks:
        decision = dict(task)
        if task_crosses_boundary(task):
            decision["reason"] = "crosses autonomy_boundary"
            blocked.append(decision)
        elif task_is_blocking(task):
            decision["reason"] = "blocking work stays local"
            local.append(decision)
        elif allow_delegation and task.get("independent", False):
            decision["reason"] = "independent sidecar work can delegate"
            delegate.append(decision)
        else:
            decision["reason"] = "default to local execution"
            local.append(decision)

    return {
        "autonomy_boundary": "stop before destructive, network, marketplace, publishing, deletion, or product-promise changes",
        "local": local,
        "delegate": delegate,
        "blocked": blocked,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plan local and optional delegated work for vision-loop tasks."
    )
    parser.add_argument("--tasks", required=True, help="JSON file containing a tasks array.")
    parser.add_argument(
        "--allow-delegation",
        action="store_true",
        help="Allow independent sidecar tasks to be marked for delegation.",
    )
    args = parser.parse_args()

    payload = load_json(Path(args.tasks))
    tasks = payload.get("tasks", payload if isinstance(payload, list) else [])
    print(json.dumps(plan_orchestration(tasks, args.allow_delegation), indent=2))


if __name__ == "__main__":
    main()
