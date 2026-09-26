# Backend work

Read the root AGENTS.md and use backend/Conventions.md to locate the concerns relevant to the task. Inspect existing contracts and current runtime evidence before selecting or changing database access, request handling, uploads, caching or background work.

The backend conventions hold the standard firm: one owner per concern (one connection pool, one validation at the boundary, one error mapping, one job runner, one storage service), one response format, safe boundaries and effort sized to real usage. Each says when it applies by how this service works; the form, such as the response shape, the paging method, the pipeline order or the job threshold, is the project's recorded choice. Record it in References.md, what only an owner may use in § Boundaries, and the reason at the decision location.

Protect secrets and personal data, validate untrusted input at the correct boundary, keep related writes atomic, and prevent cross-user and cross-tenant access. Destructive database actions, production changes and external commitments follow the recorded authority and permission boundaries. Verify the safety and behavior promised; an architectural choice never excuses a failed required check.

For backend work outside a playbook's steps, use development/TASKS.md to keep the sequence, dependencies, evidence and next action in the implementer plan.
