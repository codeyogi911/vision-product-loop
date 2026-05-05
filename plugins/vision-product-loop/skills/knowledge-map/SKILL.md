---
name: knowledge-map
description: Establish or normalise a repo's system-of-record knowledge layout (CLAUDE.md and AGENTS.md as ≤100-line maps, ARCHITECTURE.md, docs/{adr,design-docs,exec-plans,references,generated}/) by grilling the user on major architecture decisions one at a time and recording each as an ADR. Use when VISION.md is stable and the project is ready to commit architecture decisions before substantial code lands, when a repo has scattered decision records to migrate into a structured docs/ layout, or when a major architecture pivot needs to be recorded.
---

# Knowledge Map

## Purpose

Turn a stable `VISION.md` into the durable knowledge base the loop reads, edits, and grows. Grill the user on every major architecture decision before recording it. ADRs exist only when a real decision was made.

The map files (`CLAUDE.md`, `AGENTS.md`) are tables of contents pointing at deeper sources of truth. They are not encyclopedias; the linter enforces the line budget.

## When To Run

- After `VISION.md` is stable (post `grill-me`) and before the first substantial Build phase.
- When migrating an existing repo's scattered decision records into a structured layout.
- When a major architecture pivot needs to be recorded and propagated.

## Workflow Checklist

1. **Read context** — `VISION.md` (required), `CONTEXT.md`, existing `ARCHITECTURE.md`, `CLAUDE.md`, `AGENTS.md`, `docs/adr/`, scattered records under `docs/`, `notes/`, `wiki/`.
2. **Detect** — `python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root <project> --detect --json`.
3. **List candidate decisions** — surface architecture decisions from the vision must-haves, ordered by leverage.
4. **Grill each decision** — invoke `plugins/vision-product-loop/skills/grill-me/SKILL.md` for each candidate, one at a time.
5. **Record as ADR** — write `docs/adr/NNNN-<slug>.md` in Nygard format, link back to the vision must-have.
6. **Sketch ARCHITECTURE.md** — matklad style, flagged "draft, grown by loop".
7. **Establish maps** — `CLAUDE.md` (primary, ≤100 lines) and `AGENTS.md` (Codex parallel) as table-of-contents only.
8. **Establish docs/ layout** — `python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root <project> --apply` creates the minimum viable layout.
9. **Migrate** — propose source → destination for scattered records; user confirms; move with `git mv`.
10. **Update CONTEXT.md** — add `knowledge-map`, `exec-plan`, `reference-doc`, `design-doc`, `generated-doc`.
11. **Hook the loop** — Build emits ADRs and exec-plans; Reflect moves exec-plans to `completed/`.
12. **Lint** — `python3 plugins/vision-product-loop/scripts/lint_knowledge_map.py --root <project>`.

See [REFERENCE.md](REFERENCE.md) for the full step-by-step detail behind each item, including the minimum viable `docs/` layout, ADR template, and migration heuristics.

## Done Criteria

- All in-scope architecture decisions recorded as ADRs.
- `ARCHITECTURE.md` drafted or updated.
- `CLAUDE.md` and `AGENTS.md` established within the line budget.
- `docs/` layout present.
- Scattered decision docs migrated when applicable.
- `CONTEXT.md` updated with new vocabulary.
- Loop hooks active in `run_loop.py` and the main skill.
- Lint passes.

## Boundaries

Stop and ask the user before:

- Renaming or moving any existing user-authored doc.
- Overwriting an existing `CLAUDE.md`, `AGENTS.md`, or `ARCHITECTURE.md`.
- Recording an ADR the user has not explicitly committed to.
- Scaffolding domain-specific docs the vision does not call for.
