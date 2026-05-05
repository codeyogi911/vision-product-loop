# Vision Product Loop

Vision Product Loop is a plugin for turning a fuzzy product idea into a working project through a durable vision contract, focused grilling, project discovery, evidence-producing harnesses, and repeated build/verify loops.

The plugin treats `VISION.md` as the product contract. It helps the agent clarify the intent, discover the repo's existing architecture and validation tools, choose the smallest useful implementation slice, collect evidence, and keep iterating until the built product matches the agreed vision.

It ships with manifests for both **Claude Code** (`.claude-plugin/`) and **Codex** (`.codex-plugin/`), so the same skills can be installed into either runtime from this repository.

Self-check and toy proof are bootstrap evidence only. This plugin should not claim its own loop is complete until `.vision-loop/applied-proof.json` records a real target project outside this repository, the shipped change, and passing target-local evidence.

## Install In Claude Code

This repo is itself a Claude Code marketplace. Add it once, then install the plugin:

```bash
/plugin marketplace add codeyogi911/vision-product-loop
/plugin install vision-product-loop@vision-product-loop
```

The marketplace manifest lives at `.claude-plugin/marketplace.json` and points at `plugins/vision-product-loop/`, where the plugin's own `.claude-plugin/plugin.json` and `skills/` live.

## What It Does

- Establishes or refines a root `VISION.md`.
- Uses a bundled `grill-me` skill to collapse ambiguity before implementation.
- Establishes the knowledge map via the bundled `knowledge-map` skill: grills the user on every major architecture decision, records each as an ADR, sketches `ARCHITECTURE.md`, generates `CLAUDE.md` and `AGENTS.md` as ≤100-line maps, and scaffolds `docs/{adr,design-docs,exec-plans,references,generated}/` as the system of record.
- Discovers project docs, agents, architecture signals, and harnesses.
- Plans the shortest evidence path for the next product slice.
- Creates small project-local proof harnesses when none exist.
- Runs a Research, Build, Verify, Test, Reflect loop.
- Records operational state separately under `.vision-loop/`.
- Supports module visions for deep product or architecture areas.

## Repository Layout

```text
VISION.md                                       Product-level contract for this plugin
CONTEXT.md                                      Domain vocabulary used by the loop
visions/                                        Module vision contracts
plugins/vision-product-loop/                    Plugin implementation
plugins/vision-product-loop/.claude-plugin/     Claude Code plugin manifest
plugins/vision-product-loop/.codex-plugin/      Codex plugin manifest
plugins/vision-product-loop/skills/             Skills exposed by the plugin
plugins/vision-product-loop/scripts/            Deterministic helper scripts and harnesses
plugins/vision-product-loop/tests/              Regression tests for plugin helpers
.claude-plugin/marketplace.json                 Claude Code marketplace registration
.agents/plugins/marketplace.json                Codex local marketplace registration
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

Detect, scaffold, and lint the knowledge map:

```bash
python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root . --detect --json
python3 plugins/vision-product-loop/scripts/scaffold_knowledge_map.py --root . --apply
python3 plugins/vision-product-loop/scripts/lint_knowledge_map.py --root .
```

Run the toy project proof:

```bash
python3 plugins/vision-product-loop/scripts/run_toy_proof.py --target .vision-loop/toy-project
```

Record applied-project proof after using the plugin on a real target:

```text
.vision-loop/applied-proof.json
```

## Design Notes

The skill owns product judgment. Scripts provide deterministic mechanics for discovery, planning, validation, and state recording, but they should not decide product direction or hide the loop from the user.

Harnesses are evidence-producing capabilities, not a specific file type. A harness can be a command, skill workflow, evaluator, screenshot review, demo, benchmark, checklist, test, or project-specific workflow.

The loop-running orchestrator owns delegation judgment. When host capabilities and the autonomy boundary allow it, sub-agents can be used for independent slices, context management, parallel progress, independent verification, or clean task ownership.

## License

MIT
