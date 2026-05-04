#!/usr/bin/env python3
"""Create a first-pass product iteration checklist from a markdown vision file."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


VISION_CANDIDATES = (
    "VISION.md",
    "docs/VISION.md",
    "docs/product/VISION.md",
)

RECOMMENDED_SECTIONS = (
    "Product Promise",
    "Users",
    "Jobs To Be Done",
    "Must-Have Capabilities",
    "Experience Qualities",
    "Non-Goals",
    "Acceptance Checks",
    "Open Questions",
)

SIGNAL_WORDS = (
    "must",
    "should",
    "need",
    "needs",
    "user can",
    "users can",
    "allow",
    "support",
    "prevent",
    "acceptance",
    "done",
    "test",
    "harness",
    "ship",
    "reliable",
    "fast",
)

GLOBAL_REQUIREMENT_SIGNALS = (
    "must",
    "should",
    "need",
    "needs",
    "user can",
    "users can",
    "allow",
    "support",
    "prevent",
)

ACCEPTANCE_SECTION_HINTS = (
    "acceptance",
    "capabilities",
    "checks",
    "criteria",
    "must-have",
    "must have",
    "requirements",
    "success",
)


@dataclass
class Checklist:
    vision_file: str
    headings: list[str]
    missing_sections: list[str]
    acceptance_candidates: list[str]
    loop_checklist: list[str]


def find_vision_file(root: Path) -> Path | None:
    for candidate in VISION_CANDIDATES:
        path = root / candidate
        if path.is_file():
            return path
    return None


def normalize_heading(heading: str) -> str:
    return re.sub(r"\s+", " ", heading.strip().strip("#").strip())


def extract_headings(lines: Iterable[str]) -> list[str]:
    headings: list[str] = []
    for line in lines:
        if line.startswith("#"):
            headings.append(normalize_heading(line))
    return headings


def clean_bullet(line: str) -> str:
    return re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line).strip()


def has_signal_word(line: str, signals: Iterable[str]) -> bool:
    for signal in signals:
        if " " in signal:
            if signal in line:
                return True
            continue
        if re.search(rf"\b{re.escape(signal)}\b", line):
            return True
    return False


def extract_acceptance_candidates(lines: Iterable[str], limit: int) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()
    current_heading = ""
    for raw_line in lines:
        if raw_line.startswith("#"):
            current_heading = normalize_heading(raw_line).lower()
            continue
        line = clean_bullet(raw_line)
        if not line or len(line) < 12:
            continue
        lowered = line.lower()
        is_bullet = raw_line.lstrip().startswith(("-", "*", "+")) or re.match(
            r"^\s*\d+[.)]\s+", raw_line
        )
        has_signal = has_signal_word(lowered, SIGNAL_WORDS)
        has_global_requirement_signal = has_signal_word(
            lowered, GLOBAL_REQUIREMENT_SIGNALS
        )
        is_acceptance_section = any(
            hint in current_heading for hint in ACCEPTANCE_SECTION_HINTS
        )
        if is_acceptance_section:
            if not has_signal and not is_bullet:
                continue
        elif not has_global_requirement_signal:
            continue
        if line in seen:
            continue
        seen.add(line)
        candidates.append(line)
        if len(candidates) >= limit:
            break
    return candidates


def missing_sections(headings: list[str]) -> list[str]:
    normalized = {heading.lower().replace("-", " ") for heading in headings}
    missing: list[str] = []
    for section in RECOMMENDED_SECTIONS:
        section_key = section.lower().replace("-", " ")
        if not any(section_key in heading for heading in normalized):
            missing.append(section)
    return missing


def build_loop_checklist(candidates: list[str]) -> list[str]:
    checklist = [
        "Confirm the product promise and non-goals with the user.",
        "Map each must-have capability to a repo-local code area.",
        "Identify the harness that proves each acceptance check.",
    ]
    for candidate in candidates:
        checklist.append(f"Prove or implement: {candidate}")
    checklist.extend(
        [
            "Run the strongest available validation harness.",
            "Compare observed behavior against the vision contract.",
            "Record remaining gaps and choose the next highest-leverage loop.",
        ]
    )
    return checklist


def build_checklist(root: Path, vision_file: Path | None, limit: int) -> Checklist:
    if vision_file is None:
        discovered = find_vision_file(root)
        if discovered is None:
            raise FileNotFoundError(
                "No vision file found. Pass --vision or create VISION.md."
            )
        vision_file = discovered

    text = vision_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings = extract_headings(lines)
    candidates = extract_acceptance_candidates(lines, limit)
    return Checklist(
        vision_file=str(vision_file),
        headings=headings,
        missing_sections=missing_sections(headings),
        acceptance_candidates=candidates,
        loop_checklist=build_loop_checklist(candidates),
    )


def print_markdown(checklist: Checklist) -> None:
    print(f"# Vision Iteration Checklist\n")
    print(f"Vision file: `{checklist.vision_file}`\n")

    print("## Headings Found\n")
    if checklist.headings:
        for heading in checklist.headings:
            print(f"- {heading}")
    else:
        print("- No markdown headings found.")

    print("\n## Missing Recommended Sections\n")
    if checklist.missing_sections:
        for section in checklist.missing_sections:
            print(f"- {section}")
    else:
        print("- None.")

    print("\n## Acceptance Candidates\n")
    if checklist.acceptance_candidates:
        for item in checklist.acceptance_candidates:
            print(f"- [ ] {item}")
    else:
        print("- No explicit candidates found yet.")

    print("\n## Loop Checklist\n")
    for item in checklist.loop_checklist:
        print(f"- [ ] {item}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a first-pass implementation checklist from a vision doc."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root used to discover VISION.md when --vision is omitted.",
    )
    parser.add_argument(
        "--vision",
        help="Path to a specific markdown vision file.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum acceptance candidates to extract.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of markdown.",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    vision_file = Path(args.vision).expanduser().resolve() if args.vision else None
    checklist = build_checklist(root, vision_file, args.limit)

    if args.json:
        print(json.dumps(asdict(checklist), indent=2))
    else:
        print_markdown(checklist)


if __name__ == "__main__":
    main()
