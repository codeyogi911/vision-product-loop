# Vision Product Loop

## Product Promise

This plugin helps a user turn an initially fuzzy product idea into a shipped product by forcing a clear vision, interrogating ambiguity with `grill-me`, discovering the project's existing architecture, agents, and harnesses, then running evidence-based implementation loops until the product demonstrably matches the vision.

## Primary Users

The primary user is a builder using Codex on an existing or new software project, who has a product idea but needs help converting it into a precise vision, implementation plan, and repeated build/verify loops.

Secondary users are teams that already have agents, tests, docs, issue trackers, or harnesses and want Codex to respect those instead of imposing a generic workflow.

## Canonical Artifact

The canonical artifact is `VISION.md` at the project root.

The plugin should create or update `VISION.md` continuously as the shared understanding sharpens. It should update the file for clarified product intent, not silently rewrite the vision based only on implementation discoveries.

## Conflict Handling

When a user's current request conflicts with `VISION.md`, the plugin should treat `VISION.md` as the product contract, pause, call out the conflict, and ask whether the user wants to amend the vision or treat the new request as a one-off experiment.

The plugin should not silently drift the product away from the agreed vision.

## Realization Bar

The vision is realized when every must-have capability and acceptance check in `VISION.md` is either demonstrably satisfied by working software or explicitly deferred by the user, and the strongest available project-local evidence has been run.

Evidence can include tests, lint, end-to-end checks, screenshots, demos, evaluators, logs, or whatever harness the repo defines.

For this plugin, self-check evidence proves only that the bootstrap scaffold can inspect itself and find gaps. Toy project proof proves only that missing-harness creation works in a generated sandbox. Neither one is sufficient to claim `vision_complete`.

The plugin should not mark its own vision complete until it has been applied to a real target project outside this repository and recorded `.vision-loop/applied-proof.json` with the target project, the fuzzy vision item, changed files, change summary, passing target-local evidence, and what the loop caused that would not have happened without it.

## Proper Scaffold

A proper scaffold is not merely a plugin folder with a manifest, skill, and helper scripts. It is a product-building system that can take a user from vision to realized project end to end.

The user starts with a vision. The plugin interviews and grills them until the product intent is clear enough to act on. Once the vision is defined, the plugin should provide, select, create, or orchestrate whatever harnesses, skills, agents, sub-agents, scripts, checks, docs, and iteration tools are needed to achieve the end goal.

The loop-running orchestrator owns delegation judgment. When host capabilities and the autonomy boundary allow it, the orchestrator should use sub-agents whenever they materially improve context management, parallel progress, independent verification, or clean task ownership. Deterministic harnesses and scripts may provide orchestration guidance, but they should not hide product judgment behind their own sub-agent runtime.

The grill phase should be a first-class bundled capability, not only a reference to an external skill. The plugin should include a `grill-me` skill that asks one question at a time, provides a recommended answer for each question, explores the codebase instead of asking when possible, and updates `VISION.md` continuously as branches are resolved.

The plugin should not assume in advance which tools are needed for every project. Its core promise is adaptive: the end state is known through the vision, and the loop discovers or creates the means required to reach it.

If the project lacks a needed harness, skill, agent prompt, checklist, evaluator, or script, the plugin should create the smallest project-local version needed to prove progress toward the vision. It should prefer existing project tools first, then generate missing tools only when the vision cannot be verified without them.

When the vision is broad and many tools could be created, the plugin should optimize for the shortest evidence path to the vision, but the planning unit should be the smallest coherent task rather than the smallest possible code slice. A task may contain several subtasks, and those subtasks should roll up into one task-close proof. The loop should avoid building a large meta-framework before it has demonstrated one real product loop.

The plugin should choose the next implementation task by picking the highest-uncertainty, highest-leverage gap that can be proven with a local harness at task close. It should prefer tasks that validate the whole loop end to end over isolated infrastructure work.

