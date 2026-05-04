---
name: vision-product-loop
description: Use when the user wants to create, define, grill, implement, or iterate on a product from a vision; compare a repository against a vision; or coordinate agents, sub-agents, harnesses, tests, and acceptance criteria until the product matches the agreed goal.
---

# Vision Product Loop

## Purpose

Turn a product vision into working software end to end by creating a durable vision contract, pressure-testing it with the user, discovering the project's own architecture and harnesses, then iterating until the observed product satisfies the contract.

This skill is intentionally stack-agnostic. The project may define any architecture, agent setup, sub-agent plan, issue tracker, test harness, demo harness, screenshot harness, evaluator, or release process. Let those local definitions steer execution.

The proper scaffold is adaptive: after the vision is clear, provide, select, create, or orchestrate whatever project-local harnesses, skills, agents, sub-agents, scripts, checks, docs, and iteration tools are needed to reach the end goal. Do not assume the right tools in advance; discover or create the means from the vision.

When the product vision contains deep Modules, split the work into module visions instead of flattening every architecture decision into the root contract. A module vision captures the Module promise, Interface, Implementation options, intended Depth, Seam, Adapter, Leverage, Locality, research questions, and proof harnesses.

The operating loop is Research, Build, Verify, Test, Reflect. Treat tests as evidence, not as the destination. The destination is the realized vision.

## Core Principles

- Treat the vision as the source of truth for product intent, not as a vague brainstorm.
- Treat project-root `VISION.md` as the canonical product contract once it exists.
- Use the repo's own language, docs, agents, and validation tools before inventing process.
- Grill only until the work is crisp enough to act; do not turn alignment into ceremony.
- Change implementation freely when the vision demands it, but change the vision only when the user agrees.
- Keep every loop grounded in evidence: tests, screenshots, demos, logs, acceptance checks, or direct code inspection.
- Prefer the shortest evidence path: build the smallest product slice plus the smallest proof harness that can prove or falsify progress toward the vision.
- If a project is missing a needed harness, script, evaluator, skill, or agent prompt, create the smallest project-local version needed to prove progress.
- Treat a harness as an evidence-producing capability, not a file type. Commands, skills, evaluators, demos, screenshots, benchmarks, checklists, and tests can all be harnesses.
- Use module visions for Deep Modules whose Interface, Implementation, Seam, Adapter, Leverage, or Locality needs deeper thought than the root `VISION.md` can carry cleanly.
- Stop only when the vision is satisfied, the user changes direction, or a concrete blocker remains.
- Stop and ask before changing the product promise, deleting user-authored work, adding network-dependent tools, publishing or installing marketplace entries, or making destructive filesystem or git changes.

## Workflow

### 1. Find Or Establish The Vision

Look for vision sources in this order:

- `VISION.md` at the project root
- Current conversation and explicit user instructions
- `docs/VISION.md`
- `docs/product/VISION.md`
- `CONTEXT.md`, `README.md`, product specs, PRDs, ADRs, issue tracker docs

If no durable vision exists, draft one in the smallest useful form and ask for confirmation before treating it as binding. Prefer uppercase `VISION.md` at the project root unless the user explicitly chooses another artifact.

When a user request conflicts with `VISION.md`, call out the conflict and ask whether to amend the vision or treat the request as a one-off experiment. Do not silently drift the product away from the agreed contract.

A useful vision contract has:

- Product promise: the thing this product makes possible
- Primary users and contexts
- Jobs to be done
- Must-have capabilities
- Experience qualities: speed, tone, polish, reliability, accessibility, density, delight, or other domain-specific standards
- Non-goals and boundaries
- Acceptance checks
- Open questions

### 2. Grill For Shared Understanding

Use the bundled `grill-me` skill from `skills/grill-me/SKILL.md` for the alignment phase. If another host-provided `grill-me` skill is already active, follow the same contract: interview the user until shared understanding, provide a recommended answer for each question, ask questions one at a time, and explore the codebase instead of asking when the answer is discoverable locally.

Ask questions that collapse uncertainty:

- What would make this product obviously successful?
- What user behavior should change because this exists?
- What must never be compromised?
- What counts as a shippable first version?
- What would make the current implementation feel wrong even if tests pass?
- What harness or demo proves the product is real?

After each resolved branch, update `VISION.md` continuously with clarified product intent. Restate the vision contract and ask for correction only when material ambiguity remains.

### 3. Split Into Module Visions For Deep Modules

Use the `improve-codebase-architecture` lens when the user wants deeper Module design, when a product area has many research options, or when a single root vision is becoming too flat.

Before naming or reshaping a Module, read the project's domain terms and decisions:

- `CONTEXT.md`
- `docs/adr/`
- Other local product or architecture docs discovered in the repo

If the Module name is not already present in `CONTEXT.md`, update `CONTEXT.md` with the product meaning before using it as a durable concept.

Create or update `visions/<module-id>.md` when a Module needs its own contract. A useful module vision has:

- Parent product vision link
- Module promise
- Interface: the small surface callers should rely on
- Implementation: the choices hidden behind the Interface
- Depth: why the Module should be Deep rather than Shallow
- Seam: where the Module joins the rest of the product
- Adapter: any translation needed for outside tools, models, harnesses, or runtimes
- Leverage: why improving this Module improves many loops or product paths
- Locality: which changes should stay isolated inside the Module
- Research options
- Acceptance checks and harnesses
- Open questions

For research-heavy Modules such as an Intelligence Layer, preserve competing Implementation options until evidence selects a shape. The loop should choose the next evidence-gathering slice, not prematurely freeze the Interface or hide unresolved tradeoffs.

### 4. Run The Operating Loop

The loop phase order is:

