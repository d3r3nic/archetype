# References

## Project

Each line must start with `- ` (dash space). `scripts/pulse-inspect.sh` parses these bullets; lines without a leading dash are ignored.

- Name: [project name]
- Purpose: [one-line description]
- Stage: [development / staging / production]
- Profile: PROFILE.md (operating stage and decision authority per #30 and #29)
- Owner channel: [where escalations go and how quickly the owner usually answers]
- Decision location: [existing decision record path or section; otherwise DECISIONS.md from templates/decisions.md, one location only]
- Reporting pace: [every session / every release / on request]
- API URL: [base URL]

## Tech Stack

Each line must start with `- ` (dash space); content is `- Key: Value`. Inspector parses every bullet.

- Runtime: [runtime]
- Framework: [server framework]
- Language: [language]
- ORM/DB: [ORM or query layer]
- Database: [database engine]
- Validation: [schema library — one schema = types + validation]
- Cloud: [cloud provider or self-hosted]
- Auth: [identity provider or approach]
- Testing: [test runner]
- Package Manager: [package manager]

## Commands

Record each command one of three ways: the command in backticks, run exactly as written from this folder (text after the closing backtick is a note and is never run); a note in brackets while none is recorded yet; or `none` when the project has no such command. A step check that needs a command fails on a bracketed note and on a value in any other form.

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

## Compliance

PROFILE.md records whether the project handles regulated data (#30). This section records what follows from that for this unit. Keep an unanswered fact unknown.

- Regulated data: see PROFILE.md
- Regimes: [each law, contract or standard that applies, with the discovery answer or research behind it; none, with why; or unknown, with the open question]
- Obligations: [what each regime requires of this unit, such as an audit log, encryption, retention and deletion, or access review; none]
- Audit log: [where this unit keeps its audit log when a regime requires one (a path in this unit), or kept by <the unit or service that keeps it>; not required, with why]
- Promises to users: [what the project has already told its users about their data, in the owner's words; none]

## Foundational Systems

Each system is built once following convention #0 (Reusability). Features plug into these, never build ad-hoc. Sections ordered by scaffold build sequence.

### Git & Project Init (#2)
Commit convention: [e.g., conventional commits]
Branch strategy: [e.g., trunk-based]
Pre-commit hooks: [what runs - lint, format, typecheck]
Pre-commit budget: [max hook runtime before a check moves to CI (#25)]

### Project Structure & Types (#1, #7)
Folder structure: [see Folder Structure section below]
Path alias: [if applicable]
Type checking: [strictest mode the language supports]
File-size limit: [lines per file the tools in use can read whole; split past it (#1, #17)]
Compaction cadence: [optional; when the AI compacts context in long sessions (#17)]
Validation library: [name - one schema = types + validation]
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
Build-target check: [how custom error subclasses are verified on the real build target; the constructor fix if one is required (#8)]
Usage: [how features throw errors]

### API Layer & Contract (#9, #10)
Response format: [e.g., "{ data, meta, errors } via responses.success()"]
Response utility: [path to response helpers]
Contract: [how types are shared with frontend - API specification, type-safe RPC, shared schemas]
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
Pattern: [e.g., "presigned URLs, 3-step: initiate → upload to object storage → verify"]
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
Lint rules: [AI-targeted rules - no untyped escape hatch, no console-level output]

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
