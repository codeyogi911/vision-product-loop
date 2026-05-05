# Vision

## Product Promise

One-line promise: Ops Room is Codex for e-commerce founders.

It is the supervised agentic operating layer that helps them run their commerce
business from one place without losing control.

## Product Thesis

E-commerce founders already have tools. They have Shopify, Amazon, inventory
systems, support desks, fulfillment workflows, spreadsheets, analytics, vendor
threads, and a growing pile of partial dashboards. The pain is not that founders
cannot decide. The pain is that making an informed operating decision requires
assembling fragmented, stale, and contradictory context by hand.

Ops Room exists to remove that evidence-gathering tax and turn founder intent
into real operating work. It watches the commerce stack, surfaces the Issues
that deserve attention, lets the founder and agent investigate together in an
operating thread, supports the founder's Decision, and executes approved Work
Orders through safe typed connectors.

The desired feeling is:

> I can finally operate the business from one place without losing control.

Ops Room is not another app in the stack. It is the agentic layer over the
stack.

## Users And Context

The first user is the founder/operator of a growing e-commerce brand with a lean
team, roughly in the $1M-$20M GMV range. They are still close enough to the
business that important operating calls bottleneck through them, but the stack
has become too fragmented to hold in their head.

V1 should be explicit about the first-class stack it understands deeply:

- Shopify for store and order context.
- Zoho Inventory for stock, purchase, and fulfillment context.
- Zoho Desk or support data for customer experience context.
- Amazon marketplace data for channel and account context.
- Company Intelligence for the business-specific memory that the raw systems do
  not know.

Marketing and ads are part of the long-term e-commerce operating boundary, but
they are not first-class v1 execution domains. V1 may reason about demand and
promotions from available data; direct ads and lifecycle-marketing actions can
come after the core operating loop is excellent.

## Jobs To Be Done

Ops Room should help founders complete operating jobs that are painful today
because the evidence, authority, and execution path are split across tools:

- Know what needs attention today without opening every system.
- Investigate a fuzzy operating concern until the real Issue is clear.
- Assemble decision-ready evidence from live systems and Company Intelligence.
- Decide with confidence because source freshness, missing context, risk, and
  alternatives are visible.
- Turn a Decision into an approved Work Order that can actually change the
  business.
- Draft supplier, customer, support, inventory, marketplace, and internal
  operations actions with the right context attached.
- Execute approved connector actions or produce exact human-executable steps
  when a connector cannot safely act.
- Monitor outcomes and teach the system what should change next time.

## Fragmented Commerce Work

The competitive enemy is fragmented, tool-centric operation. Founders are forced
to translate scattered dashboards, alerts, reports, tickets, stock tables,
marketplace warnings, and spreadsheets into coherent action.

Existing platform agents can be excellent inside their own surfaces. Shopify
Sidekick can help inside Shopify. Amazon Seller Assistant can help inside Seller
Central. Support and lifecycle tools can automate parts of customer
communication. Analytics tools can explain parts of performance. Ops Room's job
is different: cross-stack operating work for the founder.

Ops Room must reconcile partial truth across systems, name what is fresh or
stale, gather missing evidence when possible, and keep the founder in control
while real business work gets done.

## Operating Model

Ops Room is operating-work-first. It is not chat-first, dashboard-first, or
metrics-first. Chat is the collaboration surface; structured commerce objects
are the operating substrate beneath it.

The core flow is:

```text
Signals -> Issues -> Decisions -> Work Orders -> Outcomes -> Company Intelligence
```

- A **Signal** is a raw or normalized fact from a source system, connector,
  thread, document, or Company Intelligence.
- An **Issue** is a decision-worthy operating situation assembled from Signals
  and evidence. Issues include risks and opportunities.
- A **Decision** is the founder's judgment about what should happen.
- A **Work Order** is the execution package issued from a Decision. It contains
  the proposed business delta, approvals, draft actions, execution steps,
  evidence, risk, and rescue path.
- An **Outcome** is what happened after a Work Order was executed, monitored, or
  closed.
- **Company Intelligence** is the durable operating memory that improves future
  Issues and Work Orders.

The Daily Brief is the default morning ritual, not the whole product. It shows a
small ranked set of concise Issue cards with enough evidence to triage. Each
Issue can open a dedicated operating thread where the founder and agent explore,
clarify, decide, and act.

The founder can also start outbound work directly:

> "Handle the blue yoga mat stockout risk."
> "Investigate why Amazon sales dropped."
> "Improve our fulfillment process."
> "Draft the supplier escalation and tell me what evidence supports it."

