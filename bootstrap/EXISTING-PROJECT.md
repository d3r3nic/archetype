# Existing Project Bootstrap — Parts A, B, C, D

Routed from `ONBOARD.md` Step 4 when the user is bootstrapping into an EXISTING project (via `inject.sh`) rather than starting new. Preserves everything the project already has; adds framework structure without modifying original files.

**Critical rule for this entire file:** the migration must preserve EVERY rule. Nothing gets lost. If you find yourself summarizing, stop — the "CRITICAL: do not summarize" rule is enforced by `scripts/validate-migration.sh` which checks override-file length. A lazy AI that summarizes will fail the validator.

## Prompt to give the AI

> Read `Conventions.md` and all convention docs in `conventions/`. Then scan this codebase to understand what already exists AND extract every rule from the existing instruction files. Follow `bootstrap/EXISTING-PROJECT.md` Parts A, B, C, D in order.

---

## Part A — Scan the codebase

How to scan:
1. Read `package.json` (or equivalent: `pyproject.toml`, `Cargo.toml`, `go.mod`, `*.csproj`) to identify the tech stack, dependencies, and available commands.
2. Read the project's folder structure at the top two levels to understand organization.
3. Look at `shared/`, `common/`, `lib/`, or equivalent directory for existing foundational systems.
4. Look at `features/`, `pages/`, `modules/`, or equivalent for feature mapping.
5. Check for existing documentation, config files, and instruction files.
6. If a `libraries/` directory exists in the framework, check for framework-specific guidance.

