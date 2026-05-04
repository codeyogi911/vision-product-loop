# Intelligence Layer Vision

Parent vision: [`../VISION.md`](../VISION.md)

Status: research module vision

## Module Promise

The Intelligence Layer is a deep Module that helps an agent reason from a product vision to good next actions. It should make the agent better at interpreting intent, comparing options, selecting the next slice, judging evidence, and adapting when the current loop is not closing the gap.

## Interface

The Interface should be small and durable: given a product vision, project context, evidence, and unresolved gaps, the Module returns the next recommended move, the reason for that move, the proof harness to run, and the stop condition that should govern the loop.

## Implementation Options

The Implementation is intentionally open while research continues. Candidate paths may include prompt-only reasoning, rubric-driven scoring, retrieval over project memory, evaluator-backed option ranking, planner/verifier separation, or a hybrid. The module vision should preserve these options until evidence shows which shape gives the best Leverage without harming Locality.

## Depth

The Module should be Deep: callers should not need to know which reasoning method, model prompt, ranking strategy, or evaluator produced the recommendation. The Interface should stay stable while the Implementation can improve.

## Seam And Adapter

The main Seam is between the product loop and the agent's decision logic. Adapters may be needed for model providers, evaluation harnesses, project memory, issue trackers, or local agent runtimes.

## Leverage

The Intelligence Layer has high Leverage when one improvement to the Module makes many product loops better: better slice selection, better research decisions, better harness choice, clearer stop reasons, and fewer loops that pass tests while missing the vision.

## Locality

Changes to prompts, scoring rubrics, evaluators, or model-specific Adapters should stay local to the Intelligence Layer. Product code, harness code, and user-facing vision artifacts should not need broad edits when the internal reasoning Implementation changes.

## Acceptance Checks

- Given a broad product vision, the Module can split the work into root-level and module-level visions without losing the parent product promise.
- Given competing research options, the Module keeps options explicit and chooses the next evidence-gathering slice rather than prematurely hard-coding a favorite.
- Given project evidence, the Module recommends a next action, proof harness, and stop condition that can be inspected by the user.
- Given a changed Implementation, the Interface contract remains stable.

## Open Questions

- Which Intelligence Layer Interface is smallest while still useful for real agent work?
- Which harness best proves that the Module chooses better next slices than a flat checklist?
- What evidence is strong enough to select among prompt-only, rubric, evaluator, retrieval, or hybrid Implementations?
