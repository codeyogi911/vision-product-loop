---
name: vision-product-loop
description: Drive a product from VISION.md to shipped reality through a Research-Build-Verify-Test-Reflect operating loop, treating VISION.md as the durable contract and project-local harnesses as evidence. Use when the user wants to create, define, grill, implement, or iterate on a product from a vision; compare a repository against a vision; or coordinate agents, sub-agents, harnesses, tests, and acceptance criteria until the product matches the agreed goal.
---

# Vision Product Loop

## Purpose

Turn a product vision into working software end to end. Treat `VISION.md` as the durable product contract, grill the user until intent is crisp, establish the knowledge map, then iterate Research-Build-Verify-Test-Reflect cycles until the observed product satisfies the contract.

Stack-agnostic. Discover or create whatever project-local harnesses, skills, scripts, and checks the goal needs.

## Core Principles

- `VISION.md` is the source of truth for product intent.
- Use the repo's own language, docs, agents, and validation tools before inventing process.
- Grill only until the work is crisp enough to act; alignment is not ceremony.
- Change implementation freely when the vision demands; change the vision only with user agreement.
- Ground every loop in evidence: tests, screenshots, demos, logs, acceptance checks, code inspection.
- Plan as Sprint → Task → Subtasks → Task-end validation → Reflection.
- Pick the highest-uncertainty, highest-leverage gap that can be proven with task-end validation.
- Treat a harness as an evidence-producing capability, not a file type.
- Keep harnesses immutable inside the task whose evidence they produce; harness changes belong in their own tasks.
- Declare progress indicators and a target direction before Build, snapshot a baseline, snapshot a result at Reflect, emit `kept`, `reverted`, or `pending` with a recorded reason.
- Self-check and toy proof are bootstrap evidence only; this plugin's completion also requires applied-project proof from a real external target.
- Use module visions for Deep Modules whose Interface, Implementation, Seam, Adapter, Leverage, or Locality needs deeper thought than the root contract.
- Stop only when the vision is satisfied, the user changes direction, or a concrete blocker remains.
- Stop and ask before changing the product promise, deleting user-authored work, adding network-dependent tools, publishing or installing marketplace entries, or making destructive filesystem or git changes.

## Workflow Checklist

1. **Find or establish the vision** — find `VISION.md` or draft the smallest useful form and confirm.
2. **Grill** — invoke the bundled `grill-me` skill (`skills/grill-me/SKILL.md`) one question at a time; update `VISION.md` as branches resolve.
3. **Establish the knowledge map** — invoke the bundled `knowledge-map` skill (`skills/knowledge-map/SKILL.md`) to grill on architecture decisions, record ADRs, sketch `ARCHITECTURE.md`, and scaffold `docs/`.
4. **Split into module visions** — when a Deep Module needs its own contract, write `visions/<module-id>.md`.
5. **Plan Sprint/Task/Subtasks** — `python3 plugins/vision-product-loop/scripts/plan_work.py --root <target> --json`.
6. **Run the operating loop** — Research, Build (with baseline + indicators), Verify, Test, Reflect (with result + decision). Use `scripts/run_loop.py` for the safe automated batch.
7. **Discover the project control plane** — agent files, domain docs, architecture, harnesses, workflow.
8. **Build the iteration plan** — map vision to tasks; pick the highest-leverage task with task-end validation.
9. **Iterate until reality matches vision** — repeat the loop with evidence at task close.
10. **Run batch loops** — once the autonomy boundary is clear, do not require user approval per slice.
11. **Keep machine loop state** — `.vision-loop/state.json` holds operational state with `baseline`, `result`, `target_indicators`, and `task_history`.
12. **Use the self-check harness** — `python3 plugins/vision-product-loop/scripts/self_check.py --json` reports gaps until applied-project proof is recorded.

See [REFERENCE.md](REFERENCE.md) for the full step-by-step detail behind each item, including the `state.json` schema, the harness immutability rule, the indicator-and-decision ledger, and applied-project-proof requirements.

## Done Criteria

The loop is complete when:

- `VISION.md` has no unresolved must-have acceptance gaps.
- The repo-local validation harness passes, or any failures are clearly unrelated and reported.
- If the product is this plugin, applied-project proof exists from a real target outside this repository.
- The final response names what changed, what evidence was run, and any residual risk.
- The product can be demonstrated or inspected in the form the user cares about.
