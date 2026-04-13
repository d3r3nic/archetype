# Convention B5: Background Jobs & Queues

## Principle

Any operation that takes more than 1-2 seconds or depends on external services that can fail should not run inside the request handler. It belongs in a background job queue. Email sending, PDF generation, image processing, webhook delivery, data imports, and external API calls should all be asynchronous. The request handler queues the job and returns immediately. This isolates the API from downstream failures and prevents request timeouts.

## Reusable System

Create a job processing foundation that establishes:
- A job queue (message broker or job library) configured and connected
- Job handlers that are idempotent (same job processed twice produces same result)
- Retry logic with exponential backoff, jitter, and maximum retries
- Dead letter queue for jobs that exhaust retries
- Monitoring for queue depth and job processing rate

## Rules

- Never do synchronous work over 1-2 seconds in a request handler. Email, PDF, image processing, external API calls, data imports — all must be queued as background jobs.
- Every job handler must be idempotent. If the same job runs twice, the result is identical. Check state before acting (was the email already sent? was the payment already processed?). Use idempotency keys to detect duplicates.
- Use exponential backoff with jitter for retries: 2s, 4s, 8s, 16s, 32s. Set a maximum retry count (3-5). After exhausting retries, route to a dead letter queue. Monitor dead letter queue depth.
- Keep job payloads small. Store large data in object storage and put the key in the job. Never embed large files or datasets in the job payload.
- Run workers as separate processes from API servers. They scale independently and an overloaded worker does not slow down the API.

## Violations

- Request handler sends an email synchronously. If the email service is slow, the HTTP request hangs for 30 seconds. If the email service is down, the request fails even though the user's action (creating an account) succeeded.
- Job handler sends a notification without checking if it was already sent. The job retries due to a network blip. User receives two notifications.
- Retry loop with a fixed 1-second delay and no maximum. A failing job retries infinitely, consuming worker capacity.
- Job payload contains a 50MB CSV file. Queue memory spikes. Workers download 50MB per job from the queue.

## Wrong vs Right

- WRONG: user signs up → handler creates user → sends welcome email → sends Slack notification → returns response. If email service is slow, user waits. If it fails, signup fails even though user was created.
- RIGHT: user signs up → handler creates user → queues "send welcome email" job → queues "send Slack notification" job → returns response immediately. Jobs process in background with their own retry logic.
- WRONG: job handler processes payment. Job fails due to timeout. Job retries. Payment processes twice. Customer charged twice.
- RIGHT: job handler checks idempotency key (or checks payment status in database) before processing. Second execution detects the payment was already made and exits cleanly.

## Research Notes

When bootstrapping this convention:
- Research job queue options for the framework (BullMQ for Node, Celery for Python, Hangfire for .NET, Asynq for Go).
- Research the queue's retry and dead letter patterns.
- Research idempotency key patterns for the framework.
- Research worker process isolation (separate deployment from API, independent scaling).
- Document the queue setup, job naming conventions, retry configuration, and dead letter monitoring in References.md.
