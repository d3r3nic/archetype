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

**Regulated data** (HIPAA, SOC2, PCI, financial, privacy laws):

FIRST: run Step 3 platform research. A HIPAA/SOC2/PCI-compliant vertical SaaS almost always exists — Blueprint, Healthie, or SimplePractice for therapy; Datica or Particle Health for health data; Stripe for payments; AWS Observability with compliance for logging. Platforms with signed BAAs/certifications solve 80%+ of compliance use cases without custom engineering. Custom should be the last resort for regulated data.

ONLY IF a custom build is genuinely required (product logic no platform offers, scale exceeds platform tier, multi-system integration):
- Cloud provider with compliance certifications AND a signed BAA/equivalent (AWS, GCP, Azure)
- Database: managed, encrypted at rest and in transit (AWS RDS, Cloud SQL)
- Auth: compliance-certified managed auth (AWS Cognito, Auth0 enterprise, WorkOS)
- Infrastructure as code (SST, CDK, Terraform)
- Audit trails, access controls, incident response — mandatory
- Monitoring: CloudWatch, Datadog, or equivalent with alerting
- Budget reality: compliance-grade infrastructure costs ~$100/month minimum BEFORE engineering time. If the user cannot absorb this, a platform is the only correct answer — surface this explicitly, do not scaffold custom.

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
| Has preferences | AI respects preferences AND still runs Step 3 research. If a platform covers the use case, or scale/compliance/cost is mismatched to the preference, surface the alternatives before agreeing. User can still choose their preference — but must see the tradeoff. |
| Sensitive data (health, finance) | Compliance-grade infrastructure, encryption, audit trails |
| No DevOps knowledge | Managed services (Supabase, Vercel, Railway) |
| Knows AWS/cloud | AWS with proper architecture (preferred for production) |

### Common proven stacks (for reference):

