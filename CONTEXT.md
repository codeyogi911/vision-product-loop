# Context

## Domain Terms

### Vision Product Loop

A product-building loop that starts from a durable `VISION.md`, grills unclear intent until the goal is crisp, discovers the project's existing tools, then iterates with evidence until reality matches the vision.

### Module Vision

A durable vision artifact for one deep Module inside a larger product vision. A module vision names the Module promise, the Interface callers should rely on, the Implementation choices hidden behind that Interface, the intended Depth, the Seam where the Module joins the rest of the product, any Adapter needed for outside tools or models, the expected Leverage, the intended Locality, and the harnesses that prove progress.

### Intelligence Layer

A research-heavy Module for an agent or product that decides how context is interpreted, how options are compared, how actions are chosen, how evidence is judged, and how the loop adapts. Its module vision should keep competing Implementation options visible until harness evidence selects the Interface, Seam, Adapter, Depth, Leverage, and Locality that best realize the product vision.

### Operating Loop

The repeatable engine that moves a project from vision to realized product. Its phases are Research, Build, Verify, Test, and Reflect. The loop should resume from durable artifacts when the user returns, continue within the autonomy boundary, and stop only when the vision is satisfied, the task or sprint budget is exhausted, or the next action needs the user.

### Sprint Task Planning

The applied planning shape for real repositories. A Sprint is the short planning container, a Task is the coherent product outcome that owns broad validation, and Subtasks are bounded implementation steps inside the task. The default test cadence is task-end validation: subtasks use inspection or focused probes, while broad test, typecheck, browser, and eval harnesses run once at task close unless risk demands earlier validation.

### Knowledge Map

The project's `docs/` directory treated as the system of record, with `CLAUDE.md` and `AGENTS.md` as small (≤100 lines) tables of contents pointing at deeper sources of truth (`ARCHITECTURE.md`, `docs/adr/`, `docs/design-docs/`, `docs/exec-plans/`, `docs/references/`, `docs/generated/`). Map files should not become encyclopedias. The bundled `knowledge-map` skill establishes this layout, grills the user on architecture decisions, and records each as an ADR.

### Exec Plan

A first-class durable plan for one task that has more than one subtask. Lives under `docs/exec-plans/active/<slug>.md` while the task is running and moves to `docs/exec-plans/completed/<slug>.md` when the task closes with passing evidence. Pairs with `.vision-loop/state.json` so machines and humans share a view of work.

### Reference Doc

A third-party reference (API doc, tool doc, llms.txt copy) checked into `docs/references/` so the agent does not depend on external network calls during the loop.

### Design Doc

A longer-form design discussion under `docs/design-docs/` that explores a Module or area too richly for an ADR but that has not yet collapsed into a single decision.

### Generated Doc

A doc under `docs/generated/` produced by tooling (db schema, API surface, type signatures) that should be regenerated rather than hand-edited.

### Harness

An evidence-producing capability used by the loop to prove or falsify progress against the vision. A harness may be a command, skill workflow, evaluator, screenshot review, demo, benchmark, checklist, test, or project-specific workflow. Files are only Implementations or Adapters behind the harness Interface.
