#!/usr/bin/env python3
"""Scaffold or detect a Vision Product Loop knowledge-map layout.

Detect mode reports the current state of the knowledge map without writing
anything. Apply mode creates the minimum viable layout idempotently and never
overwrites existing user-authored files.

The knowledge map is the system of record for a project. The map files
(CLAUDE.md, AGENTS.md) are tables of contents under a strict line budget;
deeper sources of truth live under docs/. This script handles the deterministic
file mechanics. Product judgment (what decisions to record, how to grill the
user, what to migrate) belongs to the knowledge-map skill.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_LINE_BUDGET = 100


TARGET_FILES = (
    "VISION.md",
    "CONTEXT.md",
    "ARCHITECTURE.md",
    "CLAUDE.md",
    "AGENTS.md",
)


TARGET_DIRS = (
    "docs/adr",
    "docs/design-docs",
    "docs/exec-plans/active",
    "docs/exec-plans/completed",
    "docs/references",
    "docs/generated",
)


SCATTERED_DECISION_HINTS = (
    "decision",
    "adr",
    "rfc",
    "design-decision",
)


SCATTERED_SEARCH_DIRS = ("docs", "notes", "wiki")


ADR_TEMPLATE = """# NNNN. Title

## Status

Proposed | Accepted | Deprecated | Superseded by ADR-XXXX

## Context

What is the issue we're seeing that motivates this decision? Reference the
VISION.md must-have or constraint that this decision serves.

## Decision

What is the decision and why this option over the alternatives that were
considered?

## Consequences

What becomes easier, what becomes harder, and what new decisions are now
required as a result?
"""


ADR_0001 = """# 1. Record architecture decisions

## Status

Accepted

## Context

We need to record the architectural decisions made on this project so future
contributors and agents can understand why the system is the way it is.

## Decision

We will use Architecture Decision Records, as described by Michael Nygard, in
`docs/adr/`. Each decision lives in its own file `NNNN-<slug>.md` and follows
the template in `docs/adr/template.md`.

## Consequences

The Vision Product Loop will emit an ADR every time a non-trivial architecture
decision is made during a Build phase. The map files (`CLAUDE.md`,
`AGENTS.md`) point at `docs/adr/` so agents and humans can find decisions
without scanning the codebase.
"""


ADR_INDEX = """# Architecture Decisions

This index lists every ADR in this project, newest first. Each ADR captures a
decision the team committed to, in Michael Nygard's format (status, context,
decision, consequences).

- [0001 — Record architecture decisions](0001-record-architecture-decisions.md)
"""


DESIGN_DOCS_INDEX = """# Design Docs

Design docs live here. Each file captures a longer-form design discussion that
is too rich for an ADR but still needs to be durable for future contributors.

ADRs (`../adr/`) record decisions; design docs record the exploration that
preceded a decision or a Module-level investigation that does not yet have a
single decision to record.
"""


def architecture_skeleton() -> str:
    return """# Architecture

> Status: draft, grown by the loop. This file is a sketch until the first
> Build phase materialises code; the operating loop will refine it as Modules
> form.

## Bird's-eye view

A short paragraph describing what this product does at the highest level and
the shape of the code that will deliver it.

## Code map

A high-level walk of the top-level directories and what each one is for. Add
entries here as Modules emerge; do not predict directories before they exist.

## Boundaries

Where the strong seams sit and what crosses them.

## Cross-cutting concerns

Logging, error handling, configuration, secrets, tracing — anything that
touches many Modules.

## Naming

Conventions worth committing to so future contributors and agents read the
codebase the same way.
"""


def map_skeleton(target_filename: str) -> str:
    return f"""# {target_filename}

> Map only. Hard line budget: {DEFAULT_LINE_BUDGET} lines. Add pointers, not
> content. Deeper sources of truth live under `docs/`.

## Purpose

Briefly state what this project is. One or two sentences.

## Sources of truth

- `VISION.md` — product contract.
- `CONTEXT.md` — domain vocabulary.
- `ARCHITECTURE.md` — bird's-eye-view code map.
- `docs/adr/` — architecture decision records.
- `docs/design-docs/` — longer-form design exploration.
- `docs/exec-plans/active/` — in-flight execution plans.
- `docs/exec-plans/completed/` — closed execution plans (durable history).
- `docs/references/` — third-party reference docs in agent-friendly form.
- `docs/generated/` — generated docs (db schema, API surface, etc.).

## Run entry points

Add the project's main entry points here as they land.

## Operating loop