For this plugin itself, the first meaningful slice is: read `VISION.md`, inspect the current plugin, produce a gap list, choose one gap, patch files, run validation, and update loop state.

## Knowledge Map

The plugin should treat the project's `docs/` directory as the system of record, with `CLAUDE.md` and `AGENTS.md` as small (≤100 lines) tables of contents pointing at deeper sources of truth. Map files should never become encyclopedias.

The bundled `knowledge-map` skill should run after `VISION.md` is stable (post `grill-me`) and before the first substantial Build phase. It should:

- Detect existing knowledge artefacts (`ARCHITECTURE.md`, `CLAUDE.md`, `AGENTS.md`, `docs/adr/`) and any scattered decision-like records under `docs/`, `notes/`, `wiki/`.
- Grill the user on every major architecture decision one at a time using the bundled `grill-me` skill, and record each resolved decision as an ADR under `docs/adr/NNNN-<slug>.md` in Nygard format.
- Sketch `ARCHITECTURE.md` in matklad style after in-scope decisions are recorded, flagged "draft, grown by loop" until the first Build materialises code.
- Generate `CLAUDE.md` and `AGENTS.md` skeletons within the line budget, pointing at the deeper sources.
- Scaffold the minimum viable layout (`docs/{adr, design-docs, exec-plans/{active, completed}, references, generated}/`) with templates and indexes, but never bootstrap domain-specific docs (`FRONTEND.md`, `SECURITY.md`, etc.) — the loop materialises those when the vision calls for them.
- Migrate scattered decision records into `docs/adr/` only with explicit user confirmation; never silently rewrite history.
- Update `CONTEXT.md` with the new vocabulary (`knowledge-map`, `exec-plan`, `reference-doc`, `design-doc`, `generated-doc`).
- Hook the operating loop so Build emits an ADR for every flagged decision and writes an exec-plan for any task with more than one subtask, and Reflect moves the exec-plan to `completed/` on task close.

The plugin should provide a deterministic scaffold helper and a deterministic linter for the knowledge map:

```bash
python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root <project> --detect --json
python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root <project> --apply
python3 plugins/vision-product-loop/scripts/lint_knowledge_map.py --root <project>
```

The scaffold helper should be idempotent and must not overwrite existing user-authored files. The linter should enforce the map line budget, cross-link resolution, ADR section completeness, and exec-plan placement against `.vision-loop/state.json`.

## Module Visions And Deep Modules

The root `VISION.md` remains the product-level contract. When the product contains deep Modules with their own research questions, Interfaces, harnesses, or architecture tradeoffs, the plugin should split the work into module visions instead of forcing every decision into one flat document.

A module vision should live under `visions/<module-id>.md` unless the project already has a better local convention. Each module vision should link back to the root vision and describe:

- Module promise: what the Module makes possible inside the product vision.
- Interface: the small surface other parts of the product should rely on.
- Implementation: the choices hidden behind the Interface.
- Depth: why the Module should be Deep rather than Shallow.
- Seam: where the Module joins the rest of the product.
- Adapter: any translation layer needed for outside tools, models, harnesses, or runtimes.
- Leverage: why improving this Module improves many loops or features.
- Locality: what changes should stay isolated inside the Module.
- Research options: competing approaches that still need evidence.
- Acceptance checks and harnesses: how the Module vision will be verified.

The plugin should use the `improve-codebase-architecture` lens when a vision asks for architecture deepening. It should read `CONTEXT.md` and `docs/adr/` before naming or reshaping Modules, update `CONTEXT.md` when a new product term becomes important, and use the architecture vocabulary consistently: Module, Interface, Implementation, Depth, Deep, Shallow, Seam, Adapter, Leverage, and Locality.

For example, an agent may have an `Intelligence Layer` module vision. That Module might explore prompt-only reasoning, rubric scoring, evaluator-backed ranking, retrieval over project memory, planner/verifier separation, or a hybrid. The loop should not pretend the answer is known up front. It should keep options visible, pick the next evidence-gathering slice, and evolve the Module until its Interface is stable, its Implementation is replaceable, and its harnesses prove that it helps realize the parent product vision.

