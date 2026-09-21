# Backend work

Read the root AGENTS.md and use backend/Conventions.md to locate the concerns relevant to the task. Inspect existing contracts and current runtime evidence before selecting or changing database access, request handling, uploads, caching or background work.

Preserve the project's accepted architecture and record consequential changes at its existing decision location. Shared examples do not settle the project's response shape, queue threshold, connection strategy or middleware boundaries. Evaluate their applicability under the root judgment guidance and record justified convention choices in the existing overrides location.

Protect secrets and personal data, validate untrusted inputs at the correct boundary, preserve atomicity where related writes require it, and prevent cross-user or cross-tenant access. Destructive database actions, production changes and external commitments follow the recorded authority and permission boundaries. Verify the actual safety and behavior promised; an architectural choice never excuses a failed required check.

For unconverted backend work, use development/TASKS.md to keep the sequence, dependencies, evidence and next action in the existing implementer plan. This entry routes work; it does not claim every backend pattern or runtime is automatically supported.