1. Research: read `VISION.md`, module visions, `CONTEXT.md`, ADRs, project docs, current loop state, code, and prior evidence. Identify the highest-uncertainty or highest-leverage gap and choose the smallest slice that can produce useful evidence.
2. Build: implement the smallest coherent product, harness, skill, Adapter, script, prompt, evaluator, or documentation change needed for the chosen slice.
3. Verify: run or perform the harness that directly proves or falsifies the slice against the vision. The harness may be a command, skill workflow, evaluator, screenshot review, demo, generated artifact inspection, benchmark, or checklist.
4. Test: run the strongest relevant regression checks available in the project, such as unit tests, lint, typecheck, integration tests, browser checks, or plugin self-checks.
5. Reflect: compare evidence against the root vision and any module vision. Update `.vision-loop/state.json`, record the remaining gap, update module visions or `CONTEXT.md` when understanding deepens, and return to Research unless the vision is satisfied or the autonomy boundary requires the user.

When the user returns, resume from durable artifacts instead of asking what to do next by default. Read `VISION.md`, `visions/`, `CONTEXT.md`, and `.vision-loop/state.json`, infer the next safe phase, and continue within the autonomy boundary.

Use the deterministic runner when the safe automated part of the loop should be executed as a batch:

```bash
python3 plugins/vision-product-loop/scripts/run_loop.py --slice-budget 5 --json
```

The runner records Research, Build, Verify, Test, and Reflect phase events and can mark `.vision-loop/state.json` complete with `stop_reason: vision_complete` when no gaps remain and required evidence passes.

### 5. Discover The Project Control Plane

Inspect the repo before designing the loop:

- Agent instructions: `AGENTS.md`, `CLAUDE.md`, `.agents/`, `.codex/`
- Domain docs: `CONTEXT.md`, `docs/`, `docs/adr/`, specs, PRDs
- Architecture: package manifests, services, apps, modules, boundaries
- Harnesses: commands, skills, test scripts, lint scripts, e2e suites, visual checks, benchmark scripts, evaluator prompts, demo scripts, manual checklists
- Existing workflow: issue templates, make targets, CI config, release notes

Summarize only what affects the current loop. Do not perform broad refactors just because the vision is broad.

### 6. Build The Iteration Plan

Map the vision to thin vertical slices. Each slice should connect:

- Vision requirement
- User-visible behavior
- Code area
- Harness or evidence
- Acceptance check
- Known risks

Choose the next implementation slice by picking the highest-uncertainty, highest-leverage gap that can be proven with the smallest local harness. Prefer slices that validate the whole loop end to end over isolated infrastructure work.

If sub-agents are available and explicitly permitted by the current host/user, split independent slices across them with disjoint ownership. Otherwise keep the loop local and serial.

### 7. Iterate Until Reality Matches Vision

For each loop:

1. Research the highest-leverage unsatisfied acceptance check.
2. Build the smallest coherent change that moves the product toward the vision.
3. Verify with the direct evidence-producing harness.
4. Test with the strongest relevant regression checks.
5. Reflect against the vision contract.
6. Record the remaining gap and return to Research.

When tests pass but the product still feels short of the vision, trust the vision and add a better harness or explicit acceptance check.

### 8. Run Batch Loops

When the vision and autonomy boundary are clear, do not require the user to restart every tiny slice. Run multiple autonomous slices in one pass when the user asks for a batch, or when continuing is obviously within the agreed boundary.

A batch loop should stop when:

- The requested slice budget is exhausted.
- The vision is satisfied and `.vision-loop/state.json` can be marked `complete`.
- The next action crosses the autonomy boundary.
- A real blocker remains after trying to create a smaller proof harness or smaller slice.

At the end of a batch, report how many slices ran, what changed, what evidence was collected, why it stopped, and what gap remains.

### 9. Keep Machine Loop State

The skill owns the loop. Scripts are helpers for deterministic mechanics, but the Codex skill drives judgment: reading `VISION.md`, discovering the project, choosing the next gap, deciding what proof is needed, implementing changes, running evidence, and updating `.vision-loop/state.json`.

Use `.vision-loop/state.json` as the canonical operational state file when persistent tracking helps the project continue across iterations:

```json
{
  "vision_file": "VISION.md",
  "phase": "research",
  "iteration": 0,
  "current_slice": "",
  "gaps": [],
  "selected_gap": null,
  "harnesses": [],
  "evidence": [],
  "reflection": "",
  "status": "planning",
  "stop_reason": "",
  "remaining_gaps": [],
  "next_actions": []
}
```

Keep durable product intent in `VISION.md`; keep operational state in `.vision-loop/state.json`.

### 10. Use The Self-Check Harness

For this plugin itself, the first deterministic proof tool is the self-check harness:

```bash
python3 plugins/vision-product-loop/scripts/self_check.py --json
```

The self-check harness reads `VISION.md`, inspects this plugin's manifest and skill files, writes `.vision-loop/state.json`, and reports concrete gaps between the vision and current scaffold. It should produce at least one valid gap unless the loop state is explicitly `complete`.

## Done Criteria

The loop is complete when:

- The vision contract has no unresolved must-have acceptance gaps.
- The repo-local validation harness passes, or any failures are clearly unrelated and reported.
- The final response names what changed, what evidence was run, and any residual risk.
- The product can be demonstrated or inspected in the form the user cares about.

## Companion Script

This plugin includes `scripts/vision_checklist.py`, a lightweight helper that scans a vision document and emits an iteration checklist. Use it when a project already has a markdown vision and you want a fast first-pass map from prose to loop items.

It also includes `scripts/self_check.py`, a deterministic self-check harness for bootstrapping the plugin against its own `VISION.md` contract.

Use `scripts/run_loop.py` when you need the deterministic operating loop to execute the safe automated phases, record phase events, respect a slice budget, and mark completion when the evidence satisfies the vision.
