#!/usr/bin/env python3
"""Lint a Vision Product Loop knowledge-map layout.

Checks the deterministic shape of the knowledge map: map-file line budgets,
cross-link resolution from map files, ADR section completeness, and exec-plan
placement against `.vision-loop/state.json`.

Returns exit code 0 on pass, 1 on lint failure, 2 on usage error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_LINE_BUDGET = 100
DEFAULT_STATE_PATH = ".vision-loop/state.json"


CANONICAL_MAP = "AGENTS.md"
SYMLINKED_MAP = "CLAUDE.md"
MAP_FILES = (CANONICAL_MAP, SYMLINKED_MAP)


REQUIRED_ADR_SECTIONS = ("Status", "Context", "Decision", "Consequences")


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


@dataclass
class LintIssue:
    severity: str  # "error" or "warning"
    rule: str
    path: str
    detail: str


@dataclass
class LintReport:
    root: str
    line_budget: int
    issues: list[LintIssue] = field(default_factory=list)
    checked_files: list[str] = field(default_factory=list)
    passed: bool = True


def line_count(path: Path) -> int:
    return sum(1 for _ in path.read_text(encoding="utf-8").splitlines())


def lint_map_budget(root: Path, report: LintReport) -> None:
    for filename in MAP_FILES:
        path = root / filename
        if not path.is_file() and not path.is_symlink():
            report.issues.append(
                LintIssue(
                    severity="warning",
                    rule="map-missing",
                    path=filename,
                    detail=f"{filename} is missing; run knowledge-map scaffold.",
                )
            )
            continue
        report.checked_files.append(filename)
        if not path.is_file():
            # Broken symlink.
            report.issues.append(
                LintIssue(
                    severity="error",
                    rule="map-broken-symlink",
                    path=filename,
                    detail=f"{filename} is a broken symlink.",
                )
            )
            continue
        n = line_count(path)
        if n > report.line_budget:
            report.issues.append(
                LintIssue(
                    severity="error",
                    rule="map-line-budget",
                    path=filename,
                    detail=(
                        f"{filename} has {n} lines; budget is {report.line_budget}. "
                        "Maps are tables of contents, not encyclopedias."
                    ),
                )
            )


def lint_map_symlink(root: Path, report: LintReport) -> None:
    """CLAUDE.md should be a symlink to AGENTS.md so both share one source.

    If both files exist as separate regular files with diverging content the
    linter emits a warning so users can decide whether to recover the symlink
    convention or keep them split intentionally.
    """
    canonical = root / CANONICAL_MAP
    pointer = root / SYMLINKED_MAP
    if not canonical.is_file():
        return
    if pointer.is_symlink():
        target = os.readlink(pointer)
        # Accept either the bare filename or an absolute/relative path that
        # resolves back to the canonical map.
        resolved = (pointer.parent / target).resolve()
        if resolved != canonical.resolve():
            report.issues.append(
                LintIssue(
                    severity="warning",
                    rule="map-symlink-target",
                    path=SYMLINKED_MAP,
                    detail=(
                        f"{SYMLINKED_MAP} symlinks to {target!r}; expected "
                        f"{CANONICAL_MAP}."
                    ),
                )
            )
        return
    if not pointer.is_file():
        return
    if pointer.read_text(encoding="utf-8") != canonical.read_text(encoding="utf-8"):
        report.issues.append(
            LintIssue(
                severity="warning",
                rule="map-divergence",
                path=SYMLINKED_MAP,
                detail=(
                    f"{SYMLINKED_MAP} and {CANONICAL_MAP} are both regular "
                    "files with different content. Make CLAUDE.md a symlink to "
                    "AGENTS.md (or a one-line pointer) to keep one source of "
                    "truth across agents."
                ),
            )
        )


def lint_map_links(root: Path, report: LintReport) -> None:
    for filename in MAP_FILES:
        path = root / filename
        if not path.is_file():
            continue
        # Skip the symlinked pointer to avoid duplicate reports against the
        # same content already checked via the canonical map.
        if filename == SYMLINKED_MAP and path.is_symlink():
            continue
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(2).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_clean = target.split("#", 1)[0]
            if not target_clean:
                continue
            target_path = (root / target_clean).resolve()
            try:
                target_path.relative_to(root.resolve())
            except ValueError:
                report.issues.append(
                    LintIssue(
                        severity="error",
                        rule="map-link-escape",
                        path=filename,
                        detail=f"Link {target!r} points outside the project root.",
                    )
                )
                continue
            if not target_path.exists():
                report.issues.append(
                    LintIssue(
                        severity="error",
                        rule="map-link-broken",
                        path=filename,
                        detail=f"Link {target!r} does not resolve.",
                    )
                )


def lint_adrs(root: Path, report: LintReport) -> None:
    adr_dir = root / "docs" / "adr"
    if not adr_dir.is_dir():
        report.issues.append(
            LintIssue(
                severity="warning",
                rule="adr-dir-missing",
                path="docs/adr",
                detail="docs/adr/ is missing; run knowledge-map scaffold.",
            )
        )
        return
    for path in sorted(adr_dir.glob("*.md")):
        name = path.name
        if name in {"index.md", "template.md"}:
            continue
        report.checked_files.append(str(path.relative_to(root)))
        text = path.read_text(encoding="utf-8")
        missing = [
            section
            for section in REQUIRED_ADR_SECTIONS
            if not re.search(rf"^##\s+{re.escape(section)}\b", text, re.MULTILINE)
        ]
        if missing:
            report.issues.append(
                LintIssue(
                    severity="error",
                    rule="adr-missing-section",
                    path=str(path.relative_to(root)),
                    detail=(
                        f"ADR is missing required Nygard section(s): {', '.join(missing)}."
                    ),
                )
            )


def lint_exec_plans(root: Path, state_path: Path, report: LintReport) -> None:
    active_dir = root / "docs" / "exec-plans" / "active"
    completed_dir = root / "docs" / "exec-plans" / "completed"
    if not active_dir.is_dir() or not completed_dir.is_dir():
        return
    if not state_path.is_file():
        return
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.issues.append(
            LintIssue(
                severity="warning",
                rule="state-unreadable",
                path=str(state_path.relative_to(root)) if state_path.is_relative_to(root) else str(state_path),
                detail=f"Could not parse loop state: {exc}",
            )
        )
        return
    closed_slugs = {
        slug
        for slug in (state.get("closed_exec_plans") or [])
        if isinstance(slug, str)
    }
    for path in active_dir.glob("*.md"):
        if path.stem in closed_slugs:
            report.issues.append(
                LintIssue(
                    severity="error",
                    rule="exec-plan-stale",
                    path=str(path.relative_to(root)),
                    detail=(
                        "Exec plan is in active/ but state.json marks it closed. "
                        "Move it to docs/exec-plans/completed/."
                    ),
                )
            )


def run_lint(
    root: Path,
    state_path: Path,
    line_budget: int = DEFAULT_LINE_BUDGET,
) -> LintReport:
    report = LintReport(root=str(root), line_budget=line_budget)
    lint_map_budget(root, report)
    lint_map_symlink(root, report)
    lint_map_links(root, report)
    lint_adrs(root, report)
    lint_exec_plans(root, state_path, report)
    report.passed = not any(issue.severity == "error" for issue in report.issues)
    return report


def report_payload(report: LintReport) -> dict[str, Any]:
    return {
        "root": report.root,
        "line_budget": report.line_budget,
        "passed": report.passed,
        "checked_files": report.checked_files,
        "issues": [asdict(i) for i in report.issues],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lint a Vision Product Loop knowledge-map layout.",
    )
    parser.add_argument("--root", default=".", help="Project root.")
    parser.add_argument(
        "--state",
        default=DEFAULT_STATE_PATH,
        help="Loop state JSON file relative to root.",
    )
    parser.add_argument(
        "--line-budget",
        type=int,
        default=DEFAULT_LINE_BUDGET,
        help="Line budget for map files (CLAUDE.md, AGENTS.md).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"root does not exist or is not a directory: {root}")
    state_path = (root / args.state).resolve()

    report = run_lint(root, state_path, line_budget=args.line_budget)
    payload = report_payload(report)
    print(json.dumps(payload, indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
