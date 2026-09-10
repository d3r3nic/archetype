# Freshness and source authority

Framework-managed in downstream installations. Local AI must not edit this file; the next framework update overwrites it. Project-specific policies and live observations belong in the local task binding and knowledge records.

Follow [TASKS.md](TASKS.md). Never present a known outdated, invalidated, or unverifiable fact as current. Verification proves what a source reported at a recorded revision and time; it does not prove that an independent source can never change afterward.

## Identify what must be current

Distinguish immutable evidence from living facts. An old commit may remain valid historical evidence; today's deployment, permission, task priority, or product claim needs current verification. A new timestamp on a rewritten summary is not a new source observation.

Every action-dependent fact needs its authoritative source, observed revision, observation time, relevant scope, and an explicit invalidation or age policy. Derived context identifies the source revisions it covers. Framework version support is separate from factual freshness: a supported pinned rule release can remain valid while the task's source facts must refresh.

## Gate reads and actions

- Read canonical task state with its revision. Treat summaries, boards, and search indexes as derived views. They must expose source coverage; a newer source revision invalidates affected dependent context.
- At start, resume, and consequential action, verify the required fact set, claim, authorization, rule-version support, and budget. A known mismatch, expired observation, revoked version, or unverifiable prerequisite blocks that affected action until refreshed or resolved under policy.
- Block only dependent activity. Preserve access-controlled inspection of historical or unverified information with clear labels. Fresh independent work may continue.
- Use version-checked writes and an ownership fence where the source supports them. If state changes after preparation, reject the stale write and re-evaluate. Approval covers the reviewed action and evidence revision, not any later replacement action.
- Re-check external state immediately when its policy requires it. Use the provider's conditional operation when available. A preflight read alone cannot eliminate an external read/write race. Where the risk requires a guarantee the provider cannot supply, narrow the action or stop for resolution.

## Make updates durable

Persist the accepted task change and its required follow-up actions together. A failed publisher must leave durable pending work. Close only after required context publication acknowledges the expected source revision; do not let a late old publication replace a newer one.

Invalidation follows actual dependencies. Recompute affected summaries and retrieval views without rereading every project. Keep enough durable source and operation history to recover beyond transient delivery or stream retention. Never put required recovery state only in an agent conversation or a short-lived queue.

## Detect missed changes

Combine source events with scheduled reconciliation using saved cursors and overlapping lookbacks. Periodically verify broader coverage and access changes. A separately monitored heartbeat exposes failed reconciliation even if the worker loop has stopped. Direct source checks and failed-work recovery remain necessary when notifications are lost.

If the source is down, show when it was last verified and what is blocked. Do not reset the verification time merely because the poll ran or a cache was readable. If historical evidence cannot be recovered, retain an explicit gap rather than fabricating completeness.

## Required proof in the consuming system

Exercise stale task versions, expired authorization, old worker results, lost source events, publisher failure, a dead reconciler, revoked rules, and uncertain external outcomes. Show which operations are rejected, how the gap becomes visible, and how safe recovery resumes work. Static prompt or document checks do not prove these runtime guarantees.

The defensible goal is no silent acceptance of known stale or unverifiable prerequisites, with bounded detection of external change. Absolute zero staleness across independent systems is not a credible promise.
