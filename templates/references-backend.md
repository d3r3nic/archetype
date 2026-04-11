# References

## Project

Name: [project name]
Purpose: [one-line description]
Stage: [development / staging / production]
API URL: [base URL]

## Tech Stack

Runtime: [Node.js / Python / Go / C# / Java / etc.]
Framework: [Express / Fastify / SST / Django / FastAPI / ASP.NET / Spring Boot / Gin / Rails / etc.]
Language: [TypeScript / Python / Go / C# / Java / Ruby / Rust / etc.]
ORM/DB: [Prisma / SQLAlchemy / Django ORM / Entity Framework / GORM / ActiveRecord / Diesel / etc.]
Database: [PostgreSQL / MySQL / MongoDB / SQLite / SQL Server / etc.]
Validation: [Zod / Pydantic / FluentValidation / go-playground/validator / Bean Validation / etc.]
Cloud: [AWS / GCP / Azure / self-hosted / etc.]
Auth: [Cognito / Auth0 / ASP.NET Identity / Django auth / Firebase / custom JWT / etc.]
Testing: [Vitest / Jest / pytest / xUnit / go test / RSpec / etc.]
Package Manager: [npm / pnpm / pip / dotnet / go mod / bundler / cargo / etc.]

## Commands

```
dev:       [command to start dev server]
build:     [command to build]
test:      [command to run tests]
typecheck: [command to run type checker]
lint:      [command to lint]
deploy:    [command to deploy]
db:migrate:[command to run migrations]
db:studio: [command to open DB GUI]
logs:      [command to view logs]
```

## Foundational Systems

Each system is built once following convention #0 (Reusability). Features plug into these, never build ad-hoc. Sections ordered by scaffold build sequence.

### Git & Project Init (#2)
Commit convention: [e.g., conventional commits]
Branch strategy: [e.g., trunk-based]
Pre-commit hooks: [what runs - lint, format, typecheck]

### Project Structure & Types (#1, #7)
Folder structure: [see Folder Structure section below]
Path alias: [if applicable]
Type checking: [e.g., TypeScript strict, mypy strict, nullable reference types, etc.]
Validation library: [e.g., Zod, Pydantic, FluentValidation, go-playground/validator, etc.]
Shared types: [path to shared type definitions]

### Handler Pattern & Architecture (#3)
Pattern: [e.g., "Handler (thin) → Service (logic) → Data Access (ORM)"]
Handler location: [e.g., src/handlers/{feature}/]
Service location: [e.g., src/handlers/{feature}/services/]
Import rules: [features never import from other features]
Usage: [how new endpoints are structured]

### Error System (#8)
Location: [e.g., src/shared/errors/]
Error classes: [path to custom error definitions]
Error handling: [e.g., "framework wraps handlers, no try/catch needed"]
Usage: [how features throw errors]

### API Layer & Contract (#9, #10)
Response format: [e.g., "{ data, meta, errors } via responses.success()"]
Response utility: [path to response helpers]
Contract: [how types are shared with frontend - OpenAPI, tRPC, shared schemas]
Usage: [how handlers return responses]

### Auth System (#11)
Auth utility: [path]
Returns: [what it returns - database ID, not provider ID]
Authorization: [where auth checks happen - service layer, not handler]
CRITICAL: [production-learned auth rules]

### Database (#3)
ORM/Driver: [which one]
Schema: [path to schema]
Query builders: [path if any]
Migration commands: [how to run migrations]
Migration rules: [e.g., "never run destructive migrations without user approval"]
Usage: [how features access data]

### Validation (#7)
Schema location: [e.g., "handlers/{feature}/schemas"]
Shared primitives: [path to common validators]
Usage: [how handlers validate input]

### File Storage (#11)
Pattern: [e.g., "presigned URLs, 3-step: initiate → upload to S3 → verify"]
Location: [path to file service]
Usage: [how features handle file uploads]

### Testing Setup (#12, #18)
Test runner: [which one and command]
Test utilities: [path to shared factories, fixtures, mocks]
API mocking: [how API tests mock external services]
Verification commands: [exact commands - test, typecheck, build]
Coverage: [thresholds and enforcement]

### CI/CD (#15)
CI platform: [which one]
Pipeline: [sequence - lint → typecheck → test → build → deploy]
Deploy command: [how to deploy]
Rollback: [how to rollback]
Lint rules: [AI-targeted rules - no any, no console.log]

## Folder Structure

```
[paste actual folder structure here]

Example:
src/
├── handlers/           # Feature code (self-contained)
│   └── [feature]/
│       ├── [handler]       # Endpoint handler (thin entry point)
│       ├── schemas         # Validation schemas
│       ├── types           # Feature types
│       ├── services/       # Business logic
│       └── README.md       # Feature documentation
│
├── shared/             # Foundational systems
│   ├── auth/           # Auth utilities
│   ├── errors/         # Error classes
│   ├── responses/      # Response helpers
│   ├── validation/     # Schema primitives
│   └── db/             # Database access
│
└── config/             # App configuration
```

## Existing Patterns to Study

- [feature name]: [path] - [what it demonstrates]
- [feature name]: [path] - [what it demonstrates]

## Critical Lessons

- [lesson]: [what happened and the rule that prevents it]
- [lesson]: [what happened and the rule that prevents it]

## Convention Overrides

- [convention #]: [what's different and why]

## Project-Specific Documentation

For existing projects migrated to the framework, additional documentation locations:

### Convention Overrides (per-convention project rules)
- conventions/overrides/{N}-{name}.md - project-specific rules extending the base conventions

### Workflow Protocols
- protocols/{name}.md - workflow protocols beyond the base framework

### Reference Catalogs
- catalogs/{name}.md - reference materials for quick lookup

### Project-Specific Docs
- (List any links to existing project /docs/ that contain critical information)
