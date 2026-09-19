# Frontend scaffold: long-running operation streams

Part of the frontend scaffold playbook (scaffolding/SCAFFOLD-FRONTEND.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step. Before building, read the conventions it names and write how the system will be built in its References.md section (scaffolding/_preamble.md); when it lands, update its feature-tree.md row and its docs/systems/ page.

## Step 10c: Long-running operation streams
Read: #9; scaffolding/_preamble.md § Convention-mapping rule
Produces: the operation registry and the stream that replays its tail to a late subscriber
Check: run project: typecheck, lint, test, build; evidence: what was seen when this was tried: two clients watching one operation, and a reload mid-operation
Skip when: the product has no operation that runs for seconds to minutes

For any operation that takes seconds-to-minutes (deploy, build, teardown, import), build a subprocess/job registry + SSE stream pattern rather than one-shot HTTP:

- A **registry** keyed by the operation target (slug, job id, etc.) holds active and recently-completed operations.
- The registry stores events as they happen, so a late subscriber can **replay** the tail.
- SSE endpoints subscribe to the registry; multiple clients can watch the same operation (reload-resilient).
- Finished operations TTL-cleanup after a window so subscribers who reload late still see the final state.

Applies equally to shell subprocesses and async in-process jobs.
