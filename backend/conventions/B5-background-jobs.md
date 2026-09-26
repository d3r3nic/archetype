# Convention B5: Background Jobs & Queues

## Applies when

The service does work that people should not wait for, or that depends on something that can fail or stall: sending messages, generating documents, processing media, calling outside services, importing data, running scheduled work. What varies is how much of it there is and how much people rely on it (#30). A small tool may run such work inline or on a simple schedule and record why.

## Principle

Work that should not hold a request runs outside it, through one job runner, and every job can run twice without doing harm. Retries are bounded, failures are kept for inspection and reported, and the machinery is sized to the real volume: a queue and separate workers when volume or reliability calls for them, something simpler when it does not.

## Reusable System

The job foundation: the one runner (a queue, a scheduler, or both), the job handlers, the retry policy, the place failed jobs are kept, and the monitoring the reliance calls for. References.md records the runner, the naming of jobs, the retry policy, the threshold for moving work out of a request and why, and where failures go.

## Rules

- Decide once, and record, which work leaves the request: by how long it takes, whether it depends on something that can fail, and what the person needs to see before the response. Apply the rule consistently.
- Make every handler idempotent: check state before acting, or use an idempotency key, so a retry or a duplicate delivery cannot send, charge or create twice.
- Retry with a growing delay and jitter, up to a limit. After the last attempt keep the job for inspection and make the failure visible.
- Keep payloads small: store large data elsewhere and pass its key.
- Run workers apart from the request-serving processes when load or reliability calls for independent scaling or failure.

## Violations

- A request that waits on a slow outside service, and fails although the person's action succeeded.
- A handler that sends or charges without checking whether it already did.
- Retries with no limit, or failures that vanish.
- A large file carried inside a job payload.

## Wrong vs Right

- WRONG: sign-up creates the account, sends the welcome message and posts a notification before responding; a slow message service makes sign-up slow, and a down one makes it fail. RIGHT: sign-up creates the account, queues the two jobs and responds; the jobs retry on their own.
- WRONG: a payment job times out and is retried, and the customer is charged twice. RIGHT: the job checks the payment's state or its idempotency key first, and the retry exits cleanly.

## Research Notes

Research the job runners that fit the chosen stack and the real volume, their retry and failed-job handling, idempotency-key patterns, and how workers are deployed and scaled on the chosen hosting. Record the runner, the threshold, the retry policy and the failure handling in References.md.