For each framework convention (universal #0 through the highest numbered, plus backend B1-B7 if backend project), determine:
1. Does a foundational system for this convention already exist? If yes, where?
2. If partial: what exists, what's missing?
3. If not at all: mark "not started" in `feature-tree.md`.

Document findings in `References.md` under "Foundational Systems" and in `feature-tree.md`.

---

## Part B — Rule Extraction (CRITICAL — do not skip, do not summarize)

Read EVERY existing instruction file in full:
- `/CLAUDE.md` or `/Claude.md` (main project rules)
- Any `/docs/` directory with project-specific guides
- Any `/TECHNICAL-DEBT.md`, `/HANDOFF.md`, `/MIGRATION_*.md`, `/REFACTORING_*.md`, `/IMPLEMENTATION-*.md`
- Any `.claude/` directory with rules, agents, commands
- Any external instruction files referenced from `CLAUDE.md` (follow the pointers)

Extract every rule, protocol, and pattern. Categorize each:

### Category 1 — Maps to a framework convention

For each rule that maps to a framework convention, create an override file at `archetype/conventions/overrides/{N}-{name}.md`. Format:

```
# Convention #N: {Name} — PROJECT OVERRIDES

This file extends conventions/{N}-{name}.md with project-specific rules
extracted from the existing instruction files. The base convention still
applies. These are additional project-specific rules.

## Source
Extracted from: {file paths of original rule sources}
Migration date: {date}

## Project-Specific Rules
{Full text of every project-specific rule, with original wording preserved}

## Code Examples (if any)
{Original code examples from the source files}

## Critical Production Lessons
{Bugs that broke production and the rules that prevent them}
```

### Category 2 — Workflow protocols

Audit, breaking change, technical debt, feature development protocols. Create at `archetype/protocols/{name}.md`. Capture: when it applies, step-by-step process, templates, examples, reporting format.

Common protocols: Feature Audit Protocol, Breaking Change Protocol, Technical Debt Tracking, Critical Workflow for complex tasks, Pre-commit checklist, Code review process.

### Category 3 — Reference catalogs

Feature directories, pattern catalogs, helper API lists, theme token catalogs. Create at `archetype/catalogs/{name}.md`.

Common catalogs: Feature directory (every feature with purpose), factory-pattern reference, helper catalog, quick-reference Q&A, topic-based documentation map, external-docs index.

**Always create `catalogs/external-docs.md`** if the project has a `/docs/` folder with substantial content — cataloging every subfolder and standalone file with a one-line description. The framework's `docs/systems/` and `docs/features/` are for NEW framework-specific docs; they do NOT replace the existing `/docs/`. The catalog makes existing docs discoverable.

### Category 4 — Framework-level enforcement rules (for CLAUDE.md root)

Rules that should appear in the project's root `CLAUDE.md` enforcer (not just in override docs). These are direct "never do X" rules that catch common mistakes at the enforcer layer. Add them to `archetype/CLAUDE.md.additions`.

This file is a staging area — the user reviews and merges into root `CLAUDE.md` when ready. A rule may appear BOTH as a Category 1 override (full detail) AND as a Category 4 addition (one-line enforcer rule). The override has depth; the addition has visibility.

Example — "never throw new Error" rule:
- Category 1: `conventions/overrides/08-errors.md` — full rule with project error hierarchy, examples, production-lesson context
- Category 4: `CLAUDE.md.additions` — one line: `Never throw new Error. Use AppError subclass. → conventions/overrides/08-errors.md`

**CRITICAL: do not summarize. EXTRACT IN FULL.** The original wording and detail must be preserved. A developer reading override files should get the same information as reading the original `CLAUDE.md`, just organized. If the original has 200 lines on the audit protocol, the protocol file has 200 lines. Lossy summarization defeats the purpose — and is checked by `scripts/validate-migration.sh`.

---

## Part C — Cross-reference everything

After extraction, update `References.md` to LIST every file created. The "Project-Specific Documentation" section must enumerate:
- Every file in `conventions/overrides/` with a one-line description
- Every file in `protocols/` with a one-line description
- Every file in `catalogs/` with a one-line description

Create `archetype/INDEX.md` as a master map of every file in the `archetype/` subfolder, organized by category. A new AI agent reading `INDEX.md` should be able to find any rule, protocol, or pattern in 2 hops.

**Verification (manual):** walk through the original `CLAUDE.md` top-to-bottom. For each section, identify which extracted file it lives in now. Any section without a destination = bug. Go back and extract it.

**Verification (automated):** run `scripts/validate-migration.sh`. Checks:
- Every rule in original CLAUDE.md has a pointer in INDEX.md
- Every override file is non-trivial length (catches summarization)
- Every audit file names its convention
- No original files modified
- Migrated docs match originals byte-for-byte

For existing systems that don't fully match a framework convention, note the gap under "Convention Overrides" in `References.md`. Do NOT change any existing code during bootstrap.

---

## Part D — Documentation discovery, migration, and audit

Existing projects often have documentation in many places, not just `/docs/`. Find ALL of it.

### Step 1 — Discover

Search for:
- `/docs/` at project root (most common)
- `/documentation/`, `/doc/`, `/wiki/`, `/guides/`, `/handbook/` (alternate names)
- `README.md` files anywhere in the project (not just root)
- `/notes/`, `/knowledge/`, `/reference/` (less common)
- Any `*.md` files in `src/` subdirectories (feature docs)
- `/architecture/`, `/decisions/`, `/adr/` (architecture decision records)
- `/docs1/`, `/docs2/`, `/old-docs/` (sometimes projects have multiple generations)
- Confluence / Notion / external doc URLs referenced from `CLAUDE.md` or `README`
- `/HANDOFF.md`, `/MIGRATION_*.md`, `/REFACTORING_*.md`, `/IMPLEMENTATION-*.md` at root (these are docs even if not in a folder)

Use `grep` or `find` to locate all `.md` files (excluding `node_modules`, `.git`, `dist`, `build`).

### Step 2 — Categorize

- **TIER 1** — Architectural / standards docs (folder structures, patterns, conventions). Definitely migrate.
- **TIER 2** — Feature / system docs (how-to guides, integration guides). Definitely migrate.
- **TIER 3** — Project history (handoff notes, migration summaries, refactoring proposals). Migrate but mark as historical.
- **TIER 4** — Outdated / stale docs (clearly references removed code, dated more than a year ago). Migrate but flag as stale.
- **TIER 5** — Generated / temporary (test reports, build outputs, agent reports). SKIP, do not migrate.
- **AMBIGUOUS** — Cannot tell if it's relevant. STOP and ASK the user before deciding.

### Step 3 — Present findings BEFORE migrating

Output a summary with counts per tier, the ambiguous items requiring user decision, and the plan. Wait for user response before proceeding.

**If no user is available** (e.g., automated batch migration), decide based on evidence: file dates, self-labels ("superseded", "2023 snapshot"), contradictions with current stack. Document the decision in the audit file with rationale so it can be reversed.

### Step 4 — Migrate (COPY, not move, not edit)

For each doc to migrate, COPY it into `archetype/docs/migrated/` preserving the original folder structure. Original files stay UNTOUCHED.

### Step 5 — Map to convention

For each migrated doc, identify the framework convention it maps to. Examples:
- `/docs/01-fundamentals/architecture-overview.md` → convention #3 (Architecture)
- `/docs/02-structure/folder-structure.md` → convention #1 (Project Setup)
- `/docs/03-state-management/redux-structure.md` → convention #5 (State Management)
- `/docs/06-styling/*` → convention #6 (Styling)
- `/docs/07-error-handling/*` → convention #8 (Errors)
- `/docs/00-factory-pattern/*` → convention #0 (Reusability)

### Step 6 — Audit against convention

For each migrated doc, audit:
- Content that aligns with the convention (good)
- Content that violates the convention (flag it)
- Content that doesn't fit any convention (note it)
- **Stale content** (references removed code, deprecated libraries, old patterns). Cross-check against `package.json` and other authoritative sources.
- Conflicts with the project's extracted rules (from Part B)

### Step 7 — Write audit files

Create `archetype/docs/audit/{doc-path}.audit.md` for each migrated doc:
- Source path (where it was copied from)
- Maps to convention: #N
- Alignment summary: which parts follow the convention
- Violations found: parts that conflict
- Staleness check: does the doc still match current code?
- Recommended action: keep as-is, update, deprecate, or merge

**If the migrated copy is stale, prepend a STALE banner to the top of the migrated copy.** The banner points to the audit file. This prevents a reader from falling into the same trap the audit caught. Format:

```markdown
> **⚠️ STALE — see ../audit/{path}.audit.md**
> This doc references {tool/pattern} which the project no longer uses.
> Preserved for historical reference only.

---

{original content untouched}
```

This is the one documented edit allowed on migrated copies — a banner, never touching the original content.

### Step 8 — Write summary

Create `archetype/docs/audit/SUMMARY.md` with one-line status per doc (clean / minor issues / major issues / stale / orphaned). If the harness blocks filename `SUMMARY.md`, use `audit-status-table.md` and note the rename inside.

### Step 9 — Cross-link

Update `INDEX.md` and `References.md` with the migrated docs and audit results.

### Critical migration rules

- **COPY, do not edit** the original content. Original `/docs/` stays untouched.
- **COPY, do not move.** Originals remain in place.
- **STALE banner is the one exception** — banner added to migrated copy only, not the original.
- Migrated copies in `archetype/docs/migrated/` are the audit targets, not the originals.
- Audit findings live in `archetype/docs/audit/` separately from migrated copies.
- A future cleanup phase (NOT part of bootstrap) uses audit findings to decide what to fix.

---

## What to generate at the end

- `References.md` (project context + tech stack + Critical Lessons + Convention Overrides summary)
- `feature-tree.md` (all systems and features mapped with status)
- `docs/systems/` with a doc for each foundational system that already exists
- `docs/features/` with a doc for each feature that already exists
- `archetype/conventions/overrides/` with one file per convention that has project-specific rules
- `archetype/protocols/` with one file per workflow protocol found
- `archetype/catalogs/` with one file per reference catalog found
- `archetype/CLAUDE.md.additions` with extra enforcement rules staged for root merge
- `archetype/INDEX.md` master map
- `archetype/docs/migrated/` (byte-for-byte copies of discovered docs)
- `archetype/docs/audit/` (one audit per migrated doc + SUMMARY.md)
- `MIGRATION-NOTES.md` explaining what was extracted, where it lives, how to merge

Run `scripts/validate-migration.sh` before committing. Any validator failure = re-extract, do not paper over.