For vague intent, Ops Room should inspect available business context first, then
grill the founder like a sharp operator until the shared mental model is clear.
It should ask focused questions, offer its recommended interpretation, and keep
updating the Issue or Work Order as the conversation progresses.

## Operating Threads

Every Issue or founder-started request should have an operating thread. The
thread is where collaboration happens, similar to how a software engineer works
with Codex on a task.

An operating thread should contain:

- The founder's intent and clarifications.
- The systems and sources the agent explored.
- The evidence gathered, including source freshness and missing context.
- The agent's recommendation and alternatives.
- The founder's Decision.
- The drafted or approved Work Order.
- The execution log, monitoring state, and outcome.
- Any durable learning proposed for Company Intelligence.

Anything relevant can enter the thread, but the thread must stay grounded in
commerce context, tools, evidence, Work Orders, and the Operating Ledger. The
anti-goal is not chat itself. The anti-goal is empty chatbot behavior detached
from real operating work.

## Work Orders And The Operating Ledger

Software agents have Git: branch, diff, test, review, merge, revert. Commerce
operations do not have a shared equivalent across Shopify, Zoho, Amazon,
support, vendors, customers, and marketplaces. Ops Room must provide that safety
primitive itself.

The **Operating Ledger** is the commerce replacement for Git's safety model.
Every meaningful agent run records:

- The business state and source snapshot used.
- The Issue being handled or founder intent being pursued.
- The evidence and Company Intelligence considered.
- The proposed business delta.
- The Work Order created from the Decision.
- The approval state and approver.
- The external actions executed.
- The outcome and monitoring result.
- The rescue path or compensating action when available.

The Codex analogy should guide the product:

| Codex | Ops Room |
| --- | --- |
| Repository | Commerce stack |
| Task thread | Operating thread |
| Branch or worktree | Work Order preparation space |
| Diff | Proposed business delta |
| Tests | Evidence checks, policy checks, and risk checks |
| Pull request review | Approval Gate |
| Merge | Execute approved Work Order |
| Revert | Rescue path or compensating action |
| Commit history | Operating Ledger |

## Autonomy And Approval

Ops Room should be useful before approval and powerful after approval.

The agent may automatically:

- Investigate live connectors and related sources.
- Refresh stale or partial evidence.
- Search Company Intelligence and prior Work Orders.
- Deduplicate already-handled Issues.
- Draft recommendations, messages, system changes, and Work Orders.
- Monitor open Issues and executed Work Orders.
- Suggest memory updates from founder corrections and outcomes.

External business changes require an approved Work Order. This includes
mutations to commerce systems, customer or vendor communication, marketplace
state, inventory records, product data, support records, ads, orders, refunds,
and finance-adjacent systems.

Ops Room may execute approved Work Orders through safe typed connectors. If a
connector cannot execute safely, Ops Room should prepare exact human-executable
steps and record the outcome. The important boundary is not that the agent never
acts. The boundary is that the agent never performs an external business action
without an approved Work Order.

For communication, the default rule is:

> Draft freely. Send only after approval.

Auto Mode may exist long term for narrow, founder-configured, low-risk workflows
with clear limits, logs, monitoring, and override controls. It is not a v1
promise and must not weaken the default approval-first trust model.

## Company Intelligence

Company Intelligence is Ops Room's living operating memory: the durable facts,
preferences, policies, relationships, exceptions, prior decisions, Work Orders,
and outcomes that help the agent understand how this specific e-commerce
business runs.

It includes:

- SKUs, bundles, vendors, channels, locations, customers, policies, and
  relationships.
- Vendor reliability, lead times, and exceptions.
- SKU quirks, margin constraints, and channel-specific rules.
- Founder preferences, approval habits, and operating policies.
- Customer promise rules and support expectations.
- Prior Issues, Decisions, Work Orders, outcomes, and suppressions.

It excludes raw connector dumps as permanent truth, unconfirmed guesses without
provenance, and transient one-off events unless they are promoted into durable
memory.

Every durable fact should carry provenance and trust state, such as `derived`,
`agent_suggested`, `confirmed`, or `taught`. The founder and agent jointly
curate Company Intelligence through typed, inspectable flows. The agent never
edits durable memory opaquely from model text alone.

Company Intelligence must change future behavior. It should reduce repeated
noise, improve recommendations, guide skills, and help Ops Room get more useful
as the founder corrects it.

## Domain Skills

The base agent gives leverage. Skills make it vertical.

