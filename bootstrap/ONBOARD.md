# Phase 1: Bootstrap

Onboard a project into the framework. Run once at project creation or when adopting the framework on an existing project.

## Prerequisites

- You know what you want to build (even just "a todo app" is enough to start)
- Tech stack chosen (or let the framework help you choose in Step 2)

## Step 1: Initialize Project

Tell your AI assistant to set up the project. Alternatively, run these commands yourself:

### For a NEW project (full clone):

```bash
# Option A: Clone from GitHub
git clone https://github.com/d3r3nic/archetype.git my-project-name
cd my-project-name
rm -rf .git libraries/

# Option B: If you already have the framework files locally
cp -r /path/to/archetype my-project-name
cd my-project-name
rm -rf .git libraries/

# For a fullstack project (frontend + backend as separate folders):
mkdir my-project && cd my-project
git clone https://github.com/d3r3nic/archetype.git frontend
git clone https://github.com/d3r3nic/archetype.git backend
rm -rf frontend/.git frontend/libraries/ backend/.git backend/libraries/
```

### For an EXISTING project (inject as subfolder):

Use the inject script. It copies the framework into your project as a subfolder without touching any existing files. This is the safe migration path.

```bash
# Clone the framework somewhere if you don't have it locally
git clone https://github.com/d3r3nic/archetype.git /tmp/archetype-framework

# Inject into your existing project
cd /tmp/archetype-framework
./inject.sh /path/to/your/existing-project

# Default subfolder name is "archetype". To customize:
./inject.sh /path/to/your/existing-project archetype-migration
```

After injection, your existing project has a new subfolder (default `archetype/`) containing the framework. Nothing existing was modified. From here, follow the "For an EXISTING project" path in Step 3.

After setup, each project folder has:
```
your-project/
├── CLAUDE.md          # the enforcer
├── Conventions.md     # convention index
├── conventions/       # 25 convention docs
├── bootstrap/         # this file
├── scaffolding/       # scaffold guide
├── development/       # develop + maintain guides
└── templates/         # references, feature-tree, hooks
```

For fullstack: each endpoint (frontend/, backend/) is a separate project with its own copy of the framework, its own References.md, feature-tree.md, and docs/. They are separate git repos. If you prefer a monorepo, put both folders under one git repo and manage them together.

## Step 2: Discovery (AI interviews you)

Do NOT jump straight to building. The AI needs to understand what you're building first. Tell the AI to read this section and follow the discovery process.

### Discovery Prompt:

Give this to your AI assistant:

---

Read bootstrap/ONBOARD.md Step 2: Discovery. Follow the discovery process before generating anything.

I want to build: [describe your idea in plain English, even one sentence is fine]

---

### Discovery Process (for the AI assistant):

Before choosing any technology or generating any files, interview the user with these questions. Ask them one group at a time. These are designed for people who may not know technical terms.

**Group 1 - What is it?**
- What does your app do? Describe it like you're explaining to a friend.
- Who uses it? Just you? Your team? The public?
- Can you name an existing app that's similar to what you want? (even loosely)

**Group 2 - Where does it run?**
- Should this work in a web browser? (like Gmail, Twitter)
- Should this be a phone app? (like Instagram, Uber)
- Should this be a desktop application? (like Photoshop, Slack desktop)
- Or some combination?

**Group 3 - What do users do?**
- Do users need to create accounts and log in?
- Do users fill out forms or submit data?
- Do users upload files or images?
- Do users need to see updates in real time? (like chat, live notifications)
- Does the app need to work without internet? (offline mode)

