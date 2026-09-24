# Feature Tree

Living map of the project. Maintained by hooks, audited after major changes. New AI agents read this first to understand the project.

Last audited: [date]

## Foundational Systems

Built during scaffolding. Every feature plugs into these.

**Column order is contract.** `scripts/pulse-inspect.sh` reads these columns by position: #, Name, Convention, Location, Status. Changing the order breaks the pulse dashboard. Extra trailing columns (like Docs or Notes) are fine: `scripts/validate-scaffold.sh` finds the Docs column by its header and reads each system's page path there, from the project root.

| # | Name | Convention | Location | Status | Docs |
|---|------|-----------|----------|--------|------|
| 01 | Git & Hooks | #2 | [path] | not started | docs/systems/git.md |
| 02 | Project Structure & Types | #1, #7 | [path] | not started | docs/systems/structure.md |
| 03 | Theme | #6 | [path] | not started | docs/systems/theme.md |
| 04 | Errors & Loading | #8 | [path] | not started | docs/systems/errors.md |
| 05 | API Layer & Contract | #9, #10 | [path] | not started | docs/systems/api.md |
| 06 | Database | #3 | [path] | not started | docs/systems/database.md |
| 07 | File Storage | #9, #11 | [path] | not started | docs/systems/files.md |
| 08 | Auth & Security | #11 | [path] | not started | docs/systems/auth.md |
| 09 | Routing & Layouts | #21 | [path] | not started | docs/systems/routing.md |
| 10 | State Management | #5 | [path] | not started | docs/systems/state.md |
| 11 | Components & Accessibility | #4, #14, #22 | [path] | not started | docs/systems/components.md |
| 12 | Forms | #20 | [path] | not started | docs/systems/forms.md |
| 13 | Testing | #12, #18 | [path] | not started | docs/systems/testing.md |
| 14 | CI/CD & Performance | #15, #13 | [path] | not started | docs/systems/ci.md |
| 15 | Pulse Monitor | #26 | [path] | not started | docs/systems/pulse-monitor.md |
| 16 | Design Foundation & Interface Craft | #27, #31 | [link to artifact; the vocabulary file; the review checklist] | not started | docs/systems/design-foundation.md |

Notes:
- Not all systems apply to every project. Backend projects skip Theme, Routing, Components. Remove rows that don't apply.
- Add project-specific systems below row 16 using ordinal numbering (17, 18, ...). Use `—` in the Convention column when no framework convention applies.
- Keep the numbers in the `#` column plain, not bold, in both tables: `scripts/validate-maintain.sh` looks for plain digits when it matches a feature folder to its row.
- A system the operating stage defers (#30) keeps its row with Status `deferred (TD-N)` and a docs/systems/ page that says what is deferred and until which trigger.
- A system that waits on an owner action (opening an account, approving a recurring cost, accepting terms) keeps its row with Status `blocked (owner: <action>)` and a docs/systems/ page that names the action and what was built meanwhile (#29).

## Features

**Column order is contract.** Pulse reads these columns by position: #, Feature, Location, Routes, Systems Used. Systems Used values must match Foundational System names (case-insensitive, normalized) for the diagram to link each feature to its systems.

| # | Feature | Location | Routes | Systems Used | Status | Docs |
|---|---------|----------|--------|--------------|--------|------|
| 01 | [name] | [location] | [routes] | [systems] | [status] | docs/features/[name].md |

Status values: not started, in progress, implemented, needs audit, `blocked (owner: <action>)`.

## Audit Log

| Date | Scope | Findings |
|------|-------|----------|
| [date] | [what was audited] | [what was found/fixed] |
