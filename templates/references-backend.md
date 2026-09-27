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
- Peer coding: [none; or peer-coding/SETTINGS.md, when the owner chose two AI assistants taking turns (development/PEER-CODING.md)]
- API URL: [base URL]

## Tech Stack

Each line must start with `- ` (dash space); content is `- Key: Value`. The inspector parses every bullet. Record what bootstrap chose and add a line for anything else the service depends on.

- Runtime: [runtime]
- Framework: [server framework, or none]
- Language: [language]
- Data access: [the data-access approach, or none when the service owns no database]
- Database: [the store, or none]
- Validation: [how outside data is validated, with one definition per shape (#7)]
- Hosting: [where it runs]
- Auth: [identity provider or approach, or none]
- Testing: [test runner]
- Package Manager: [package manager]

## Commands

Record each command one of three ways: the command in backticks, run exactly as written from this folder (text after the closing backtick is a note and is never run); a note in brackets while none is recorded yet; or `none` when the project has no such command. A step check that needs a command fails on a bracketed note and on a value in any other form. A recorded `migrate` command must also be bounded in § Boundaries to the path that may apply it to production (B1).

```
dev:       [command to start dev server]
build:     [command to build]
test:      [command to run tests]
typecheck: [command to run type checker]
lint:      [command to lint]
deploy:    [command to deploy]
migrate:   [command that applies migrations, or none]
logs:      [command to view logs]
```

## Boundaries

What only each shared system may use, one line per concern (#0, #25): `` - <concern>: `<pattern>` only in `<path>`, `<path>` ``. The pattern is an extended regular expression for this project's own tool, such as the call that opens a database connection or reads the environment. Each path is a folder ending in `/`, a file, or a glob such as `*.test.*`, from this folder. `scripts/validate-develop.sh` fails when a file outside those paths contains the pattern (Markdown files are not read), and the scaffold's exit gate checks the lines that exist. Add a line as each shared system is built. With no shared concern to guard, record `- none: <reason>`.

- [Configuration: `<the pattern that reads the environment>` only in `<the configuration owner's path>`]
- [Database: `<the pattern that opens a connection>` only in `<the data-access layer's path>`]
- [Production migrations: `<the migrate command>` only in `<the manual or gated path that applies them>`]

## Compliance

PROFILE.md records whether the project handles regulated data (#30). This section records what follows from that for this unit. Keep an unanswered fact unknown.

- Regulated data: see PROFILE.md
- Regimes: [each law, contract or standard that applies, with the discovery answer or research behind it; none, with why; or unknown, with the open question]
- Obligations: [what each regime requires of this unit, such as an audit log, encryption, retention and deletion, or access review; none]
- Audit log: [where this unit keeps its audit log when a regime requires one: its path in this unit, recorded when scaffold builds it; kept by <another unit or service>; or not required, with why]
- Audit store: [optional: a pattern found in the audit log's code that names its production store, when the audit folder also holds a memory-only store for tests; the exit gate looks for it]
- Promises to users: [what the project has already told its users about their data, in the owner's words; none]

## Foundational Systems

Complete only the sections for systems this service builds; each convention's Applies when decides. For each, record the choice, where it lives, how features use it, and the reason where it is not obvious. Features use these systems; they never build competing ones (#0), and § Boundaries keeps them from going around them. Sections follow the scaffold's build order.

### Git & Project Init (#2)
Commit convention: [the convention the team follows]
Branch strategy: [the branch model and why]
Checks run: [where the project's checks run before work reaches the main line: a hook at `<path>`, a pipeline at `<path>`, both, or none, with why (#2, #15)]
Hook budget: [how long a check before each commit may take before it moves to the pipeline (#25), or none]

### Project Structure & Types (#1, #7)
Folder structure: [see Folder Structure below]
Configuration: [the configuration owner's path, and how it validates required values at startup]
Type checking: [the level the project holds to, and where it is configured]
Validation: [how outside data is validated, and where the shared data shapes live]

### Architecture (#3)
Responsibilities: [the service's owners of state, rules and effects, and how consumers reach them]
Layers: [the boundaries this service draws and why, such as transport, domain and data access; none that only forward calls]
Usage: [how a new endpoint or job is structured]

### Error System (#8)
Location: [where the error system lives]
Kinds: [the kinds of error the service distinguishes]
Mapping: [the one place errors become the transport's codes and the recorded error format (B2)]
Build-target check: [how custom error types are verified on the real build target; the fix if one is required (#8)]
Usage: [how features raise errors]

### API (B2, #10)
Style: [the API style chosen for the consumers, and why]
Response format: [the one format for success, lists and errors]
Paging: [the paging method and its limits]
Evolution: [how the API changes without breaking consumers the project does not control]
Contract: [how the exchanged shapes are shared with consumers (#10)]
Query allow-list: [when clients compose their own queries and public or device clients call the API: the allow-list's path in backticks, which the exit gate checks exists; otherwise not needed, with why]
Usage: [how handlers return responses]

### Auth System (#11, #24)
Auth owner: [its path, or none when callers do not sign in]
Identity: [what it returns: the project's own identifier, not the provider's]
Authorization: [the permission model and where the check runs: the service layer, against the record]
Critical: [production-learned auth rules]

### Database (B1)
Data access: [the data-access layer's path, and the one pool]
Schema: [where the schema lives]
Tenancy: [how every query is scoped to the caller's tenant, when one deployment serves several customers; or not multi-tenant]
Migrations: [how migrations are written and applied, and the manual or gated path to production]
Usage: [how features read and write data]

### File Storage (B6)
Storage service: [its path, or none when the service handles no files]
Transfer path: [through the server or straight to storage, and why]
Validation: [how content, size and malware are checked]
Usage: [how features store and read files]

### Testing Setup (#12, #18)
Test runner: [which one and command]
Shared setup: [where the shared setup, data builders and fakes live]
Database in tests: [how tests get a disposable real store]
Isolation: [how tests stay independent of each other's data]
Verification commands: [the commands to run: test, typecheck, build]
Coverage: [where testing effort goes and any thresholds]

### CI/CD (#15)
Pipeline: [where the checks run and what a merge requires]
Deploy command: [how to deploy]
Rollback: [how to roll back]

## Folder Structure

```
[paste actual folder structure here]
```

## Existing Patterns to Study

- [feature name]: [path] - [what it demonstrates]

## Critical Lessons

- [lesson]: [what happened and the rule that prevents it]

## Convention Overrides

- [convention #]: [what's different and why]

## Project-Specific Documentation

Where this project's own rules and documents live, when it has them:

- conventions/overrides/{N}-{name}.md: [each override file with a one-line description]
- protocols/{name}.md: [each workflow protocol with a one-line description]
- [other documents]: [each location with what it holds]