**Group 4 - Scale and stage**
- Is this a personal project, a startup MVP, or an enterprise product?
- How many users do you expect? (just you, tens, hundreds, thousands, millions)
- Do you have any tech preferences? (if yes, which ones; if no, that's fine)

**Group 5 - Infrastructure and sensitivity**
- Does this app handle sensitive data that has legal requirements? (health records, financial data, personal information with privacy laws)
- Do you or your team have experience managing servers and cloud infrastructure? Or would you prefer something that handles that for you?
- How important is it that you own and control all the infrastructure vs getting something live quickly?

### How the AI decides (read the user's knowledge level):

The AI should gauge the user's technical experience from how they talk. Adjust choices accordingly:

**Non-technical user** (says things like "I don't know how apps work", "I heard AI can help"):
- Choose managed services that require zero DevOps knowledge
- Database: Supabase (managed PostgreSQL with auth and storage built in) or SQLite for simple apps
- Hosting: Vercel (frontend), Railway or Render (backend)
- Auth: Supabase Auth or Clerk (fully managed, drop-in)
- These ARE production-level services. They just don't require server management knowledge.

**Developer with some experience** (knows frameworks, doesn't know DevOps):
- Choose cloud platforms with simple deployment
- Database: Managed PostgreSQL (Supabase, Neon, PlanetScale)
- Hosting: Vercel/Netlify (frontend), Railway/Render/Fly.io (backend)
- Auth: Auth0, Clerk, or framework-native auth
- Can migrate to AWS/GCP later as needs grow

**Experienced developer / team with DevOps knowledge** (mentions AWS, cloud, infrastructure):
- Choose cloud providers with full control. AWS preferred for production.
- Database: AWS RDS (PostgreSQL), or self-managed on cloud
- Hosting: AWS (Lambda/ECS/EC2), GCP, or Azure
- Auth: AWS Cognito, or self-managed JWT with proper security
- CI/CD: GitHub Actions deploying to cloud provider
- Full monitoring, logging, alerting

**Enterprise / compliance requirements** (HIPAA, SOC2, financial regulations):
- Must use cloud providers with compliance certifications. AWS preferred.
- Database: AWS RDS with encryption at rest and in transit
- Auth: AWS Cognito or enterprise identity provider
- Infrastructure as code (SST, CDK, Terraform)
- Audit trails, encryption, access controls are mandatory
- Monitoring: CloudWatch, Datadog, or equivalent with alerting

### How to translate answers into technical decisions:

| Answer | Technical Decision |
|--------|-------------------|
| Web browser app | Frontend: web framework (React, Vue, Svelte, etc.) |
| Phone app | Mobile: React Native, Flutter, or native |
| Desktop app | Desktop: Electron, Tauri, .NET WPF, or native |
| Users log in | Auth system needed |
| Users submit forms | Form system needed |
| Users upload files | File storage system needed |
| Real-time updates | WebSocket/SSE needed |
| Works offline | Offline support needed |
| Just me / personal | Simple stack, SQLite OK, managed hosting |
| Startup MVP | Modern stack, managed PostgreSQL, cloud hosting |
| Enterprise / compliance | AWS/GCP, infrastructure as code, full monitoring |
| Millions of users | Performance, CDN, caching, horizontal scaling |
| No tech preferences | AI picks based on experience level (see above) |
| Has preferences | AI respects them and fills in the gaps |
| Sensitive data (health, finance) | Compliance-grade infrastructure, encryption, audit trails |
| No DevOps knowledge | Managed services (Supabase, Vercel, Railway) |
| Knows AWS/cloud | AWS with proper architecture (preferred for production) |

### Common proven stacks (for reference):

Web frontend: React + TypeScript + Vite + Tailwind
Backend API (Node): Node.js + TypeScript + Express + Prisma + PostgreSQL
Backend API (Python): Python + FastAPI + SQLAlchemy + PostgreSQL
Backend API (C#): ASP.NET + Entity Framework + SQL Server
Mobile: React Native + Expo OR Flutter + Dart
Desktop: Electron + React OR Tauri + Svelte

After discovery, the AI knows: what kind of app, what platforms, what features, what scale. Now it can choose the right stack and proceed to generate References.md.

## Step 3: Generate Project Context

After discovery, the AI generates the project files.

### For a fullstack project (web frontend + backend API):

The AI runs the generation process TWICE - once for the frontend folder using templates/references-frontend.md, and once for the backend folder using templates/references-backend.md. Each endpoint gets its own References.md and feature-tree.md.

### For a single endpoint:

The AI runs once in the project folder, using the matching template (frontend, backend, or mobile).

### Generation Process (for the AI assistant):

---

Read Conventions.md to understand the convention index. Do NOT read all 25 convention docs upfront.

Based on the discovery answers, you now know: what platforms, what features, what scale, and what tech stack.

Generate these files:
- References.md using the appropriate template from templates/ (references-frontend.md, references-backend.md, or references-mobile.md)
- feature-tree.md using templates/feature-tree.md (systems listed as "not started", remove systems the project doesn't need based on discovery answers)
- docs/systems/ directory (empty)
- docs/features/ directory (empty)
- .gitignore appropriate for the tech stack
- Initialize git with an initial commit

For each foundational system section in References.md:
1. Read the corresponding convention doc (the # number is in the section header)
2. Read its Research Notes section
3. Research the current best practices for that convention in the chosen tech stack. If you can do web searches, search for the latest patterns. If not, use your best knowledge and note what should be verified.
4. Describe HOW the system will be implemented
5. Report what you found so the user can verify
6. Leave Location fields empty (scaffolding fills them in)
7. If a system is not needed (based on discovery), remove it from References.md and feature-tree.md

---

### Example bootstrap conversations:

**Vibe coder with a vague idea:**

User: "I want to build an app for my restaurant"

AI: "Great! Let me ask a few questions to understand what you need..."
- "What should the app do? Take orders? Show the menu? Let people book tables?"
- "Should customers use it in a browser or as a phone app?"
- "Do customers need to create accounts?"
- ...

User: "I just want people to see our menu and book a table online"

AI: "Got it. This is a web app with a frontend for customers and a backend to store menu items and bookings. Users don't need accounts for viewing the menu, but bookings need a simple form. No file uploads, no real-time, no offline needed. I'd recommend React + Node.js. Let me set it up..."

**Developer who knows what they want:**

User: "I'm building a healthcare SaaS. React frontend, SST backend on AWS, Prisma with PostgreSQL, Cognito auth. I know the stack."

AI: "Perfect. Let me generate your References.md with that stack. I'll read through the conventions and set everything up..."

---

### For an EXISTING project:

Existing projects already have rules, protocols, and conventions accumulated over time. The migration must preserve EVERY rule. Nothing gets lost. The bootstrap has TWO parts: (1) scan the codebase, (2) extract every rule from existing instruction files.

Use this prompt with your AI assistant:

---

Read Conventions.md and all convention docs in conventions/. Then scan this codebase to understand what already exists AND extract every rule from the existing instruction files.

PART A: Scan the codebase

How to scan:
1. Read package.json (or equivalent) to identify the tech stack, dependencies, and available commands
2. Read the project's folder structure at the top two levels to understand organization
3. Look at the shared/ or common/ directory for existing foundational systems
4. Look at the features/ or pages/ directory to map existing features
5. Check for existing documentation, config files, and instruction files
6. If a libraries/ directory exists in the framework, check for framework-specific guidance

For each convention (#0-#22), determine:
1. Does a foundational system for this convention already exist?
2. If yes: where does it live? Document it in References.md.
3. If partially: what exists and what's missing? Note gaps.
4. If no: mark as "not started" in feature-tree.md.

PART B: Rule Extraction (CRITICAL - do not skip)

Read EVERY existing instruction file in full:
- /CLAUDE.md or /Claude.md (the main project rules)
- Any /docs/ directory with project-specific guides
- Any /TECHNICAL-DEBT.md, /HANDOFF.md, /MIGRATION_*.md, /REFACTORING_*.md
- Any .claude/ directory with rules, agents, or commands
- Any external instruction files referenced from the main CLAUDE.md (follow the pointers)

Extract every rule, protocol, and pattern. Categorize each one:

CATEGORY 1 - Maps to a framework convention (#0-#22):
For each rule that maps to an existing framework convention, create an override file at:
archetype/conventions/overrides/{convention-number}-{convention-name}.md

This file documents project-specific deviations or additions to that convention. Format:
```
# Convention #N: {Name} - PROJECT OVERRIDES

This file extends conventions/{N}-{name}.md with project-specific rules
extracted from the existing instruction files. The base convention still
applies. These are additional project-specific rules.

## Source
Extracted from: {file paths of original rule sources}
Migration date: {date}

## Project-Specific Rules
{Full text of every project-specific rule, with the original wording preserved}

## Code Examples (if any)
{Original code examples from the source files}

## Critical Production Lessons
{Bugs that broke production and the rules that prevent them}
```

CATEGORY 2 - Workflow protocols (audit, breaking change, technical debt, feature development):
These don't map to a single convention - they are project-wide protocols. Create a file at:
archetype/protocols/{protocol-name}.md

For each protocol, capture:
- When it applies
- Step-by-step process
- Templates and checklists
- Examples
- Reporting format

Common protocols to look for:
- Feature Audit Protocol
- Breaking Change Protocol
- Technical Debt Tracking
- Critical Workflow for complex tasks
- Pre-commit checklist
- Code review process

CATEGORY 3 - Reference catalogs (feature directory, pattern catalog, helper APIs):
These are reference materials, not rules. Create files at:
archetype/catalogs/{catalog-name}.md

Examples:
- Feature directory (every feature with its purpose)
- Factory pattern reference implementations
- Theme helper catalog (available colors, borders, spacings)
- Quick reference Q&A
- Topic-based documentation map (which doc to read for which task)
- External docs index (catalog of every existing /docs/ folder and standalone doc with a one-line description so an AI knows what's in each)

If the existing project has a /docs/ folder with substantial content, ALWAYS create catalogs/external-docs.md cataloging every subfolder and standalone file with a one-line description. The framework's docs/systems/ and docs/features/ are for NEW framework-specific docs - they do not replace the existing /docs/. The catalog makes the existing /docs/ discoverable to a new AI agent.

PART D: Documentation discovery, migration, and audit

Existing projects often have documentation in many places, not just /docs/. Find ALL of it.

Step 1: Discover all documentation in the project. Search for:
- /docs/ at project root (most common)
- /documentation/, /doc/, /wiki/, /guides/, /handbook/ (alternative names)
- README.md files anywhere in the project (not just root)
- /notes/, /knowledge/, /reference/ (less common)
- Any *.md files in src/ subdirectories (feature docs)
- /architecture/, /decisions/, /adr/ (architecture decision records)
- /docs1/, /docs2/, /old-docs/ (sometimes projects have multiple)
- Confluence/Notion/external doc URLs referenced from CLAUDE.md or README
- /HANDOFF.md, /MIGRATION_*.md, /REFACTORING_*.md, /IMPLEMENTATION-*.md at root (these are docs even if not in a folder)

Use grep or find to locate all .md files in the project (excluding node_modules, .git, dist, build).

Step 2: Categorize what was found:
- TIER 1 - Architectural/standards docs (folder structures, patterns, conventions): definitely migrate
- TIER 2 - Feature/system docs (how-to guides, integration guides): definitely migrate
- TIER 3 - Project history (handoff notes, migration summaries, refactoring proposals): migrate but mark as historical
- TIER 4 - Outdated/stale docs (clearly references removed code, dated more than a year ago): migrate but flag as stale
- TIER 5 - Generated/temporary (test reports, build outputs, agent reports): SKIP, do not migrate
- AMBIGUOUS - Cannot tell if it's relevant: STOP and ASK the user before deciding

Step 3: Present findings to the user BEFORE migrating.

Output a summary:
```
Documentation discovery results:

Found in {project root}:
- /docs/ (12 files, 4 folders) - architectural and standards docs - TIER 1
- /docs1/ (8 files) - older docs that look like duplicates - AMBIGUOUS
- /HANDOFF.md - project history - TIER 3
- /TECHNICAL-DEBT.md - active tracking doc - already extracted in PART B
- /src/features/patients/docs/ - feature-specific docs - TIER 2
- /src/shared/offline-mode/integration-docs/ - subsystem docs - TIER 2
- /MIGRATION_SUMMARY.md - completed migration history - TIER 3
- /OPTIMISTIC-FOLDER-CREATION.md - feature notes at root - AMBIGUOUS

Plan:
- Migrate 25 TIER 1-2 docs into archetype/docs/migrated/
- Migrate 4 TIER 3 docs into archetype/docs/migrated/history/ marked as historical
- Skip 0 TIER 5 docs

Ambiguous items requiring your decision:
1. /docs1/ - is this actively used or replaced by /docs/?
2. /OPTIMISTIC-FOLDER-CREATION.md - is this a current spec or historical notes?

Should I proceed with the plan above? Please answer the ambiguous questions.
```

Wait for user response before proceeding to step 4.

Step 4: For each doc to migrate, COPY it (read original, write copy) into archetype/docs/migrated/ preserving the original folder structure. Original files stay UNTOUCHED.

Step 5: Map each migrated doc to a framework convention. For example:
   - /docs/01-fundamentals/architecture-overview.md → maps to convention #3 (Architecture)
   - /docs/02-structure/folder-structure.md → maps to convention #1 (Project Setup)
   - /docs/03-state-management/redux-hierarchical-structure.md → maps to convention #5 (State Management)
   - /docs/06-styling/* → maps to convention #6 (Styling)
   - /docs/07-error-handling/* → maps to convention #8 (Errors)
   - /docs/00-factory-pattern/* → maps to convention #0 (Reusability)

Step 6: For each migrated doc, audit it against its convention. Look for:
   - Content that aligns with the convention (good)
   - Content that violates the convention (flag it)
   - Content that doesn't fit any convention (note it)
   - Stale content (refers to removed code, old patterns, deprecated libraries)
   - Conflicts with the project's existing rules (from PART B extraction)

Step 7: Create archetype/docs/audit/{doc-name}.audit.md for each migrated doc with:
   - Source path (where it was copied from)
   - Maps to convention: #N
   - Alignment summary: which parts follow the convention
   - Violations found: parts that conflict with the convention
   - Staleness check: does the doc still match current code?
   - Recommended action: keep as-is, update, deprecate, or merge into another doc

Step 8: Create archetype/docs/audit/SUMMARY.md listing every audited doc with one-line status (clean / minor issues / major issues / stale / orphaned).

Step 9: Update INDEX.md and References.md with the migrated docs and audit results.

CRITICAL:
- COPY, do not edit. Original /docs/ stays untouched.
- COPY, do not move. The originals must remain in place.
- The migrated copies in archetype/docs/migrated/ are the audit targets, not the originals.
- The audit findings live in archetype/docs/audit/ separately from the migrated copies.
- A future cleanup phase (not part of bootstrap) will use the audit findings to decide what to fix in the migrated copies.

CATEGORY 4 - Framework-level enforcement rules:
Rules that should appear in the project's CLAUDE.md enforcer (not just in convention docs). These are direct "never do X" rules. Add them to:
archetype/CLAUDE.md.additions

This file contains additional enforcement rules that should be appended to the framework's CLAUDE.md when the user is ready to promote it.

Generate:
- References.md (project context + tech stack + Critical Lessons + Convention Overrides summary)
- feature-tree.md (all systems and features mapped with status)
- docs/systems/ with a doc for each foundational system that already exists
- docs/features/ with a doc for each feature that already exists
- archetype/conventions/overrides/ with one file per convention that has project-specific rules
- archetype/protocols/ with one file per workflow protocol found
- archetype/catalogs/ with one file per reference catalog found
- archetype/CLAUDE.md.additions with extra enforcement rules
- MIGRATION-NOTES.md explaining everything that was extracted, where it lives, and how to merge it

CRITICAL: do not summarize. EXTRACT IN FULL. The original wording and detail must be preserved. A developer reading the override files should get the same information as reading the original CLAUDE.md, just organized differently. If the original has 200 lines on the audit protocol, the protocol file has 200 lines. Lossy summarization defeats the purpose.

PART C: Cross-reference everything

After extraction, update References.md to LIST every file you created. The "Project-Specific Documentation" section in References.md must enumerate:
- Every file in conventions/overrides/ with a one-line description
- Every file in protocols/ with a one-line description
- Every file in catalogs/ with a one-line description

Also create archetype/INDEX.md as a master map of every file in the archetype/ subfolder, organized by category. A new AI agent reading INDEX.md should be able to find ANY rule, protocol, or pattern in 2 hops.

Verification: walk through the original CLAUDE.md from top to bottom. For each section, identify which extracted file it lives in now. If any section has no destination, that's a bug - go back and extract it.

For existing systems that don't fully match the convention, note the gap under "Convention Overrides" in References.md. Do not change any existing code during bootstrap.

---

## Step 4: Set Up Hooks (optional - can be done later)

Hooks automatically remind the AI to update documentation and run verification. See templates/hooks-spec.md for what hooks to create. This step can be deferred to scaffolding if you want to get started faster.

## Checklist

After bootstrap, verify:

- [ ] CLAUDE.md in project root (or in archetype/ subfolder if existing project)
- [ ] Conventions.md in project root (or in archetype/)
- [ ] conventions/ directory with all 25 framework convention docs (unmodified)
- [ ] References.md generated with relevant sections filled (irrelevant systems removed)
- [ ] feature-tree.md initialized (irrelevant systems removed)
- [ ] docs/systems/ directory created
- [ ] docs/features/ directory created
- [ ] Git initialized with .gitignore (new project only)

For existing projects, additional verification:
- [ ] conventions/overrides/ directory with project-specific rules per convention
- [ ] protocols/ directory with workflow protocols extracted from existing files
- [ ] catalogs/ directory with reference catalogs extracted
- [ ] CLAUDE.md.additions with extra enforcement rules to merge later
- [ ] Every rule from the original CLAUDE.md is captured somewhere (not lost in summarization)
- [ ] MIGRATION-NOTES.md explains where each piece of the original lives now

## Step 5: Log the Bootstrap

After bootstrap completes, update VERSION-LOG.md (in the archetype/ folder) to record what was done. If VERSION-LOG.md doesn't exist, create it.

Append a bootstrap entry:

```
## Bootstrap

Date: [today's date]
Type: [new project / existing project migration]
Tech stack: [the tech stack chosen]
Files generated:
- References.md ([word count] words)
- feature-tree.md ([number of systems] systems, [number of features] features)
- [for existing projects] conventions/overrides/ ([number] files)
- [for existing projects] protocols/ ([number] files)
- [for existing projects] catalogs/ ([number] files)
- [for existing projects] docs/migrated/ ([number] files copied)
- [for existing projects] docs/audit/ ([number] audits, [summary: clean/minor/major/stale])
Conventions read during bootstrap: [list which convention docs were read]
Discovery questions asked: [list questions asked and answers received]
Key decisions made: [any tech stack choices, systems included/excluded, overrides noted]
```

This log ensures a future AI or developer can see exactly what happened during bootstrap, what was generated, and what decisions were made.

## What Bootstrap Does NOT Do

- Does not create code or foundational systems (Phase 2: Scaffold)
- Does not modify existing code (for existing projects)
- Does not set up CI/CD (part of scaffolding)

Bootstrap generates the map. Scaffolding builds what the map describes.

## Next Step

Proceed to scaffolding/SCAFFOLD.md to build the foundational systems.
