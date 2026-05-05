# Vision Product Loop Plugin

This plugin gives a coding agent (Claude Code or Codex) a repeatable loop for turning a product vision into working software end to end:

1. Establish or refine a durable vision contract.
2. Grill unclear intent until the goal is crisp enough to act on.
3. Establish the knowledge map: grill the user on every major architecture decision, record each as an ADR, sketch `ARCHITECTURE.md`, generate `CLAUDE.md` and `AGENTS.md` as ≤100-line maps, scaffold the `docs/` system of record.
4. Split deep Modules into module visions when the product needs more than one flat contract.
5. Run the operating loop: Research, Build, Verify, Test, Reflect.
6. Repeat until the acceptance gaps are closed.

After the vision is clear, the plugin should provide, select, create, or orchestrate the project-local harnesses, skills, agents, sub-agents, scripts, checks, docs, and iteration tools needed to realize that vision. The exact tools are discovered from the project and the goal; the known thing is the end state.

## Contents

- `.claude-plugin/plugin.json`: Claude Code plugin manifest.
- `.codex-plugin/plugin.json`: Codex plugin manifest.
- `skills/vision-product-loop/SKILL.md`: the primary skill (loaded by both runtimes).
- `skills/grill-me/SKILL.md`: bundled grill skill for one-question-at-a-time vision alignment.
- `skills/knowledge-map/SKILL.md`: bundled skill that grills the user on architecture decisions, records ADRs, sketches `ARCHITECTURE.md`, scaffolds the `docs/` system of record, and migrates scattered decision records.
- `scripts/vision_checklist.py`: helper that turns a markdown vision into a first-pass iteration checklist.
- `scripts/run_loop.py`: deterministic runner for Research, Build, Verify, Test, Reflect loop phases.
- `scripts/self_check.py`: self-check harness that inspects the plugin against `VISION.md`.
- `scripts/discover_project.py`: control plane scanner for docs, agents, architecture signals, and harnesses.
- `scripts/plan_harness.py`: planner for the shortest evidence path from discovery output.
- `scripts/plan_work.py`: applied project planner that emits a sprint/task/subtask plan with task-end validation cadence.
- `scripts/scaffold_knowledge_map.py`: deterministic detect/apply helper that scaffolds the `docs/` system of record, ADR templates, and map skeletons without overwriting user-authored files.
- `scripts/lint_knowledge_map.py`: deterministic linter that enforces the map line budget, cross-link resolution, ADR section completeness, and exec-plan placement.
- Root `VISION.md`: the product-level contract.
- Root `visions/<module-id>.md`: optional module vision contracts for Deep Module work.

## Self-Check Loop

The skill owns the product loop. The self-check harness provides deterministic evidence for the first bootstrap slice:

```bash
python3 plugins/vision-product-loop/scripts/self_check.py --json
```

The harness reads project-root `VISION.md`, inspects the plugin manifest and main skill, writes `.vision-loop/state.json`, and selects the next concrete gap. It should report at least one gap unless `.vision-loop/state.json` is explicitly marked `complete`. For this plugin, self-check can only prove the bootstrap loop; completion also requires applied-project proof from a real target outside this repository.

Use `--run-tests` when the loop needs validation evidence recorded directly in machine state:

```bash
python3 plugins/vision-product-loop/scripts/self_check.py --json --run-tests
```

## Applied Project Proof

Toy proof and self-check are useful bootstrap harnesses, but they do not prove product usefulness. Before this plugin can claim `status: complete` with `stop_reason: vision_complete`, record `.vision-loop/applied-proof.json` from a real target project outside this repository:

```json
{
  "target_project": "/absolute/path/to/real-target",
  "target_is_external": true,
  "vision_item": "The fuzzy product item the loop clarified and shipped.",
  "changed_files": ["path/in/target"],
  "change_summary": ["What changed in the target project."],
  "evidence": [
    {
      "kind": "target-test",
      "command": "target-local validation command",
      "passed": true,
      "detail": "What the evidence proved."
    }
  ],
  "would_not_have_happened_without_loop": "Why the loop changed the outcome."
}
```

