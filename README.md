# Vision Product Loop

Vision Product Loop is a Codex plugin for turning a fuzzy product idea into a working project through a durable vision contract, focused grilling, project discovery, evidence-producing harnesses, and repeated build/verify loops.

The plugin treats `VISION.md` as the product contract. It helps Codex clarify the intent, discover the repo's existing architecture and validation tools, choose the smallest useful implementation slice, collect evidence, and keep iterating until the built product matches the agreed vision.

## What It Does

- Establishes or refines a root `VISION.md`.
- Uses a bundled `grill-me` skill to collapse ambiguity before implementation.
- Discovers project docs, agents, architecture signals, and harnesses.
- Plans the shortest evidence path for the next product slice.
- Creates small project-local proof harnesses when none exist.
- Runs a Research, Build, Verify, Test, Reflect loop.
- Records operational state separately under `.vision-loop/`.
- Supports module visions for deep product or architecture areas.

## Repository Layout

```text
VISION.md                                  Product-level contract for this plugin
CONTEXT.md                                 Domain vocabulary used by the loop
visions/                                   Module vision contracts
plugins/vision-product-loop/               Codex plugin implementation
plugins/vision-product-loop/skills/        Codex skills exposed by the plugin
plugins/vision-product-loop/scripts/       Deterministic helper scripts and harnesses
plugins/vision-product-loop/tests/         Regression tests for plugin helpers
.agents/plugins/marketplace.json           Local plugin marketplace registration
```

## Quick Start

Run the plugin self-check:

```bash
python3 plugins/vision-product-loop/scripts/self_check.py --json
```

Run the deterministic loop runner:

```bash
python3 plugins/vision-product-loop/scripts/run_loop.py --slice-budget 5 --json
```

Run the test suite:

```bash
python3 -m unittest discover -s plugins/vision-product-loop/tests
```

## Useful Helpers

Create a checklist from a vision document:

```bash
python3 plugins/vision-product-loop/scripts/vision_checklist.py --vision VISION.md
```

Discover a project's control plane:

```bash
python3 plugins/vision-product-loop/scripts/discover_project.py --root .
```

Plan the shortest proof path from discovery output:

```bash
python3 plugins/vision-product-loop/scripts/plan_harness.py --discovery discovery.json
```

Create a missing harness from a plan:

```bash
python3 plugins/vision-product-loop/scripts/create_harness.py --plan harness-plan.json --root . --apply
```

Plan local work versus optional delegation:

```bash
python3 plugins/vision-product-loop/scripts/plan_orchestration.py --tasks tasks.json --allow-delegation
```

Run the toy project proof:

```bash
python3 plugins/vision-product-loop/scripts/run_toy_proof.py --target .vision-loop/toy-project
```

## Design Notes

The skill owns product judgment. Scripts provide deterministic mechanics for discovery, planning, validation, and state recording, but they should not decide product direction or hide the loop from the user.

Harnesses are evidence-producing capabilities, not a specific file type. A harness can be a command, skill workflow, evaluator, screenshot review, demo, benchmark, checklist, test, or project-specific workflow.

The loop-running orchestrator owns delegation judgment. When host capabilities and the autonomy boundary allow it, sub-agents can be used for independent slices, context management, parallel progress, independent verification, or clean task ownership.

## License

MIT
