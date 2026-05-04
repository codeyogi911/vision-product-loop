#!/usr/bin/env python3
"""Discover a project's control plane for the Vision Product Loop."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DOC_NAMES = (
    "VISION.md",
    "README.md",
    "CONTEXT.md",
    "AGENTS.md",
    "CLAUDE.md",
)

DOC_DIRS = (
    "docs",
    "specs",
    "adr",
    "docs/adr",
)

AGENT_PATH_PARTS = (
    ".agents",
    ".codex",
    "agents",
    "skills",
)

AGENT_FILE_NAMES = (
    "AGENTS.md",
    "CLAUDE.md",
)

ARCHITECTURE_FILES = (
    "package.json",
    "pnpm-workspace.yaml",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "Gemfile",
    "Makefile",
    "docker-compose.yml",
    "compose.yml",
)

HARNESS_NAMES = (
    "test",
    "tests",
    "spec",
    "e2e",
    "playwright",
    "cypress",
    "vitest",
    "jest",
    "pytest",
    "lint",
    "bench",
    "eval",
    "evaluate",
    "check",
)


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def safe_load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def walk_files(root: Path, max_files: int) -> list[Path]:
    ignored = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}
    files: list[Path] = []
    for path in root.rglob("*"):
        if len(files) >= max_files:
            break
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return files


def discover_docs(root: Path, files: list[Path]) -> list[str]:
    docs: set[str] = set()
    for name in DOC_NAMES:
        path = root / name
        if path.is_file():
            docs.add(rel(path, root))
    for path in files:
        relative = rel(path, root)
        if any(relative == directory or relative.startswith(f"{directory}/") for directory in DOC_DIRS):
            if path.suffix.lower() in {".md", ".mdx", ".txt"}:
                docs.add(relative)
    return sorted(docs)


def discover_agents(root: Path, files: list[Path]) -> list[str]:
    agents: set[str] = set()
    for path in files:
        relative = rel(path, root)
        parts = set(path.relative_to(root).parts)
        if path.name in AGENT_FILE_NAMES or parts.intersection(AGENT_PATH_PARTS):
            if path.suffix.lower() in {".md", ".json", ".toml", ".yaml", ".yml"}:
                agents.add(relative)
    return sorted(agents)


def discover_architecture(root: Path) -> list[str]:
    architecture: list[str] = []
    for name in ARCHITECTURE_FILES:
        path = root / name
        if path.is_file():
            architecture.append(rel(path, root))
    return architecture


def script_looks_like_harness(name: str) -> bool:
    lowered = name.lower()
    return any(token in lowered for token in HARNESS_NAMES)


def discover_package_harnesses(root: Path) -> list[dict[str, str]]:
    package_json = root / "package.json"
    package = safe_load_json(package_json)
    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict):
        return []
    harnesses: list[dict[str, str]] = []
    for name, command in sorted(scripts.items()):
        if script_looks_like_harness(name):
            harnesses.append(
                {
                    "kind": "package-script",
                    "name": name,
                    "command": f"npm run {name}",
                    "detail": str(command),
                }
            )
    return harnesses


def discover_file_harnesses(root: Path, files: list[Path]) -> list[dict[str, str]]:
    harnesses: list[dict[str, str]] = []
    for path in files:
        relative = rel(path, root)
        lowered = relative.lower()
        if path.suffix.lower() not in {".py", ".js", ".ts", ".sh", ".md", ".json"}:
            continue
        if any(token in lowered for token in HARNESS_NAMES):
            harnesses.append(
                {
                    "kind": "file",
                    "name": path.name,
                    "path": relative,
                }
            )
    return harnesses


def discover_project(root: Path, max_files: int = 2000) -> dict[str, Any]:
    root = root.resolve()
    files = walk_files(root, max_files)
    return {
        "root": str(root),
        "docs": discover_docs(root, files),
        "agents": discover_agents(root, files),
        "architecture": discover_architecture(root),
        "harnesses": discover_package_harnesses(root) + discover_file_harnesses(root, files),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover docs, agents, architecture signals, and harnesses for a project."
    )
    parser.add_argument("--root", default=".", help="Project root to inspect.")
    parser.add_argument(
        "--max-files",
        type=int,
        default=2000,
        help="Maximum files to inspect while discovering project signals.",
    )
    args = parser.parse_args()

    result = discover_project(Path(args.root), args.max_files)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