`plugins/vision-product-loop/` provides the Vision Product Loop plugin. Use
its `vision-product-loop` skill to drive Research → Build → Verify → Test →
Reflect cycles.
"""


@dataclass
class FileStatus:
    path: str
    exists: bool
    line_count: int | None = None


@dataclass
class ScatteredHit:
    path: str
    reason: str


@dataclass
class DetectReport:
    root: str
    files: list[FileStatus] = field(default_factory=list)
    dirs: list[FileStatus] = field(default_factory=list)
    scattered_decisions: list[ScatteredHit] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class ApplyReport:
    root: str
    created_dirs: list[str] = field(default_factory=list)
    created_files: list[str] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def line_count(path: Path) -> int | None:
    if not path.is_file():
        return None
    return sum(1 for _ in path.read_text(encoding="utf-8").splitlines())


def detect(root: Path) -> DetectReport:
    report = DetectReport(root=str(root))

    for filename in TARGET_FILES:
        path = root / filename
        report.files.append(
            FileStatus(
                path=filename,
                exists=path.is_file(),
                line_count=line_count(path),
            )
        )

    for dirname in TARGET_DIRS:
        path = root / dirname
        report.dirs.append(FileStatus(path=dirname, exists=path.is_dir()))

    report.scattered_decisions = list(scan_scattered(root))

    if not (root / "VISION.md").is_file():
        report.notes.append(
            "VISION.md is missing. Run vision-product-loop before knowledge-map."
        )
    if not (root / "docs" / "adr").is_dir() and report.scattered_decisions:
        report.notes.append(
            "Decision-like artefacts found outside docs/adr/. Propose migration."
        )
    return report


def scan_scattered(root: Path) -> list[ScatteredHit]:
    hits: list[ScatteredHit] = []
    pattern = re.compile(
        r"(?:^|[\\/_-])(" + "|".join(re.escape(h) for h in SCATTERED_DECISION_HINTS) + r")",
        re.IGNORECASE,
    )
    canonical_adr_dir = (root / "docs" / "adr").resolve()
    for sub in SCATTERED_SEARCH_DIRS:
        base = root / sub
        if not base.is_dir():
            continue
        for path in base.rglob("*.md"):
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if canonical_adr_dir in resolved.parents or resolved == canonical_adr_dir:
                continue
            stem = path.stem
            if pattern.search(stem):
                hits.append(
                    ScatteredHit(
                        path=str(path.relative_to(root)),
                        reason=f"filename matches decision hint ({stem})",
                    )
                )
    return hits


def apply(root: Path) -> ApplyReport:
    report = ApplyReport(root=str(root))

    for dirname in TARGET_DIRS:
        path = root / dirname
        if path.is_dir():
            continue
        path.mkdir(parents=True, exist_ok=True)
        report.created_dirs.append(dirname)

    write_if_missing(
        root / "docs" / "adr" / "template.md",
        ADR_TEMPLATE,
        report,
    )
    write_if_missing(
        root / "docs" / "adr" / "0001-record-architecture-decisions.md",
        ADR_0001,
        report,
    )
    write_if_missing(
        root / "docs" / "adr" / "index.md",
        ADR_INDEX,
        report,
    )
    write_if_missing(
        root / "docs" / "design-docs" / "index.md",
        DESIGN_DOCS_INDEX,
        report,
    )

    for keep_dir in ("references", "generated"):
        keep = root / "docs" / keep_dir / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")
            report.created_files.append(str(keep.relative_to(root)))

    write_if_missing(
        root / "ARCHITECTURE.md",
        architecture_skeleton(),
        report,
    )
    write_if_missing(
        root / "CLAUDE.md",
        map_skeleton("CLAUDE.md"),
        report,
    )
    write_if_missing(
        root / "AGENTS.md",
        map_skeleton("AGENTS.md"),
        report,
    )

    return report


def write_if_missing(path: Path, content: str, report: ApplyReport) -> None:
    rel = str(path.relative_to(Path(report.root)))
    if path.exists():
        report.skipped_files.append(rel)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    report.created_files.append(rel)


def detect_payload(report: DetectReport) -> dict[str, Any]:
    return {
        "mode": "detect",
        "root": report.root,
        "files": [asdict(f) for f in report.files],
        "dirs": [asdict(d) for d in report.dirs],
        "scattered_decisions": [asdict(s) for s in report.scattered_decisions],
        "notes": report.notes,
    }


def apply_payload(report: ApplyReport) -> dict[str, Any]:
    return {
        "mode": "apply",
        "root": report.root,
        "created_dirs": report.created_dirs,
        "created_files": report.created_files,
        "skipped_files": report.skipped_files,
        "notes": report.notes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect or scaffold a Vision Product Loop knowledge-map layout.",
    )
    parser.add_argument("--root", default=".", help="Project root.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--detect", action="store_true", help="Report current state only.")
    mode.add_argument("--apply", action="store_true", help="Create the minimum viable layout.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a summary.")
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"root does not exist or is not a directory: {root}")

    if args.detect:
        report = detect(root)
        payload = detect_payload(report)
    else:
        report = apply(root)
        payload = apply_payload(report)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
