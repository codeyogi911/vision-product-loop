# Vision Product Loop — Reference

Detailed step-by-step workflow for the [vision-product-loop skill](SKILL.md). The SKILL.md file holds the checklist; this file holds the operating detail.

## 1. Find Or Establish The Vision

Look for vision sources in this order:

- `VISION.md` at the project root
- Current conversation and explicit user instructions
- `docs/VISION.md`
- `docs/product/VISION.md`
- `CONTEXT.md`, `README.md`, product specs, PRDs, ADRs, issue tracker docs

If no durable vision exists, draft one in the smallest useful form and ask for confirmation before treating it as binding. Prefer uppercase `VISION.md` at the project root unless the user explicitly chooses another artifact. Once it exists, treat `VISION.md` as the canonical product contract.

When a user request conflicts with `VISION.md`, call out the conflict and ask whether to amend the vision or treat the request as a one-off experiment. Do not silently drift the product away from the agreed contract.

A useful vision contract has:

- Product promise
- Primary users and contexts
- Jobs to be done
- Must-have capabilities
- Experience qualities (speed, tone, polish, reliability, accessibility, density, delight)
- Non-goals and boundaries
- Acceptance checks
- Open questions

## 2. Grill For Shared Understanding

Use the bundled `grill-me` skill from `skills/grill-me/SKILL.md` for the alignment phase. Interview the user until shared understanding, provide a recommended answer for each question, ask questions one at a time, and explore the codebase instead of asking when the answer is discoverable locally.

Ask questions that collapse uncertainty:

- What would make this product obviously successful?
- What user behavior should change because this exists?
- What must never be compromised?
- What counts as a shippable first version?
- What would make the current implementation feel wrong even if tests pass?
- What harness or demo proves the product is real?

After each resolved branch, update `VISION.md` continuously with clarified product intent.

## 3. Establish The Knowledge Map (hard gate before Build)

Once `VISION.md` is stable and before substantial Build, run the bundled `knowledge-map` skill (`plugins/vision-product-loop/skills/knowledge-map/SKILL.md`).

It grills the user on every major architecture decision one at a time (runtime, product surface, persistence, deployment, public API), records each as an ADR under `docs/adr/`, sketches `ARCHITECTURE.md`, generates `AGENTS.md` as a ≤100-line table of contents, creates `CLAUDE.md` as a symlink to `AGENTS.md` so every agent reads one source, scaffolds the `docs/{adr,design-docs,exec-plans,references,generated}/` system of record, migrates any scattered decision records with confirmation, and updates `CONTEXT.md` with the new vocabulary.

```bash
python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root <project> --detect --json
python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root <project> --apply
python3 plugins/vision-product-loop/scripts/lint_knowledge_map.py --root <project>
```

Detect first, then apply, then lint. The lint check enforces the map line budget, cross-link resolution, ADR section completeness, exec-plan placement against `.vision-loop/state.json`, and that `CLAUDE.md` is a symlink to (or content match of) `AGENTS.md`.

This step is a **hard gate**. `plan_work.py` and `run_loop.py` refuse to plan or run a Build slice while only the bootstrap ADR exists; both emit `stop_reason="knowledge_map_required"` until at least one product architecture decision has been recorded. Decisions about *what kind of product to build* (CLI vs web, Python vs Node, SQLite vs hosted DB, single-binary vs containerised, etc.) are user-owned and must be grilled, not arbitrarily picked by the agent.

Do not scaffold domain-specific docs (`FRONTEND.md`, `SECURITY.md`, etc.). The loop materialises those when the vision calls for them.

## 4. Split Into Module Visions For Deep Modules

Use the `improve-codebase-architecture` lens when the user wants deeper Module design, when a product area has many research options, or when a single root vision is becoming too flat.

Before naming or reshaping a Module, read the project's domain terms and decisions:

- `CONTEXT.md`
- `docs/adr/`
- Other local product or architecture docs discovered in the repo

If the Module name is not already present in `CONTEXT.md`, update `CONTEXT.md` with the product meaning before using it as a durable concept.

Create or update `visions/<module-id>.md` when a Module needs its own contract. A useful module vision has:

- Parent product vision link
- Module promise
- Interface, Implementation, Depth, Seam, Adapter, Leverage, Locality
- Research options
- Acceptance checks and harnesses
- Open questions

For research-heavy Modules such as an Intelligence Layer, preserve competing Implementation options until evidence selects a shape.

## 5. Plan Sprint, Task, And Subtasks

Before substantial applied work, create a bigger planning chunk in the shape `Sprint -> Task -> Subtasks -> Task-end validation -> Reflection`:

- Sprint: short container for one or more coherent product tasks.
- Task: the unit that satisfies a meaningful product outcome and owns task-end validation.
- Subtasks: implementation steps inside the task. Use inspection or focused probes; do not run broad regression, typecheck, browser, or eval suites after every ordinary subtask.

```bash
python3 plugins/vision-product-loop/scripts/plan_work.py --root <target-project> --json
```

The planner emits a sprint/task/subtask plan with `test_cadence: task_end`, broad task-close commands, and subtask validation guidance.

## 6. Run The Operating Loop

The phase order is Research, Build, Verify, Test, Reflect.

Phases:

1. Research: read `VISION.md`, module visions, `CONTEXT.md`, ADRs, project docs, current loop state, code, prior evidence. Identify the highest-uncertainty or highest-leverage gap; choose the smallest coherent task that can produce useful evidence.
2. Build: declare the task's progress indicators (open gap count, harness pass count, evaluator score, screenshot diff, benchmark number, or any project-local scalar) and a target direction per indicator (`decrease`, `increase`, `true`, `false`, or `equals:<value>`). Capture a baseline snapshot to `.vision-loop/state.json`: current git ref, measured indicator values, ISO timestamp. Implement the task through subtasks bounded to the task promise. Do not modify a harness the task depends on; harness changes belong in their own task.
3. Verify: use inspection or focused probes during subtasks, then run the harness that proves or falsifies the full task against the vision (command, skill workflow, evaluator, screenshot review, demo, generated artifact inspection, benchmark, or checklist).
4. Test: run the strongest relevant regression checks at task-end validation. Do not pay the full validation cost after every ordinary subtask unless risk justifies it.
5. Reflect: capture a result snapshot. Compare against the baseline using declared targets and emit one of `kept`, `reverted`, or `pending` with a one-line `decision_reason`. Append to `task_history`. If `reverted`, restore the baseline git ref. If Build modified a depended-on harness, mark `reverted` with reason `harness_modified_during_task` and reopen as a harness-change task. Then return to Research unless the vision is satisfied or the autonomy boundary requires the user.

When the user returns, resume from durable artifacts. Read `VISION.md`, `visions/`, `CONTEXT.md`, and `.vision-loop/state.json`, infer the next safe phase, and continue within the autonomy boundary.

```bash
python3 plugins/vision-product-loop/scripts/run_loop.py --slice-budget 5 --json
```

The runner records Research, Build, Verify, Test, and Reflect phase events and can mark `.vision-loop/state.json` complete with `stop_reason: vision_complete` when no gaps remain, required evidence passes, and applied-project proof is valid.

## 7. Discover The Project Control Plane

Inspect the repo before designing the loop:

- Agent instructions: `AGENTS.md`, `CLAUDE.md`, `.agents/`, `.codex/`
- Domain docs: `CONTEXT.md`, `docs/`, `docs/adr/`, specs, PRDs
- Architecture: package manifests, services, apps, modules, boundaries
- Harnesses: commands, skills, test scripts, lint scripts, e2e suites, visual checks, benchmark scripts, evaluator prompts, demo scripts, manual checklists
- Existing workflow: issue templates, make targets, CI config, release notes

Summarize only what affects the current loop. Do not perform broad refactors just because the vision is broad.

## 8. Build The Iteration Plan

Map the vision to coherent tasks. Each task should connect:

- Vision requirement
- User-visible behavior
- Code area
- Harness or evidence
- Acceptance check
- Known risks

Pick the highest-uncertainty, highest-leverage gap that can be proven with task-end validation. Prefer the shortest evidence path, but make the planning unit the smallest coherent task; prefer tasks that validate the whole loop end to end over isolated infrastructure work.

