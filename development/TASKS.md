# Task rules

Framework-managed in downstream installations. Local AI must not edit this file; the next framework update overwrites it. Tailor the project through References.md, and through protocols/task-context.md when it runs a task service. Propose shared rule changes upstream (development/FEEDBACK.md).

This file has two parts. Every project uses the first: how to carry work that no playbook steps through, and three rules about facts, completion and uncertain outcomes. The second applies only when the project runs a task service, a canonical task system with ownership, publication and freshness, recorded in protocols/task-context.md; such a project also reads [FRESHNESS.md](FRESHNESS.md). Local guidance selects scope and capabilities; it cannot broaden runtime permissions or override the active instruction hierarchy.

## Work outside a playbook's steps (every project)

For a workflow with no declared step route, the implementer carries sequencing in the project's plan: the canonical task or project plan when the project runs a task service (below), otherwise the planning file the project keeps. Reuse its scope and acceptance record; do not create a parallel tracker or another decision store. A small change can be one item.

- Name the intended result of each coherent step, the inputs and relevant guidance it needs, prerequisites or affected decision references, the check that establishes completion, and its actual state. Use the existing task system's fields or concise plan text; no new schema is required.
- Work in dependency order. At a useful boundary, run the applicable checks and link their evidence. Record the next action and unresolved conditions so another session can resume. Keep partial work visibly incomplete.
- When a requirement, decision or input changes, preserve its history at the existing decision location. Inspect direct and downstream dependants, mark affected plan items stale, and repeat the necessary work and checks before closing them. Retain unaffected work with a reason. This review is manual; dependency tags alone do not perform invalidation.
- If affected work also has declared step-ledger records, use development/STEPS.md to reopen those records as well. Do not write invented close/reopen events, silently skip a required declared step, or replace a failed gate with a plan checkbox. An unconverted task is not an excuse to abandon a declared route whose checks failed.

Completing the routes listed in PROGRESS.md establishes only their recorded scope. Check the task's acceptance conditions and remaining phase work before claiming the project complete. Automated integration belongs to a separately scoped framework task when resourced; an implementer can use this procedure now without converting the framework. An unavailable connected task service still follows the authority rule of the second part, not an offline duplicate.

## Rules for every project

- Never present a known outdated, invalidated or unverifiable fact as current (FRESHNESS.md says more for projects that run a task service).
- Never mark work done because the session stopped or a tool call returned; check its outcome first.
- For an outside call whose result is uncertain, ask the destination what happened before retrying, so an effect is never duplicated blindly.

## When the project runs a task service

Use this part for tracked development, research, marketing and operations in a project whose protocols/task-context.md names a task service.

### Establish authority

- Identify the one canonical task source before work. If the platform is not connected yet, use the explicitly declared project planning source. If a connected platform is unavailable, pause dependent actions; do not create an offline second tracker or mark work complete locally.
- Resolve workspace, project, repository, and task identity through the authorized source. Validate explicit links. A possible similarity match is a suggestion, not authority to close or merge work.
- Check for existing work before creating a task or project. Previously completed external work becomes a retrospective record and is never dispatched as a new assignment. A project represents an outcome, not each individual change.

### Prepare and execute

- Record the intended outcome, acceptance evidence, dependencies, affected scope, allowed actions, and execution budget. Claim the task through the available ownership mechanism before changing shared work. In a local planning phase, an isolated branch/worktree and a recorded task assignment establish the handoff; do not invent a remote lease.
- Load relevant shared rules, department guidance, local context, and source evidence. Record their revisions. Do not load every repository or assume the previous conversation remains authoritative.
- Use the verified platform capabilities declared in the task binding. Never invent endpoints, commands, credentials, or tool results. Adapter details and exact state names belong to project documentation, not this rulebook.
- Keep runs bounded. Re-check task ownership, cancellation, permissions, budget, and changed prerequisites before consequential actions and resumed work. A retry is subject to the same checks as its first attempt.
- Follow the project's implementation and review process. Use task branches/worktrees for code changes and stable artifact references for other work. Record partial outcomes and blockers honestly.

### Verify, record, and close

- Verify the task's outcome using authoritative evidence. Drafted, reviewed, merged, released, published, and measured are distinct facts. Significant deliverables require independent review under the project policy; an author cannot supply their own independent verdict.
- Submit the result, evidence, review, and durable knowledge changes together through the canonical task interface. If no knowledge change is needed, record that finding rather than adding empty log files.
- Required context publication must be acknowledged before final task closure. A failed write remains pending and recoverable. Never mark a task done because the agent stopped or a tool call returned without checking its outcome.
- Preserve action identifiers and source revisions. For an external call with an uncertain result, query the destination before retrying. If safe recovery is unavailable, expose uncertainty and request the concrete decision needed; do not duplicate external effects blindly.
- A revert, rejection, or changed outcome adds corrective history and reopens or blocks affected work when warranted. It does not erase earlier evidence.

### Handoff and maintenance

- Persist enough context for a new worker to continue: current task state, decisions, artifacts, verification, and the next bounded action. Summaries link to evidence rather than replacing it.
- Cross-department handoffs transfer only authorized facts. Follow-up tasks need a reason, a duplicate check, and a budget. Recurring work needs an end or review condition.
- Archive completed activity from normal working views; keep current knowledge concise. Repeated corrections may propose central improvements, but cannot change the worker's own rules or permissions.
- Resolve conflicts through the canonical source and recorded versions. Do not silently merge contradictory facts or move a stuck task to done to clean the board.

For code implementation, continue through [DEVELOP.md](DEVELOP.md); for broader maintenance, use [MAINTAIN.md](MAINTAIN.md). Instruction text guides behavior. The consuming system must implement the enforcement, persistence, and recovery described by its task contract.
