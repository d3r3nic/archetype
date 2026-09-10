# Global task rulebook

Framework-managed in downstream installations. Local AI must not edit this file; the next framework update overwrites it. Tailor the project through protocols/task-context.md and References.md. Propose shared rule changes upstream.

Use this workflow for tracked development, research, marketing, and operations. Read [FRESHNESS.md](FRESHNESS.md) and the project-root task binding. Local guidance selects scope and capabilities; it cannot broaden runtime permissions or override the active instruction hierarchy.

## Establish authority

- Identify the one canonical task source before work. If the platform is not connected yet, use the explicitly declared project planning source. If a connected platform is unavailable, pause dependent actions; do not create an offline second tracker or mark work complete locally.
- Resolve workspace, project, repository, and task identity through the authorized source. Validate explicit links. A possible similarity match is a suggestion, not authority to close or merge work.
- Check for existing work before creating a task or project. Previously completed external work becomes a retrospective record and is never dispatched as a new assignment. A project represents an outcome, not each individual change.

## Prepare and execute

- Record the intended outcome, acceptance evidence, dependencies, affected scope, allowed actions, and execution budget. Claim the task through the available ownership mechanism before changing shared work. In a local planning phase, an isolated branch/worktree and a recorded task assignment establish the handoff; do not invent a remote lease.
- Load relevant shared rules, department guidance, local context, and source evidence. Record their revisions. Do not load every repository or assume the previous conversation remains authoritative.
- Use the verified platform capabilities declared in the task binding. Never invent endpoints, commands, credentials, or tool results. Adapter details and exact state names belong to project documentation, not this rulebook.
- Keep runs bounded. Re-check task ownership, cancellation, permissions, budget, and changed prerequisites before consequential actions and resumed work. A retry is subject to the same checks as its first attempt.
- Follow the project's implementation and review process. Use task branches/worktrees for code changes and stable artifact references for other work. Record partial outcomes and blockers honestly.

## Verify, record, and close

- Verify the task's outcome using authoritative evidence. Drafted, reviewed, merged, released, published, and measured are distinct facts. Significant deliverables require independent review under the project policy; an author cannot supply their own independent verdict.
- Submit the result, evidence, review, and durable knowledge changes together through the canonical task interface. If no knowledge change is needed, record that finding rather than adding empty log files.
- Required context publication must be acknowledged before final task closure. A failed write remains pending and recoverable. Never mark a task done because the agent stopped or a tool call returned without checking its outcome.
- Preserve action identifiers and source revisions. For an external call with an uncertain result, query the destination before retrying. If safe recovery is unavailable, expose uncertainty and request the concrete decision needed; do not duplicate external effects blindly.
- A revert, rejection, or changed outcome adds corrective history and reopens or blocks affected work when warranted. It does not erase earlier evidence.

## Handoff and maintenance

- Persist enough context for a new worker to continue: current task state, decisions, artifacts, verification, and the next bounded action. Summaries link to evidence rather than replacing it.
- Cross-department handoffs transfer only authorized facts. Follow-up tasks need a reason, a duplicate check, and a budget. Recurring work needs an end or review condition.
- Archive completed activity from normal working views; keep current knowledge concise. Repeated corrections may propose central improvements, but cannot change the worker's own rules or permissions.
- Resolve conflicts through the canonical source and recorded versions. Do not silently merge contradictory facts or move a stuck task to done to clean the board.

For code implementation, continue through [DEVELOP.md](DEVELOP.md); for broader maintenance, use [MAINTAIN.md](MAINTAIN.md). Instruction text guides behavior. The consuming system must implement the enforcement, persistence, and recovery described by its task contract.
