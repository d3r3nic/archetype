# Frontend scaffold: long-running operation streams

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 10c: Long-running operation streams
Read: #9; scaffolding/_preamble.md § Convention-mapping rule
Produces: the operation registry and the stream that replays its tail to a late subscriber
Check: run project: typecheck, lint, test, build; evidence: what was seen when this was tried: two clients watching one operation, and a reload mid-operation
Skip when: the product has no operation that runs for seconds to minutes

An operation that takes seconds to minutes (a deploy, a build, an import) is watched through a stream the client can resubscribe to, not one request that waits:
- A registry keyed by the operation's target holds active and recently finished operations.
- The registry keeps each operation's events as they happen, so a late subscriber replays the tail.
- The stream subscribes to the registry; several clients can watch one operation, and a reload reconnects.
- Finished operations are cleaned up after a window long enough for a late reload to see the final state.

The same shape serves processes the product starts and work it runs in-process.

**Verify:** two clients watch one operation and see the same events; a reload mid-operation reconnects and shows everything so far.