The evidence must include at least one passing target-local proof item that is not `self_check.py`, `run_loop.py`, or `run_toy_proof.py`.

## Grill Alignment

The plugin includes `skills/grill-me/SKILL.md` so the vision phase is portable. Use it to interview the user one question at a time, provide a recommended answer with each question, and explore the codebase instead of asking when the answer is already discoverable locally. As each branch is resolved, update `VISION.md` continuously.

## Knowledge Map

Once `VISION.md` is stable, before substantial Build, run the bundled `knowledge-map` skill. It treats `docs/` as the system of record and `CLAUDE.md`/`AGENTS.md` as ≤100-line tables of contents pointing at deeper sources of truth.

The skill grills the user on every major architecture decision one at a time, records each resolved decision as an ADR in `docs/adr/NNNN-<slug>.md`, sketches `ARCHITECTURE.md` in matklad style, generates the map files within budget, and scaffolds the minimum viable `docs/{adr,design-docs,exec-plans/{active,completed},references,generated}/` layout. It does not bootstrap domain-specific docs; the loop materialises those when the vision calls for them.

```bash
python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root <project> --detect --json
python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root <project> --apply
python3 plugins/vision-product-loop/scripts/lint_knowledge_map.py --root <project>
```

The scaffold helper is idempotent and never overwrites user-authored files. The linter enforces the map line budget, cross-link resolution, ADR Nygard sections, and exec-plan placement against `.vision-loop/state.json`.

## Operating Loop

The loop engine is:

1. Research: read the vision, module visions, context docs, code, current state, and prior evidence; choose the smallest coherent high-leverage task.
2. Build: make the coherent product, harness, skill, Adapter, script, prompt, evaluator, or documentation change through subtasks.
3. Verify: use inspection or focused probes during subtasks, then run or perform the evidence-producing harness that proves or falsifies the full task against the vision.
4. Test: run the strongest relevant regression checks at task-end validation, not after every ordinary subtask.
5. Reflect: compare evidence against the vision, update `.vision-loop/state.json`, record the remaining gap, and return to Research.

When the user returns, the plugin should read `VISION.md`, `visions/`, `CONTEXT.md`, and `.vision-loop/state.json`, infer the next safe phase, and continue without asking what to do next when the path is already inside the autonomy boundary.

Run the deterministic loop runner when the safe automated part of the loop should execute as a batch:

```bash
python3 plugins/vision-product-loop/scripts/run_loop.py --slice-budget 5 --json
```

The runner records Research, Build, Verify, Test, and Reflect events in `.vision-loop/state.json`. When no gaps remain, applied-project proof is present, and validation evidence passes, it writes `status: complete` with `stop_reason: vision_complete`.

## Harnesses

A harness is an evidence-producing capability, not a file type. Existing commands, generated commands, skills, evaluators, screenshots, demos, benchmarks, checklists, tests, and project-specific workflows can all be harnesses.

Generated Python or JavaScript files are only Implementations or Adapters behind the harness Interface. Prefer existing project harnesses first; create the smallest missing Adapter only when the vision cannot be verified without it.

## Applied Work Planning

For real repositories, plan in a bigger chunk before editing:

```text
Sprint -> Task -> Subtasks -> Task-end validation -> Reflection
```

Use `plan_work.py` against the target project:

```bash
python3 plugins/vision-product-loop/scripts/plan_work.py --root <target-project> --json
```

The planner reads target `VISION.md`, `.vision-loop/state.json`, `TODOS.md`, docs, architecture signals, agents, and harnesses. It emits `planning_granularity: sprint_task_subtask` and `test_cadence: task_end`, chooses the next task from an open loop-state gap, open TODO, or vision-backed planning fallback, then keeps broad commands such as test, typecheck, browser, and eval suites at task close.