## Sprint Task Planning

For applied repositories, the loop should plan in sprint-sized chunks before it starts editing. A sprint is a short container with one or more coherent tasks. A task is the unit that should satisfy a meaningful product outcome, carry acceptance checks, and run broad validation at the end. Subtasks are implementation steps inside the task; they should use inspection or focused probes, not repeated full regression suites.

The default planning shape is:

```text
Sprint -> Task -> Subtasks -> Task-end validation -> Reflection
```

The plugin should provide a work planner:

```bash
python3 plugins/vision-product-loop/scripts/plan_work.py --root <target-project> --json
```

The planner should read the target repo's `VISION.md`, `.vision-loop/state.json`, `TODOS.md`, docs, architecture signals, agents, and harnesses, then produce a sprint/task/subtask plan. The plan should mark `test_cadence` as `task_end`, attach broad checks such as test, typecheck, browser, or eval commands to task-close validation, and keep those broad checks out of ordinary subtasks.

Toy project proof is useful as a regression harness for missing-harness creation, but applied planning must be proven against a real target repository before the plugin claims completion.

## Operating Loop

The loop is the plugin's core engine. The vision defines the final goal; the loop repeatedly closes the gap between the current project and that goal.

Every autonomous run should move through these phases:

- Research: read `VISION.md`, module visions, `CONTEXT.md`, ADRs, project docs, current state, code, and prior evidence. Identify the highest-uncertainty or highest-leverage gap, preserve open research options, and choose the smallest coherent task that can produce useful evidence.
- Build: declare the task's progress indicators and target direction, capture a baseline snapshot (git ref plus measured indicators), then implement the task through subtasks, keeping each subtask bounded to the task promise.
- Verify: use inspection or focused probes during subtasks, then run or perform the evidence-producing harness that directly proves or falsifies the full task against the vision. Verification may be a command, skill workflow, evaluator, screenshot review, demo, generated artifact inspection, benchmark, or manual checklist when automation is not yet possible.
- Test: run the strongest relevant regression checks at task-end validation, such as unit tests, lint, typecheck, integration tests, browser checks, or plugin self-checks. Do not pay this cost after every ordinary subtask unless the subtask is risky enough to need it.
- Reflect: capture a result snapshot (git ref plus measured indicators), compare against the baseline using the declared target direction, mark the task `kept` or `reverted`, and append the decision and reason to `task_history`. Compare all task-end evidence against the root vision and any module vision. Update `.vision-loop/state.json`, name the remaining gap, update module visions or `CONTEXT.md` when understanding deepens, and return to Research unless the vision is satisfied or the autonomy boundary requires the user.

The loop should not stop after Build or Test if the vision is still unmet. Passing tests is evidence, not the destination. The destination is the realized vision.

When the user returns to the project, the plugin should resume from durable artifacts instead of asking "what next?" by default. It should read `VISION.md`, `visions/`, `CONTEXT.md`, and `.vision-loop/state.json`, infer the next safe loop phase, and continue within the autonomy boundary.

The plugin should provide a deterministic loop runner for the parts of the loop that can be automated safely:

```bash
python3 plugins/vision-product-loop/scripts/run_loop.py --slice-budget 5 --json
```

The runner should execute Research, Build, Verify, Test, and Reflect phases, record phase events in `.vision-loop/state.json`, respect the slice budget, and mark `stop_reason` as `vision_complete` when no gaps remain, required validation evidence passes, and applied-project proof has been recorded.

## Evidence Harnesses

A harness is an evidence-producing capability, not a file type. The harness Interface is: given a slice or acceptance check, produce evidence that can be compared to the vision.

Harnesses may be existing commands, generated commands, skills, evaluators, screenshots, demos, benchmarks, checklists, tests, or project-specific workflows. Python files, JavaScript files, Playwright specs, prompt files, or shell commands are only Implementations or Adapters behind that harness Interface.

