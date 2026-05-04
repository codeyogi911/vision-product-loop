# Vision Product Loop Plugin

This plugin gives Codex a repeatable loop for turning a product vision into working software end to end:

1. Establish or refine a durable vision contract.
2. Grill unclear intent until the goal is crisp enough to act on.
3. Split deep Modules into module visions when the product needs more than one flat contract.
4. Run the operating loop: Research, Build, Verify, Test, Reflect.
5. Repeat until the acceptance gaps are closed.

After the vision is clear, the plugin should provide, select, create, or orchestrate the project-local harnesses, skills, agents, sub-agents, scripts, checks, docs, and iteration tools needed to realize that vision. The exact tools are discovered from the project and the goal; the known thing is the end state.

## Contents

- `skills/vision-product-loop/SKILL.md`: the primary Codex skill.
- `skills/grill-me/SKILL.md`: bundled grill skill for one-question-at-a-time vision alignment.
- `scripts/vision_checklist.py`: helper that turns a markdown vision into a first-pass iteration checklist.
- `scripts/run_loop.py`: deterministic runner for Research, Build, Verify, Test, Reflect loop phases.
- `scripts/self_check.py`: self-check harness that inspects the plugin against `VISION.md`.
- `scripts/discover_project.py`: control plane scanner for docs, agents, architecture signals, and harnesses.
- `scripts/plan_harness.py`: planner for the shortest evidence path from discovery output.
- Root `VISION.md`: the product-level contract.
- Root `visions/<module-id>.md`: optional module vision contracts for Deep Module work.

## Self-Check Loop

The skill owns the product loop. The self-check harness provides deterministic evidence for the first bootstrap slice:

```bash
python3 plugins/vision-product-loop/scripts/self_check.py --json
```

The harness reads project-root `VISION.md`, inspects the plugin manifest and main skill, writes `.vision-loop/state.json`, and selects the next concrete gap. It should report at least one gap unless `.vision-loop/state.json` is explicitly marked `complete`.

Use `--run-tests` when the loop needs validation evidence recorded directly in machine state:

```bash
python3 plugins/vision-product-loop/scripts/self_check.py --json --run-tests
```

## Grill Alignment

The plugin includes `skills/grill-me/SKILL.md` so the vision phase is portable. Use it to interview the user one question at a time, provide a recommended answer with each question, and explore the codebase instead of asking when the answer is already discoverable locally. As each branch is resolved, update `VISION.md` continuously.

## Operating Loop

The loop engine is:

1. Research: read the vision, module visions, context docs, code, current state, and prior evidence; choose the smallest high-leverage slice.
2. Build: make the smallest coherent product, harness, skill, Adapter, script, prompt, evaluator, or documentation change.
3. Verify: run or perform the evidence-producing harness that proves or falsifies the slice against the vision.
4. Test: run the strongest relevant regression checks available in the project.
5. Reflect: compare evidence against the vision, update `.vision-loop/state.json`, record the remaining gap, and return to Research.

When the user returns, the plugin should read `VISION.md`, `visions/`, `CONTEXT.md`, and `.vision-loop/state.json`, infer the next safe phase, and continue without asking what to do next when the path is already inside the autonomy boundary.

Run the deterministic loop runner when the safe automated part of the loop should execute as a batch:

```bash
python3 plugins/vision-product-loop/scripts/run_loop.py --slice-budget 5 --json
```

The runner records Research, Build, Verify, Test, and Reflect events in `.vision-loop/state.json`. When no gaps remain and validation evidence passes, it writes `status: complete` with `stop_reason: vision_complete`.

## Harnesses

A harness is an evidence-producing capability, not a file type. Existing commands, generated commands, skills, evaluators, screenshots, demos, benchmarks, checklists, tests, and project-specific workflows can all be harnesses.

Generated Python or JavaScript files are only Implementations or Adapters behind the harness Interface. Prefer existing project harnesses first; create the smallest missing Adapter only when the vision cannot be verified without it.

## Module Visions

Use module visions when the root product vision contains a Deep Module that needs its own Interface, Implementation options, Depth, Seam, Adapter, Leverage, Locality, research questions, and proof harnesses.

The default location is `visions/<module-id>.md`. Each module vision should link back to root `VISION.md`, preserve the product promise, and make the Module's research options explicit until evidence picks the next shape. The skill should read `CONTEXT.md` and `docs/adr/` first, then update `CONTEXT.md` when a new Module term becomes durable.

An Intelligence Layer is the canonical example: it may research prompt-only reasoning, rubric scoring, evaluator-backed ranking, retrieval, planner/verifier separation, or a hybrid while keeping a stable Interface for the product loop.

## Batch Execution

The plugin does not require the user to restart every small slice. Once the vision and autonomy boundary are clear, Codex can run a batch with a slice budget, such as five slices, and keep going until the budget is exhausted, the vision is complete, the next action crosses the autonomy boundary, or a real blocker remains.

At the end of a batch, Codex should report what changed, what evidence was collected, why it stopped, and which gap remains.

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

Marketplace registration was intentionally left out of this scaffold. Add a repo-local `.agents/plugins/marketplace.json` entry when you want this plugin to appear in Codex plugin ordering.
