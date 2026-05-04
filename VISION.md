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

## Proper Scaffold

A proper scaffold is not merely a plugin folder with a manifest, skill, and helper scripts. It is a product-building system that can take a user from vision to realized project end to end.

The user starts with a vision. The plugin interviews and grills them until the product intent is clear enough to act on. Once the vision is defined, the plugin should provide, select, create, or orchestrate whatever harnesses, skills, agents, sub-agents, scripts, checks, docs, and iteration tools are needed to achieve the end goal.

The loop-running orchestrator owns delegation judgment. When host capabilities and the autonomy boundary allow it, the orchestrator should use sub-agents whenever they materially improve context management, parallel progress, independent verification, or clean task ownership. Deterministic harnesses and scripts may provide orchestration guidance, but they should not hide product judgment behind their own sub-agent runtime.

The grill phase should be a first-class bundled capability, not only a reference to an external skill. The plugin should include a `grill-me` skill that asks one question at a time, provides a recommended answer for each question, explores the codebase instead of asking when possible, and updates `VISION.md` continuously as branches are resolved.

The plugin should not assume in advance which tools are needed for every project. Its core promise is adaptive: the end state is known through the vision, and the loop discovers or creates the means required to reach it.

If the project lacks a needed harness, skill, agent prompt, checklist, evaluator, or script, the plugin should create the smallest project-local version needed to prove progress toward the vision. It should prefer existing project tools first, then generate missing tools only when the vision cannot be verified without them.

When the vision is broad and many tools could be created, the plugin should optimize for the shortest evidence path to the vision: create the smallest slice of product plus the smallest harness that can prove or falsify progress. It should avoid building a large meta-framework before it has demonstrated one real product loop.

The plugin should choose the next implementation slice by picking the highest-uncertainty, highest-leverage gap that can be proven with the smallest local harness. It should prefer slices that validate the whole loop end to end over isolated infrastructure work.

For this plugin itself, the first meaningful slice is: read `VISION.md`, inspect the current plugin, produce a gap list, choose one gap, patch files, run validation, and update loop state.

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

## Operating Loop

The loop is the plugin's core engine. The vision defines the final goal; the loop repeatedly closes the gap between the current project and that goal.

Every autonomous run should move through these phases:

- Research: read `VISION.md`, module visions, `CONTEXT.md`, ADRs, project docs, current state, code, and prior evidence. Identify the highest-uncertainty or highest-leverage gap, preserve open research options, and choose the smallest slice that can produce useful evidence.
- Build: implement the smallest coherent product, harness, skill, Adapter, script, prompt, evaluator, or documentation change needed for the chosen slice.
- Verify: run or perform the evidence-producing harness that directly proves or falsifies the slice against the vision. Verification may be a command, skill workflow, evaluator, screenshot review, demo, generated artifact inspection, benchmark, or manual checklist when automation is not yet possible.
- Test: run the strongest relevant regression checks available in the project, such as unit tests, lint, typecheck, integration tests, browser checks, or plugin self-checks.
- Reflect: compare all evidence against the root vision and any module vision. Update `.vision-loop/state.json`, record what changed, name the remaining gap, update module visions or `CONTEXT.md` when understanding deepens, and return to Research unless the vision is satisfied or the autonomy boundary requires the user.

The loop should not stop after Build or Test if the vision is still unmet. Passing tests is evidence, not the destination. The destination is the realized vision.

When the user returns to the project, the plugin should resume from durable artifacts instead of asking "what next?" by default. It should read `VISION.md`, `visions/`, `CONTEXT.md`, and `.vision-loop/state.json`, infer the next safe loop phase, and continue within the autonomy boundary.

The plugin should provide a deterministic loop runner for the parts of the loop that can be automated safely:

```bash
python3 plugins/vision-product-loop/scripts/run_loop.py --slice-budget 5 --json
```

The runner should execute Research, Build, Verify, Test, and Reflect phases, record phase events in `.vision-loop/state.json`, respect the slice budget, and mark `stop_reason` as `vision_complete` when no gaps remain and required evidence passes.

## Evidence Harnesses

A harness is an evidence-producing capability, not a file type. The harness Interface is: given a slice or acceptance check, produce evidence that can be compared to the vision.