Web frontend: React + TypeScript + Vite + Tailwind
Content sites / blogs / docs: Astro + Starlight (zero JS by default, fast)
Backend API (Node): Node.js + TypeScript + Express + Prisma + PostgreSQL
Backend API (Python): Python + FastAPI + SQLAlchemy + PostgreSQL
Backend API (C#): ASP.NET + Entity Framework + SQL Server
Mobile: React Native + Expo OR Flutter + Dart
Desktop: Electron + React OR Tauri + Svelte

### Handling scope changes mid-discovery

Users often add requirements as they think out loud. If the user introduces a new requirement during discovery (multi-user after answering "just for me", SSO after "personal project", mobile after "web only", compliance after "nothing sensitive"), STOP the linear flow and:

1. **Acknowledge the change explicitly.** "That changes things — multi-user means we need auth, permissions, and a shared data model. Earlier I was thinking solo-only." Do not silently merge the new requirement into the old plan.
2. **Re-ask the affected discovery groups.** Group 3 (users/auth/forms) if user count changed. Group 4 (scale) if scope or audience grew. Group 5 (sensitive data) if the data model changed.
3. **Re-run Step 3 research.** The previous platform/stack recommendation is invalid. Research fresh given the new scope.
4. **If the user resists re-interviewing** ("I told you already"): explain why — the earlier answer was for a different scope, and proceeding without re-asking will generate the wrong stack. Show them the specific question being re-asked and why.

Do not proceed to Step 4 (file generation) until discovery is coherent with the current scope.

### Red flag combinations — surface before Step 3

Some requirement combinations are incompatible, anti-pattern, or signal hidden complexity. If the user's answers hit any of these, surface the conflict BEFORE moving to Step 3. Do not silently proceed.

| Combination | Why it's a red flag | What to do |
|-------------|---------------------|------------|
| Free to run + regulated data (HIPAA, PCI, financial) | Compliance-grade hosting is not free. BAAs, compliant storage, encryption, audit logging — none ship on free tiers. | Step 3 Option A is the only correct answer. Present the cheapest compliant platform. Custom for $0 is not possible. |
| Offline + regulated data (PHI, PII, financial) | Offline means data on the device. Device loss, encryption failure, sync integrity, remote wipe — all compliance risks. | Challenge the requirement. Ask: "Do you need truly offline, or fast access while online? Offline with regulated data is a significant compliance burden." |
| Solo user + enterprise infra (Kubernetes, multi-region, service mesh, Kafka) | Operational burden will exceed feature work. User will bounce off the infra before shipping the product. | Surface the scale mismatch explicitly. Offer a simpler stack and quantify the complexity cost (hours of ops/week, baseline $/month). |
| Real-time + static hosting (Cloudflare Pages, GitHub Pages, S3) | Real-time (WebSocket, SSE) needs a long-lived server. Static hosts can't. | Add a managed real-time service (Pusher, Ably, Supabase Realtime) OR a stateful backend. Confirm the cost. |
| Multi-user team + "just me" stack (SQLite-only, no auth, local files) | Team features need auth, shared persistence, concurrency. Solo stacks can't handle this. | Re-run discovery Groups 3 and 4; escalate the stack. |
| "All equally important" priorities + tight deadline | If everything is top priority, nothing is. Deadlines force tradeoffs. | Force a ranking conversation before Step 3: "If you had to ship in half the time, which feature would go first?" |
| Enterprise SSO (Okta, Azure AD, SAML) + consumer auth stack (Supabase Auth, Firebase Auth default) | Enterprise SSO usually needs Auth0 enterprise, WorkOS, or Cognito — not consumer auth. | Flag the stack change before Step 3. Route to enterprise-auth research. |
| Compliance claim (HIPAA, SOC2) + no BAA / vendor-agreement discussion | Saying "HIPAA-compliant" without signed BAAs with every vendor touching the data is a common user error. | Ask about BAA plans; route to compliance-aware platforms or enterprise cloud paths. |

Multiple red flags = strong signal that platform Option A is correct. Do not proceed to Step 4 custom build when the scale, compliance, or budget fundamentally doesn't fit a custom path.

## Step 3: Research Before Deciding (DO NOT SKIP)

After discovery, the AI has the answers. But DO NOT pick a tech stack yet. First, research whether a custom build is even the right approach.

### The AI must consider: does the user actually need a custom app?

Many projects are better served by existing platforms than custom code. The AI must be honest about this, even though the framework exists to scaffold custom projects. Over-engineering is a violation of convention #0 (reusability — don't build what already exists, whether inside the project OR as a market-available platform).

Research and present these options to the user BEFORE committing:

**Option 1: Existing platform (no custom code needed)**

| User wants | Consider instead of custom code |
|---|---|
| Blog / content site | WordPress, Ghost, Astro + headless CMS |
| Online store | Shopify, WooCommerce, BigCommerce |
| Portfolio / brochure site | Squarespace, Wix, Webflow, Astro |
| Landing pages | Carrd, Webflow, Framer |
| Internal forms / workflows | Notion, Airtable, Retool, Google Forms |
| Booking / appointments | Calendly, Acuity, Square Appointments |
| Documentation site | Astro Starlight, Docusaurus, GitBook |

If an existing platform covers 80%+ of what the user needs, recommend it. Custom code should only be chosen when the user has requirements that platforms genuinely cannot meet.

**Option 2: Hybrid (platform + custom pieces)**

Sometimes the right answer is a platform for the core + custom code for specific features:
- WordPress for content + custom React frontend (headless WordPress)
- Shopify for e-commerce + custom dashboard for analytics
- Supabase for backend + custom frontend

**Option 3: Full custom build (what this framework scaffolds)**

Custom code is the right choice when:
- The app has complex business logic that platforms can't handle
- The app needs custom auth flows, HIPAA compliance, or specific security requirements
- The app is a SaaS product, dashboard, or tool with unique workflows
- The user has technical skills or a development team
- No existing platform covers even 50% of the requirements

### How to present the decision:

Research online (if capable) for the latest platform options that match the user's use case. Then present:

```
Based on what you described, here are your options:

Option A: [Platform name]
- What it does: [covers X, Y, Z of your requirements]
- What it doesn't do: [missing A, B]
- Cost: [pricing]
- Effort: [timeline]
- Best if: [use case fit]

Option B: [Different platform or hybrid approach]
- ...

Option C: Custom build with [tech stack]
- What it does: exactly what you need, fully customizable
- What it doesn't do: nothing - but you have to build and maintain everything
- Cost: development time + hosting
- Effort: [timeline estimate]
- Best if: you need full control, have complex requirements, or this is a product

My recommendation: [which option and why, based on the discovery answers]

Which direction would you like to go?
```

Wait for the user to decide. Do NOT proceed to file generation until the user confirms they want a custom build.

If the user chooses a platform (Option A or B), help them set it up. The Archetype framework's scaffolding phase doesn't apply — but the conventions around security (#23), documentation (#16), and git (#2) still do.

If the user confirms custom build (Option C), proceed to Step 4.

## Step 4: Generate Project Context

After the user confirms the custom build approach, the AI generates the project files.

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

AI: "Stack noted. Before I generate files, Step 3 still applies — even with a declared stack. For healthcare SaaS specifically, HIPAA-compliant vertical platforms like Healthie, Mend, or Bridge Patient Portal cover 80%+ of typical use cases with BAAs included. Is the core of your product something those platforms already do (patient portals, intake, scheduling, notes), or is it unique logic on top of that (AI analysis, custom workflows, proprietary algorithms)? If it's the latter, your stack is a reasonable fit and I'll proceed. If it's the former, we should start from the platform and build only the unique layer."

User: "Custom — the core is our AI analysis pipeline, no platform does that."

AI: "Confirmed custom build is correct. Generating References.md with React + SST + Prisma + Postgres + Cognito, and I'll flag HIPAA-specific requirements inline (BAA with AWS, RDS encryption at rest, Cognito MFA, audit logging, log-scrubbing)."

**Key takeaway:** even for a confident user with a declared stack, Step 3 still runs. A 30-second confirmation ("is this custom logic or platform-served?") prevents scaffolding weeks of infra for a use case a platform already solves.

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

## Step 5: Set Up Hooks (optional - can be done later)

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

## Step 6: Log the Bootstrap

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
