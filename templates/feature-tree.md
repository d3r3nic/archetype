# Feature Tree

Living map of the project. Maintained by hooks, audited after major changes. New AI agents read this first to understand the project.

Last audited: [date]

## Foundational Systems

Built during scaffolding. Every feature plugs into these.

**Column order is contract.** `scripts/pulse-inspect.sh` reads these columns positionally: `# | Name | Convention | Location | Status`. Changing the order breaks the pulse dashboard. Extra trailing columns (like Docs/Notes) are fine.

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
| 16 | Design Foundation | #27 | [link to artifact] | not started | docs/systems/design-foundation.md |

Notes:
- Not all systems apply to every project. Backend projects skip Theme, Routing, Components. Remove rows that don't apply.
- Add project-specific systems below row 15 using ordinal numbering (16, 17, ...). Use `—` in the Convention column when no framework convention applies.
- Do not bold cells in the `#` column; the inspector matches literal digits and skips bolded rows.

## Features

**Column order is contract.** Pulse reads: `# | Feature | Location | Routes | Systems Used`. "Systems Used" values must match Foundational System names (case-insensitive, normalized) for drift detection + Mermaid diagram generation to work.

| # | Feature | Location | Routes | Systems Used | Status | Docs |
|---|---------|----------|--------|--------------|--------|------|
| 01 | [name] | [location] | [routes] | [systems] | [status] | docs/features/[name].md |

Status values: not started | in progress | implemented | needs audit

## Audit Log

| Date | Scope | Findings |
|------|-------|----------|
| [date] | [what was audited] | [what was found/fixed] |