Ops Room starts with inventory and fulfillment as the first proof skill, but the
product is not bounded by that wedge. New commerce domains become reliable
through explicit domain skills or playbooks. A skill should define:

- The job it helps the founder complete.
- The sources and connectors it needs.
- The evidence checklist.
- The risk model and freshness requirements.
- The Work Orders it is allowed to propose.
- The approval rules for external changes.
- The monitors that prove or falsify the outcome.
- The evals that protect the behavior.

Founders should not need to write technical skill files. They teach Ops Room
through corrections, preferences, policies, approved and rejected Work Orders,
and guided "teach the agent" flows. Advanced operators and partners may define
explicit playbooks, but the founder-facing path should remain conversational and
guided.

Skills should be lightly visible in the product. A founder should be able to see
when Ops Room is using a domain skill, what it checked, and what actions it is
allowed to propose.

## First Proof Skill

Inventory and fulfillment is the first domain where Ops Room must feel magical.
It naturally requires fragmented evidence: Shopify sales velocity, Zoho stock,
vendor lead times, Amazon exposure, open orders, support complaints, customer
promise risk, and Company Intelligence.

V1 should prove one complete loop:

1. Detect or accept an inventory/fulfillment Issue.
2. Gather live evidence and complete missing context where possible.
3. Open an operating thread for founder-agent collaboration.
4. Recommend the operating path and explain alternatives.
5. Support the founder's Decision.
6. Issue a Work Order with drafts, proposed deltas, approval requirements, and
   rescue path.
7. Execute supported connector actions after approval.
8. Monitor the outcome.
9. Learn from the result and founder correction.

This is the first proof that Ops Room can get commerce work done. It is not the
product boundary.

## Must-Have Capabilities

Ops Room must have these capabilities before the vision is credible:

- A home Operating Room with today's top Issues and an input for
  founder-directed work.
- Operating threads where the founder and agent collaborate with live commerce
  context.
- Connector-backed evidence gathering across the first-class v1 stack.
- Issue assembly from Signals, including risk, opportunity, source freshness,
  impact, and missing context.
- Work Orders with proposed deltas, drafts, approvals, execution state,
  monitoring, and rescue paths.
- An Operating Ledger that records state, evidence, approvals, actions, and
  outcomes.
- Company Intelligence with provenance, trust states, and behavior-changing
  retrieval.
- Domain skills that define evidence checklists, allowed Work Orders, approval
  rules, monitors, and evals.
- Local tests, fixtures, and evals that prove the operating loop without live
  commerce credentials.

## Experience Qualities

Ops Room should feel like a calm, sharp operator in the founder's corner:

- **Fast:** the founder can understand the day in minutes.
- **Grounded:** recommendations cite evidence and source freshness.
- **Opinionated:** the agent recommends a path instead of dumping metrics.
- **Controlled:** the founder sees what will change before anything external
  happens.
- **Useful:** the agent prepares or completes real work, not just commentary.
- **Extensible:** new commerce domains become excellent through skills and
  playbooks.
- **Quieting:** the system learns from corrections and suppresses repeated
  noise.
- **Serious:** the product feels like an operating console, not a decorative
  analytics toy.

## Non-Negotiables

- Founder control is sacred: visible state, visible reasoning, visible proposed
  deltas, approval before external change, execution records, outcome
  monitoring, and learning from correction.
- Operating-work-first: the product turns Signals into Issues, supports
  Decisions, and executes approved Work Orders.
- Evidence-led: Issues and Work Orders must cite evidence, source freshness, and
  missing context before risky recommendations.
- Imperfect data is normal. Ops Room should actively complete stale or partial
  evidence through connector refreshes, related-source exploration, Company
  Intelligence, and focused founder questions. If evidence remains incomplete,
  confidence must be lowered honestly.
- External writes and external communication remain behind the Approval Gate
  unless a future Auto Mode is explicitly configured for a narrow low-risk
  workflow.
- Company Intelligence must be provenanced, inspectable, and behavior-changing.
- Agent behavior must be inspectable through tools, skills, Work Orders, action
  plans, evidence trails, evals, and the Operating Ledger.
- The repo must preserve a no-hosted-API-key path: tests and fixtures stay cheap,
  while production-like local runs may use local commerce CLIs and local CLI
  agent auth until hosted APIs are worth wiring.
- UI changes must preserve the serious operating-console posture documented in
  `DESIGN.md`.

## Anti-Goals And Non-Goals

- A generic chatbot that answers anything but does not operate the business.
- A KPI dashboard that makes the founder interpret every signal manually.
- A single-source-of-truth fantasy that hides partial, stale, or failed source
  pulls behind confident language.
