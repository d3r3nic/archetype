# Bootstrap: an existing project

Part of the bootstrap playbook (bootstrap/ONBOARD.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step: read it when the script names it, with the reading it lists, and close it before opening the next.

## Step 4.1: Existing project: scan, extract, migrate
Read: bootstrap/EXISTING-PROJECT.md
Produces: conventions/overrides/, protocols/, catalogs/, the project-root CLAUDE.md.additions, docs/migrated/ and docs/audit/, MIGRATION-NOTES.md saying where each piece of the original guidance lives now, and the References.md and feature-tree.md the migration flow generates from what it found
Check: run scripts/validate-migration.sh
Depends on: bootstrap.3
Skip when: the project is new and has no code or guidance of its own

Full migration flow (scan the codebase, extract rules, cross-reference, discover and audit documents) lives in `bootstrap/EXISTING-PROJECT.md`. Follow it end-to-end; it generates References.md and feature-tree.md itself, so Step 4.2 is skipped for an existing project. PROFILE.md and the design steps below still run, with what the audit found.

**Critical:** migration preserves EVERY rule. Nothing gets lost. If you find yourself summarizing, stop. The check fails on a missing INDEX.md, a migrated copy that drifted from its original, an override or an audit file without its convention header, and a missing References.md or feature-tree.md. Summarization it can only warn about (a short override file), so the source-to-destination review is still yours to do. Any validator failure = re-extract, do not paper over.