Subtasks should usually use inspection, code review, local reasoning, or a focused probe. Running broad validation after every subtask creates noise and slows the loop; reserve it for task-end validation unless the subtask is risky enough to justify it.

## Module Visions

Use module visions when the root product vision contains a Deep Module that needs its own Interface, Implementation options, Depth, Seam, Adapter, Leverage, Locality, research questions, and proof harnesses.

The default location is `visions/<module-id>.md`. Each module vision should link back to root `VISION.md`, preserve the product promise, and make the Module's research options explicit until evidence picks the next shape. The skill should read `CONTEXT.md` and `docs/adr/` first, then update `CONTEXT.md` when a new Module term becomes durable.

An Intelligence Layer is the canonical example: it may research prompt-only reasoning, rubric scoring, evaluator-backed ranking, retrieval, planner/verifier separation, or a hybrid while keeping a stable Interface for the product loop.

## Batch Execution

The plugin does not require the user to restart every small slice. Once the vision and autonomy boundary are clear, Codex can run a coherent task with subtasks and keep going until the task or sprint budget is exhausted, the vision is complete, the next action crosses the autonomy boundary, or a real blocker remains. The deterministic runner still accepts a legacy slice budget for scaffold checks; applied project work should translate that into task or sprint scope.

At the end of a batch, Codex should report which task and subtasks ran, what changed, what task-end evidence was collected, why it stopped, and which gap remains.

## Checklist Helper

```bash
python3 plugins/vision-product-loop/scripts/vision_checklist.py --vision VISION.md
```

## Project Discovery

Use `discover_project.py` when the loop needs a quick view of the project control plane before choosing or creating a harness:

```bash
python3 plugins/vision-product-loop/scripts/discover_project.py --root .
```

Use `plan_harness.py` on discovery JSON to pick the shortest evidence path. It reuses existing harnesses first, then recommends the smallest missing harness to create:

```bash
python3 plugins/vision-product-loop/scripts/plan_harness.py --discovery discovery.json
```

Use `plan_work.py` when the project already has enough real surface area that a tiny slice plan is too small:

```bash
python3 plugins/vision-product-loop/scripts/plan_work.py --root <target-project> --json
```

Use `create_harness.py` when the shortest evidence path requires a missing proof tool. It is dry-run by default and only writes files with `--apply`:

```bash
python3 plugins/vision-product-loop/scripts/create_harness.py --plan harness-plan.json --root .
python3 plugins/vision-product-loop/scripts/create_harness.py --plan harness-plan.json --root . --apply
```

Use `plan_orchestration.py` to decide which tasks stay local, which independent sidecar work can delegate, and which tasks must stop at the autonomy boundary:

```bash
python3 plugins/vision-product-loop/scripts/plan_orchestration.py --tasks tasks.json --allow-delegation
```

## Toy Project Proof

Use `run_toy_proof.py` for an end-to-end proof on a generated toy project. It creates a target `VISION.md`, discovers that no harness exists, plans the shortest proof path, creates a harness, runs it, and writes proof JSON:

```bash
python3 plugins/vision-product-loop/scripts/run_toy_proof.py --target .vision-loop/toy-project
```

Toy proof is a regression harness for missing-harness creation. It is intentionally not accepted as applied planning proof; use a real target repository with `plan_work.py`, ship one small change, and record `.vision-loop/applied-proof.json`.

## Installing The Plugin

The repository ships with marketplace manifests for both supported runtimes:

- Claude Code: `.claude-plugin/marketplace.json` at the repo root. Install with `/plugin marketplace add codeyogi911/vision-product-loop` then `/plugin install vision-product-loop@vision-product-loop`.
- Codex: `.agents/plugins/marketplace.json` at the repo root, registered as a local source. Adapt the `source` field to your environment when publishing.