The plugin should prefer existing project harnesses first. When evidence is missing, it should create the smallest project-local harness Adapter needed to run the loop, register what the harness proves, and record the command or skill workflow used to collect evidence.

Harnesses should stay immutable inside the task whose evidence they produce. The loop should not edit a harness during the same task that depends on it; harness changes belong in their own dedicated tasks with their own baseline and accept-or-revert decision. If a task's Build phase modifies a harness it relies on, the task should be marked `reverted` with reason `harness_modified_during_task`, then reopened either as a harness-change task or as a product task whose subtasks leave the harness alone. Adding a brand-new harness as the explicit promise of a task is allowed.

## Indicators And The Accept Or Revert Ledger

Every task should declare at least one progress indicator before Build begins. An indicator is a measurable quantity the task expects to move: open gap count, harness pass count, evaluator score, screenshot diff, demo step count, benchmark number, or any project-local scalar. The task should also declare a target direction per indicator: `decrease`, `increase`, `equals:<value>`, `true`, or `false`.

Baseline and result snapshots should each record the git ref and the measured indicators at that moment. The Reflect phase should compare result against baseline using the declared targets and emit one of `kept`, `reverted`, or `pending`. `kept` means the targets were met or the regression is explicitly accepted with a recorded reason. `reverted` means the result regressed against a non-negotiable target and the loop should restore the baseline git ref before continuing. `pending` means evidence is still being collected.

This per-task accept-or-revert ledger is what makes overnight or batch autonomous runs trustworthy. Without it, the loop has no way to detect that an iteration made the product worse against the vision.

## Loop State

Durable product intent lives in `VISION.md`.

Operational loop state should live separately under `.vision-loop/`, so the vision contract does not become cluttered with every iteration log.

Loop state should be machine-readable, with `.vision-loop/state.json` as the canonical operational file. It can track discovered gaps, selected task, subtasks, task-end evidence commands, validation results, remaining gaps, and next actions.

The minimal state shape should start small:

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

`baseline` and `result` are snapshots in the form `{"git_ref": "<sha>", "indicators": {<name>: <number_or_bool>}, "recorded_at": "<iso8601>"}`. `target_indicators` maps each indicator name to a target like `"decrease"`, `"increase"`, `"true"`, `"false"`, or `"equals:<value>"`. Each `task_history` entry has `id`, `title`, `baseline`, `target_indicators`, `result`, `decision` (`kept` | `reverted` | `pending`), and `decision_reason`. The current task's live snapshots also live at the top level so an interrupted loop can resume without parsing history.

Richer fields such as iteration history, created harnesses, agent assignments, and confidence scores can be added only when a real loop needs them.

The skill owns the loop. Scripts may provide helper mechanics, but the Codex skill should drive the judgment: reading `VISION.md`, discovering the project, choosing the next gap, deciding what harness is needed, implementing changes, running evidence, and updating `.vision-loop/state.json`.

Scripts should be optional helpers for deterministic, repeatable tasks: parsing `VISION.md`, validating `.vision-loop/state.json`, checking plugin manifest shape, and summarizing gaps. They should not decide product direction or hide the loop from the user.

The first harness this plugin should provide is a self-check harness that verifies the plugin can read `VISION.md`, inspect its own manifest and skill files, produce `.vision-loop/state.json`, and report at least one concrete gap between the vision and current scaffold. That proves the loop can start.

The self-check harness should fail when no valid gap is found unless `.vision-loop/state.json` is explicitly marked `complete`. If the vision is not complete and the harness cannot identify a next gap, the loop is broken.

## Batch Loop Execution

The plugin should not require the user to approve or restart every tiny slice. Once the vision and autonomy boundary are clear, the agent should be able to run a coherent task with subtasks in a single pass.

A batch loop should continue until one of these happens:

