# References

## Project

Name: [project name]
Purpose: [one-line description]
Stage: [development / staging / production]
API URL: [base URL]

## Tech Stack

Runtime: [Node.js / Python / Go / C# / Java / etc.]
Framework: [Express / Fastify / SST / Serverless / Django / etc.]
Language: [TypeScript / Python / Go / etc.]
ORM/DB: [Prisma / TypeORM / Drizzle / SQLAlchemy / etc.]
Database: [PostgreSQL / MySQL / MongoDB / etc.]
Validation: [Zod / Joi / etc.]
Cloud: [AWS / GCP / Azure / etc.]
Auth: [Cognito / Auth0 / Firebase / custom JWT / etc.]
Testing: [Vitest / Jest / pytest / etc.]
Package Manager: [npm / pnpm / pip / go mod / etc.]

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

Each system is built once following convention #0 (Reusability). Features plug into these, never build ad-hoc.

### Handler Pattern (#3)
Pattern: [e.g., "Handler (thin) → Service (logic) → Data Access (ORM)"]
Handler location: [e.g., src/handlers/{feature}/]
Service location: [e.g., src/handlers/{feature}/services/]
Usage: [how new endpoints are structured]

### Error System (#8)
Location: [e.g., src/shared/errors/]
Error classes: [path to custom error definitions]
Error handling: [e.g., "framework wraps handlers, no try/catch needed"]
Usage: [how features throw errors, e.g., "throw new ValidationError(message)"]

### API Layer (#9)
Response format: [e.g., "{ data, meta, errors } via responses.success()"]
Response utility: [path to response helpers]
Usage: [how handlers return responses]

### Auth System (#11)
Auth utility: [path, e.g., "getAuthenticatedUser(event)"]
Returns: [what it returns, e.g., "{ cognitoSub, userId } where userId is DB UUID"]
Authorization: [where auth checks happen, e.g., "service layer, not handler"]
CRITICAL: [any production-learned auth rules]

### Validation (#7)
Schema location: [e.g., "handlers/{feature}/schemas.ts"]
Shared primitives: [path, e.g., "shared/validation/ (safeString, emailSchema)"]
Usage: [e.g., "const data = validateRequest(event.body, schema)"]

### Database (#3)
Schema: [path to schema, e.g., "prisma/schema.prisma"]
Query builders: [path if any]
Migration rules: [e.g., "never run migrations without user approval"]
Usage: [how features access data]

### File Storage (#11)
Pattern: [e.g., "presigned URLs, 3-step: initiate → upload to S3 → verify"]
Location: [path to file service]
Usage: [how features handle file uploads]

## Folder Structure

```
[paste actual folder structure here]

Example:
src/
├── handlers/           # Feature code (self-contained)
│   └── [feature]/
│       ├── [handler].ts    # Lambda/endpoint handler
│       ├── schemas.ts      # Zod validation schemas
│       ├── types.ts        # Feature types
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
