# Backend Rules

These supplement the universal rules in the root CLAUDE.md. Read both.

Scan backend/Conventions.md for which backend conventions apply to your current task.

## Enforcement

- Never run destructive database operations (DROP, DELETE all, ALTER column type) without explicit approval. → backend/conventions/B1-database.md
- Never create database connections per request. Use the connection pool. → backend/conventions/B1-database.md
- Never fetch related data inside a loop. Use batch queries, joins, or includes. → backend/conventions/B1-database.md
- Never auto-run migrations in production. Migrations require human approval. → backend/conventions/B1-database.md
- Never wrap multiple related writes without a transaction. → backend/conventions/B1-database.md
- Never use console.log or print. Use the structured logging system. → backend/conventions/B4-logging.md
- Never log passwords, tokens, API keys, or PII. → backend/conventions/B4-logging.md
- Never do synchronous work over 2 seconds in a request handler. Queue it. → backend/conventions/B5-background-jobs.md
- Never trust client Content-Type headers for file validation. Check magic bytes server-side. → backend/conventions/B6-file-handling.md
- Never return raw arrays from API endpoints. Use the response envelope. → backend/conventions/B2-api-design.md
- Never proxy file uploads through the server. Use presigned URLs. → backend/conventions/B6-file-handling.md