After the vision is clear, the plugin should provide, select, create, or orchestrate whatever project-local harnesses, skills, agents, sub-agents, scripts, checks, docs, and iteration tools are needed to reach the goal.

If sub-agents are available and explicitly permitted, split independent tasks or sidecar research across them with disjoint ownership. Otherwise keep the loop local and serial.

## 9. Iterate Until Reality Matches Vision

For each loop:

1. Research the highest-leverage unsatisfied acceptance check.
2. Build the smallest coherent task that moves the product toward the vision.
3. Work through subtasks with inspection or focused probes.
4. Verify and test with the direct evidence-producing harnesses at task close.
5. Reflect against the vision contract.
6. Record the remaining gap and return to Research.

When tests pass but the product still feels short of the vision, trust the vision and add a better harness or explicit acceptance check.

## 10. Run Batch Loops

When the vision and autonomy boundary are clear, do not require the user to restart every tiny slice. Run a coherent task with subtasks in one pass when continuing is obviously within the agreed boundary.

A batch loop should stop when:

- The task, sprint, or slice budget is exhausted.
- The vision is satisfied and `.vision-loop/state.json` can be marked `complete`; for this plugin, that requires `.vision-loop/applied-proof.json` from a real external target.
- The next action crosses the autonomy boundary.
- A real blocker remains after trying a smaller proof harness or smaller subtask.

At the end of a batch, report which tasks and subtasks ran, what changed, what task-end evidence was collected, why it stopped, and what gap remains.

## 11. Keep Machine Loop State

The skill owns the loop. Scripts are helpers for deterministic mechanics; the skill drives judgment.

Use `.vision-loop/state.json` as the canonical operational state file:

```json
{
  "vision_file": "VISION.md",
  "phase": "research",
  "iteration": 0,
  "current_task": "",
  "current_task_id": null,
  "subtasks": [],
  "gaps": [],
  "selected_gap": null,
  "harnesses": [],
  "evidence": [],
  "indicators": {},
  "target_indicators": {},
  "baseline": null,
  "result": null,
  "task_history": [],
  "reflection": "",
  "status": "planning",
  "stop_reason": "",
  "remaining_gaps": [],
  "next_actions": []
}
```

Keep durable product intent in `VISION.md`; keep operational state in `.vision-loop/state.json`.

`baseline` and `result` are snapshots in the form `{"git_ref": "<sha>", "indicators": {<name>: <number_or_bool>}, "recorded_at": "<iso8601>"}`. `target_indicators` maps each indicator name to one of `decrease`, `increase`, `true`, `false`, or `equals:<value>`. Each `task_history` entry has `id`, `title`, `baseline`, `target_indicators`, `result`, `decision` (`kept` | `reverted` | `pending`), and `decision_reason`. The current task's live `baseline`, `target_indicators`, and `indicators` also live at the top level so an interrupted loop can resume without parsing history. A task with no baseline and no result must not be appended to `task_history`; it should sit in the live top-level fields until both snapshots exist.

## 12. Use The Self-Check Harness

```bash
python3 plugins/vision-product-loop/scripts/self_check.py --json
```

The self-check harness reads `VISION.md`, inspects this plugin's manifest and skill files, writes `.vision-loop/state.json`, and reports concrete gaps between the vision and current scaffold. It produces at least one valid gap unless the loop state is explicitly `complete`.

When evaluating this plugin, the self-check reports `missing-applied-project-proof` until `.vision-loop/applied-proof.json` records a real target project outside this repository, changed files, a change summary, passing target-local evidence, and why the loop mattered.

## Companion Scripts

- `scripts/vision_checklist.py` — scan a markdown vision and emit an iteration checklist.
- `scripts/self_check.py` — deterministic self-check harness for bootstrapping against `VISION.md`.
- `scripts/plan_work.py` — applied planner producing a sprint/task/subtask plan with task-end validation cadence.
- `scripts/run_loop.py` — deterministic operating loop runner.
- `scripts/scaffold_knowledge_map.py` and `scripts/lint_knowledge_map.py` — knowledge-map detect/apply and lint helpers.