- The requested task or sprint budget is exhausted.
- The vision is satisfied and `.vision-loop/state.json` can be marked `complete` with `stop_reason` set to `vision_complete`.
- The next action crosses the autonomy boundary and needs user approval.
- A real blocker appears that cannot be solved by creating a smaller harness or subtask.

At the end of a batch, the agent should report which tasks and subtasks ran, what changed, what task-end evidence was collected, why it stopped, and what gap remains.

## Validation Strategy

The first bootstrap test is to use the plugin on itself, but that is not the convincing proof. Self-improvement can show that the scaffold can read `VISION.md`, discover gaps, run an automated iteration loop, update plugin artifacts, and record state. It cannot prove that the loop helps ship a real product change.

The convincing proof is applied use on a real target repository outside this one. The target should start with a fuzzy product item or incomplete vision-backed task. The loop should clarify the task, choose a small coherent implementation task, change target source or docs in a way a user would care about, run target-local evidence, and capture the diff summary that would not have happened without the loop.

Until that applied proof exists, additional scripts and rubric entries should be treated as suspect. The plugin should prune or simplify scaffold that is not justified by a real target loop.

## Acceptance Checks

- `python3 plugins/vision-product-loop/scripts/run_loop.py --slice-budget 5 --json` writes `.vision-loop/state.json` with Research, Build, Verify, Test, and Reflect phase events.
- `python3 plugins/vision-product-loop/scripts/plan_work.py --root <target-project> --json` emits a sprint/task/subtask plan with `test_cadence` set to `task_end`.
- Without `.vision-loop/applied-proof.json`, the loop runner reports `missing-applied-project-proof` instead of marking the plugin complete.
- `.vision-loop/applied-proof.json` records a real target project outside this repository, the fuzzy vision item exercised, changed files, change summary, passing target-local evidence, and why the loop mattered.
- The loop runner marks the state `complete` with `stop_reason` set to `vision_complete` when no rubric gaps remain, applied-project proof is valid, and validation evidence passes.
- Every task recorded in `.vision-loop/state.json` `task_history` carries a `baseline` snapshot, a `result` snapshot, declared `target_indicators`, and a `decision` of `kept`, `reverted`, or `pending` with a `decision_reason`.
- A task whose Build phase modifies a harness it depends on is marked `reverted` with reason `harness_modified_during_task`.
- `python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root <project> --apply` creates the minimum viable `docs/` layout idempotently and never overwrites existing user-authored files.
- `python3 plugins/vision-product-loop/scripts/lint_knowledge_map.py --root <project>` exits 0 on a freshly scaffolded layout and exits 1 when `CLAUDE.md` or `AGENTS.md` exceed the line budget, when map cross-links break, when an ADR is missing a required Nygard section, or when `docs/exec-plans/active/` holds a slug closed in `.vision-loop/state.json`.
- The bundled `knowledge-map` skill at `plugins/vision-product-loop/skills/knowledge-map/SKILL.md` runs between `grill-me` and the operating loop on a fresh repo.
- `python3 -m unittest discover -s plugins/vision-product-loop/tests` passes.
- `python3 plugins/vision-product-loop/scripts/self_check.py --json --run-tests` exits successfully after the loop runner has marked the state complete.
- The toy project proof records that the plugin can create and run the smallest missing proof harness for a project that only starts with `VISION.md`, but it is not treated as proof of applied planning or product usefulness.
- No repository artifact uses the lowercase vision filename as the canonical product contract.

## Autonomy Boundary

The loop may autonomously edit plugin files, add skills, scripts, docs, tests, run local validation, and update `VISION.md` with evidence and remaining gaps.

The loop must stop and ask before changing the core product promise, deleting user-authored work, adding network-dependent tools, publishing or installing marketplace entries, or making destructive filesystem or git changes.

On real target repositories, the loop should capture the current status, name the intended task and likely files before broad edits, keep changes inside that task, and report the diff plus target-local evidence before claiming the task shipped. If the user asks for staged proposals or dry-run planning, the loop should stop at the proposal until the user grants an edit scope.