Harnesses may be existing commands, generated commands, skills, evaluators, screenshots, demos, benchmarks, checklists, tests, or project-specific workflows. Python files, JavaScript files, Playwright specs, prompt files, or shell commands are only Implementations or Adapters behind that harness Interface.

The plugin should prefer existing project harnesses first. When evidence is missing, it should create the smallest project-local harness Adapter needed to run the loop, register what the harness proves, and record the command or skill workflow used to collect evidence.

## Loop State

Durable product intent lives in `VISION.md`.

Operational loop state should live separately under `.vision-loop/`, so the vision contract does not become cluttered with every iteration log.

Loop state should be machine-readable, with `.vision-loop/state.json` as the canonical operational file. It can track discovered gaps, selected slice, evidence commands, validation results, remaining gaps, and next actions.

The minimal state shape should start small:

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

Richer fields such as iteration history, created harnesses, agent assignments, and confidence scores can be added only when a real loop needs them.

The skill owns the loop. Scripts may provide helper mechanics, but the Codex skill should drive the judgment: reading `VISION.md`, discovering the project, choosing the next gap, deciding what harness is needed, implementing changes, running evidence, and updating `.vision-loop/state.json`.

Scripts should be optional helpers for deterministic, repeatable tasks: parsing `VISION.md`, validating `.vision-loop/state.json`, checking plugin manifest shape, and summarizing gaps. They should not decide product direction or hide the loop from the user.

The first harness this plugin should provide is a self-check harness that verifies the plugin can read `VISION.md`, inspect its own manifest and skill files, produce `.vision-loop/state.json`, and report at least one concrete gap between the vision and current scaffold. That proves the loop can start.

The self-check harness should fail when no valid gap is found unless `.vision-loop/state.json` is explicitly marked `complete`. If the vision is not complete and the harness cannot identify a next gap, the loop is broken.

## Batch Loop Execution

The plugin should not require the user to approve or restart every tiny slice. Once the vision and autonomy boundary are clear, the agent should be able to run multiple autonomous slices in a single pass.

A batch loop should continue until one of these happens:

- The requested slice budget is exhausted, such as five slices.
- The vision is satisfied and `.vision-loop/state.json` can be marked `complete` with `stop_reason` set to `vision_complete`.
- The next action crosses the autonomy boundary and needs user approval.
- A real blocker appears that cannot be solved by creating a smaller harness or slice.

At the end of a batch, the agent should report how many slices ran, what changed, what evidence was collected, why it stopped, and what gap remains.

## Validation Strategy

The smallest convincing test is to use the plugin on itself, but the ideal test is stronger than a single improvement.

The plugin should start from this `VISION.md`, discover the current plugin scaffold, identify gaps between the vision and the implementation, run an automated iteration loop, and progressively regress the gap between the current scaffold and a complete, usable plugin.

The loop should autonomously choose the next highest-leverage gap, update the plugin skill or companion tooling, run evidence, compare the result to `VISION.md`, update the remaining gap, and continue until it arrives at a proper scaffold.

If the plugin can autonomously improve itself into a complete plugin using its own loop, and that result can be verified, it has a strong proof that the workflow is real rather than merely descriptive.

## Acceptance Checks

- `python3 plugins/vision-product-loop/scripts/run_loop.py --slice-budget 5 --json` writes `.vision-loop/state.json` with Research, Build, Verify, Test, and Reflect phase events.
- The loop runner marks the state `complete` with `stop_reason` set to `vision_complete` when no rubric gaps remain and validation evidence passes.
- `python3 -m unittest discover -s plugins/vision-product-loop/tests` passes.
- `python3 plugins/vision-product-loop/scripts/self_check.py --json --run-tests` exits successfully after the loop runner has marked the state complete.
- The toy project proof records that the plugin can create and run the smallest missing proof harness for a project that only starts with `VISION.md`.
- No repository artifact uses the lowercase vision filename as the canonical product contract.

## Autonomy Boundary

The loop may autonomously edit plugin files, add skills, scripts, docs, tests, run local validation, and update `VISION.md` with evidence and remaining gaps.

The loop must stop and ask before changing the core product promise, deleting user-authored work, adding network-dependent tools, publishing or installing marketplace entries, or making destructive filesystem or git changes.