- A fully autonomous commerce executor that silently edits systems, sends
  messages, changes marketplace state, or spends money without approval.
- A task manager for the entire company.
- A personal assistant, generic strategy coach, HR tool, legal advisor, or broad
  accounting suite.
- Hidden prompt behavior that cannot be tested or explained.
- Durable memory that mixes connector facts, agent guesses, and founder-taught
  truth under one trust level.
- Decorative UI, noisy visual density, graph novelty, or metric mosaics that
  weaken operating clarity.
- Treating model improvement as the moat. Better models are a tailwind; the
  moat is the operating loop, connectors, skills, Company Intelligence,
  approvals, Work Orders, and the Operating Ledger.

## Success Measures

The project is moving toward the vision when founders can say:

- I know what matters today in under five minutes.
- I opened fewer tools to make the same operating call.
- The agent prepared or completed real work, not just commentary.
- I approved fewer, better Work Orders.
- I can see why the agent recommends something and what would change.
- The system remembered my business correctly.
- Repeated or already-handled Issues got quieter.
- Nothing important changed in my business without my approval.

Revenue, margin, and growth impact matter, but they are downstream of the core
promise: operational leverage without loss of control.

## Acceptance Checks

Ops Room satisfies this vision when:

- The home surface shows today's most important Issues and a way to start
  founder-directed work from intent.
- Daily Brief Issue cards are concise enough to triage, with evidence, source
  freshness, impact, and approval posture visible.
- Each Issue or founder-started request can open an operating thread grounded in
  live connector context, Company Intelligence, and structured work state.
- Vague founder intent triggers context inspection and focused grilling before
  confident recommendations.
- Inventory and fulfillment can complete the first proof loop from Issue
  detection to approved Work Order execution, outcome monitoring, and durable
  learning.
- Every Work Order includes the proposed business delta, evidence, source
  freshness, risk, approval requirements, and rescue path when available.
- External Shopify, Zoho, Amazon, support, communication, marketplace, order,
  refund, ad, or finance-adjacent writes never execute from model text alone;
  they execute only through approved Work Orders.
- Company Intelligence changes future behavior: prior feedback, SKU status,
  dismissals, learned policies, Work Orders, and outcomes are retrievable by the
  agent and can suppress repeated noise.
- Domain skills are explicit enough to inspect, evaluate, and extend without
  depending on model vibes.
- Local tests and fixtures can prove core behavior without hosted API keys or
  live commerce credentials.
- UI changes preserve the serious operating-console posture in `DESIGN.md`:
  operating-work-first, evidence-led, approval-aware, and not decorative or
  metrics-first.

## Open Questions

- What is the smallest useful Operating Ledger representation for v1?
- Which inventory and fulfillment Work Orders should be executable first, and
  which should remain human-executable instructions?
- What approval UX makes Work Orders feel as reviewable as a pull request
  without becoming engineering-flavored?
- Which Company Intelligence updates should be suggested automatically after a
  closed Work Order?
- What narrow workflows could eventually qualify for Auto Mode, and what limits
  would make them trustworthy?
- What partner or advanced-operator workflow should exist for creating new
  domain skills?

## Revision Model

This is a living product contract, not sacred text. Revisions should happen when
project reality, founder needs, or eval evidence show that the current vision is
incomplete or misleading.

Agents may propose revisions using the format in
`docs/vision-operating-loop.md`. Humans approve, reject, or edit those proposals.
Accepted changes should update this file and append the revision history.

## Revision History

- 2026-05-04: Reframed Ops Room as Codex for e-commerce founders and rewrote the
  vision around the operating-work loop: Signals -> Issues -> Decisions -> Work
  Orders -> Outcomes -> Company Intelligence. Added operating threads, Work
  Orders, the Operating Ledger, extensible domain skills, inventory/fulfillment
  as the first proof skill, and a clearer approval/autonomy model.
- 2026-05-04: Promoted Company Intelligence to a first-class Operator surface
  with explicit per-entity / per-relationship provenance, joint
  Operator-and-agent curation through a typed surface, and anti-goals against
  mixed-trust knowledge surfaces and decorative graph rendering. Drives the
  Intelligence Graph v1 slice in `docs/intelligence-graph-v1-plan.md`.
- 2026-05-04: Added explicit acceptance checks as hard product gates for the
  vision loop, while keeping enforcement evidence-oriented rather than CI-hard.
- 2026-05-03: Initial baseline for the repo-first vision operating system.
