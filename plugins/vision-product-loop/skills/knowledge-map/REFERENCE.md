# Knowledge Map — Reference

Detailed step-by-step workflow for the [knowledge-map skill](SKILL.md). The SKILL.md file holds the checklist; this file holds the operating detail.

## 1. Read context

Required: `VISION.md`. If missing, stop and ask the user to run `vision-product-loop` first; the knowledge map is downstream of a stable vision.

Also read: `CONTEXT.md`, existing `ARCHITECTURE.md`, `CLAUDE.md`, `AGENTS.md`, `docs/adr/`, and any scattered decision docs under `docs/`, `notes/`, `wiki/`, README sections, design-doc folders.

## 2. Detect

```bash
python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root <project> --detect --json
```

The helper reports existing target files, ADR-like artefacts found outside `docs/adr/`, and proposed migration paths. Do not write anything yet. Use the output to plan the grill.

## 3. List candidate decisions

From `VISION.md` must-haves and discovered code, surface the architecture decisions that should be committed before code lands. Common candidates:

- Persistence model and data layout
- Agent runtime, sub-agent split, harness orchestration
- Deployment target and release process
- Language and runtime choice
- Public API surface and versioning
- Module seams and boundaries
- Cross-cutting concerns (logging, error handling, secrets, tracing)

Order by leverage. Decisions that block many others first.

## 4. Grill each decision

For each candidate, invoke the bundled `grill-me` skill (`plugins/vision-product-loop/skills/grill-me/SKILL.md`):

- Frame the decision and its real alternatives.
- Recommend an answer with reasoning.
- Explore the codebase before asking when discoverable.
- Resolve one branch fully before moving to the next.
- Stop when the user is committed enough to record the decision as an ADR.

Do not record an ADR until the user has explicitly committed to the decision in conversation. Half-formed opinions belong in `docs/design-docs/` instead, not `docs/adr/`.

## 5. Record as ADR

For each resolved decision write `docs/adr/NNNN-<slug>.md` using Michael Nygard's format:

```markdown
# NNNN. Title

## Status

Accepted

## Context

Why are we deciding this now? Reference the VISION.md must-have or constraint
this decision serves.

## Decision

What we will do, and why this option over the alternatives that were
considered.

## Consequences

What becomes easier, what becomes harder, and what new decisions are now
required as a result.
```

Update `docs/adr/index.md` with a link to the new ADR.

## 6. Sketch ARCHITECTURE.md

After in-scope decisions are recorded, draft `ARCHITECTURE.md` in matklad style: bird's-eye view, code map, boundaries, naming, cross-cutting concerns. Flag "draft, grown by loop" until the first Build phase materialises code. The sketch should reflect what the ADRs imply, not predict directories that do not yet exist.

## 7. Establish maps

`AGENTS.md` is canonical. `CLAUDE.md` is a symlink to it.

Generate `AGENTS.md` (≤100 lines) as the table of contents only:

- Short purpose statement (1–2 sentences).
- Pointers to `VISION.md`, `ARCHITECTURE.md`, `docs/` tree, run entry points.
- Short note on the operating loop pointer.

Then create `CLAUDE.md` as a symlink to `AGENTS.md` (`ln -s AGENTS.md CLAUDE.md`). The scaffold script does this automatically; on filesystems without symlink support it falls back to a one-line `CLAUDE.md` that points at `AGENTS.md`. Reject encyclopedia drift; the linter enforces the line budget against the canonical file.

The split-file historical convention (CLAUDE.md and AGENTS.md as parallel files) is deprecated — it produced drift between Claude Code and Codex when one map was edited and the other was not.

## 8. Establish docs/ layout

```bash
python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root <project> --apply
```

Creates the minimum viable layout idempotently and never overwrites user-authored files:

```text
docs/
├── adr/
│   ├── template.md
│   ├── 0001-record-architecture-decisions.md
│   └── index.md
├── design-docs/
│   └── index.md
├── exec-plans/
│   ├── active/
│   └── completed/
├── references/
│   └── .gitkeep
└── generated/
    └── .gitkeep
```

Do not scaffold domain-specific files (`FRONTEND.md`, `SECURITY.md`, `RELIABILITY.md`, `DESIGN.md`, etc.). The loop materialises those when the vision calls for them; pre-creating them produces empty drawers.

## 9. Migrate

If detect mode found scattered records, propose a migration plan: source path → destination path, ordered by confidence. Ask the user for confirmation before any move. Move with `git mv` where possible so history is preserved. Never silently rewrite history.

If a scattered record is not actually a decision (e.g., it is a meeting note or brainstorm), leave it where it is or move it to `docs/design-docs/` instead.

## 10. Update CONTEXT.md

Add the new vocabulary so the rest of the docs can reference it:

- `knowledge-map`
- `exec-plan`
- `reference-doc`
- `design-doc`
- `generated-doc`

If an ADR introduces a new Module name that is not yet in `CONTEXT.md`, add it at the same time.

## 11. Hook the loop

Update `plugins/vision-product-loop/scripts/run_loop.py` and the `vision-product-loop` skill so:

- Build phase emits an ADR for every decision the agent flags as non-trivial.
- Build phase writes `docs/exec-plans/active/<slug>.md` for any task with more than one subtask.
- Reflect phase moves the exec-plan to `completed/` when the task closes with passing evidence.
- `run_loop.py` records ADR and exec-plan paths in `.vision-loop/state.json` (under a `closed_exec_plans` array for the lint check, plus the active path for resume support).

## 12. Lint

```bash
python3 plugins/vision-product-loop/scripts/lint_knowledge_map.py --root <project>
```

Checks:

- `AGENTS.md` (and `CLAUDE.md` if not a symlink) within the line budget (default 100).
- `CLAUDE.md` is a symlink to `AGENTS.md`; if both exist as separate regular files with diverging content the linter emits `map-divergence`.
- All cross-links in map files resolve to existing paths within the project root.
- ADRs have all four required Nygard sections (Status, Context, Decision, Consequences).
- `docs/exec-plans/active/` entries with a slug listed in `.vision-loop/state.json` `closed_exec_plans` should have moved to `completed/`.

The linter exits 0 on pass, 1 on lint failure, 2 on usage error.
