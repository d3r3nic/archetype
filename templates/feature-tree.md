# Feature Tree

Living map of the project: its foundational systems and its features, where each lives, and its status. New sessions read this first to understand what exists before building.

Last audited: [date]

## Foundational Systems

The shared systems this project builds, one row each. Add a row for each system the project's facts call for; each convention's Applies when decides. Common ones to consider, each only where it applies: git and checks (#2), project structure, configuration and types (#1, #7), theme (#6), errors and waiting states (#8), the API client and contract (#9, #10), database (B1), file storage (B6), authentication and authorization (#11, #24), routing (#21), shared state (#5), components and accessibility (#4, #14, #22), forms (#20), testing (#12, #18), checks and delivery (#15, #13), the pulse monitor (#26), and the design foundation (#27, #31). Every feature uses these systems; none builds its own.

**Column order is contract.** `scripts/pulse-inspect.sh` reads these columns by position: #, Name, Convention, Location, Status. Changing the order breaks the pulse dashboard. Extra trailing columns (like Docs or Notes) are fine: `scripts/validate-scaffold.sh` finds the Docs column by its header and reads each system's page path there, from the project root.

| # | Name | Convention | Location | Status | Docs |
|---|------|-----------|----------|--------|------|
| 01 | [system name] | [#N] | [path] | not started | docs/systems/[name].md |

Notes:
- Number the rows in order (01, 02, ...), and use `—` in the Convention column when no framework convention applies.
- Keep the numbers in the `#` column plain, not bold, in both tables.
- A system the operating stage defers (#30) keeps its row with Status `deferred (TD-N)` and a docs/systems/ page that says what is deferred and until which trigger.
- A system that waits on an owner action (opening an account, approving a recurring cost, accepting terms) keeps its row with Status `blocked (owner: <action>)` and a docs/systems/ page that names the action, what exists, and what stays unavailable (#29).
- A system the project considered and does not need gets Status `not applicable` with the reason in its page or a Notes column, or its row is removed.

## Features

**Column order is contract.** Pulse reads these columns by position: #, Feature, Location, Routes, Systems Used. Routes holds each feature's entry points: routes, screens, endpoints, commands or jobs. Systems Used values must match Foundational System names (case-insensitive, normalized) for the diagram to link each feature to its systems. The Docs column names the feature's record; `scripts/validate-develop.sh` checks that it exists and that the record's Tests line names tests that exist.

| # | Feature | Location | Routes | Systems Used | Status | Docs |
|---|---------|----------|--------|--------------|--------|------|
| 01 | [name] | [location] | [routes] | [systems] | [status] | docs/features/[name].md |

Status values: not started, in progress, implemented, needs audit, smoke-test, `blocked (owner: <action>)`.

## Audit Log

Optional: one line each time the map is checked against the code, if the project keeps that history.

| Date | Scope | Findings |
|------|-------|----------|
| [date] | [what was checked] | [what was found or fixed] |
