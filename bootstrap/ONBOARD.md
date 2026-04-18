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
- Is this a product you want to ship, or a project to learn a specific technology? (If learning a technology, that's a legitimate reason to use that stack even when a platform would be simpler — but note it explicitly so Step 3 can handle it correctly.)

**Proactive learning-intent detection:** If the user's OPENING message declares enterprise or complex infrastructure (Kubernetes, Redis, Kafka, service mesh, multi-region, microservices, self-managed clusters) for a personal-scale or small-scale project (one user, a blog, a single-person tool, a portfolio), ask the ship-vs-learn question in your FIRST reply, not after red flags fire in later turns. Pattern: solo + enterprise-infra = learning intent >80% of the time. Surface it early so the rest of discovery proceeds with the right frame.

**Group 2 - Where does it run?**
- Should this work in a web browser? (like Gmail, Twitter)
- Should this be a phone app? (like Instagram, Uber)
- Should this be a desktop application? (like Photoshop, Slack desktop)
- Or some combination?

If the user says "phone app" or "works on my phone," do NOT silently pick a stack. Run the mobile disambiguation and decision tree — full detail in `bootstrap/RED-FLAGS.md` "Mobile Disambiguation" section. Three distinct choices: responsive web (cheapest), PWA (installable web + offline), native (App Store + native device APIs). Default for "I don't know" = responsive.

**Mobile decision tree — pattern:**
- If user names a native-only capability (HealthKit/Google Fit, haptics, biometrics, BLE, deep OS integration) → native.
- If user wants installability + offline but no native-device APIs → PWA.
- If user just wants the site to work on phones → responsive.
- If ambiguous → ask explicitly. Do not guess.

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

If the user answers vaguely ("I dunno", "not sure", "I guess not"), DEFAULT TO ASSUMING REGULATED DATA. A wrong "no" generates a non-compliant stack caught only at audit; a wrong "yes" generates overkill-but-safe. Disambiguation question + full rule in `bootstrap/RED-FLAGS.md` "Vague-Answer Rules" section.

**Deploy gate:** if regulated-data is default-assumed-yes and never affirmatively answered, scaffolding and deploy (Phase 2+) must halt. Record in `VERSION-LOG.md` as open pre-production gate. Deflections do not resolve. See RED-FLAGS.md "Deploy Gate" section.

**Budget-vague:** parallels regulated-vague. See RED-FLAGS.md "Vague budget answer" section.

**Vague stack preference** ("use whatever", "I don't care"): not a choice, a deflection. Apply Step 3 default (platform if one covers 80%+, minimum-viable custom otherwise). See RED-FLAGS.md.

### How the AI decides (read the user's knowledge level):

The AI should gauge the user's technical experience from how they talk. Adjust choices accordingly:

**Non-technical user** (says things like "I don't know how apps work", "I heard AI can help"):
- Choose managed / BaaS services that require zero DevOps knowledge
- Database: a managed PostgreSQL with auth + storage built in, or SQLite for simple single-user apps
- Hosting: a managed frontend platform + a managed backend/app platform
- Auth: a fully-managed drop-in auth provider
- Category shape is what matters; research current market leaders at bootstrap time. These ARE production-level tiers — they just don't require server management knowledge.

**Developer with some experience** (knows frameworks, doesn't know DevOps):
- Choose cloud platforms with simple deployment and managed databases
- Auth: a managed identity provider (consumer or B2B category depending on use case)
- Migratable to self-managed cloud later as needs grow
- Research current options at bootstrap time.

**Experienced developer / team with DevOps knowledge** (mentions AWS, cloud, infrastructure):
- Choose a major cloud provider with full control
- Database: managed database service on that cloud
- Auth: cloud-native managed auth or a compliance-certified managed auth broker
- Infrastructure as code (reproducible, auditable)
- CI/CD: automated pipeline to the cloud provider
- Full monitoring, logging, alerting

**Regulated data** (HIPAA, SOC2, PCI, GDPR, CCPA, financial regulations, sector-specific privacy laws):

FIRST: identify the regime. Different regimes require different controls, vendor agreements, and evidence. Research current requirements and vendor options for the specific regime at bootstrap time — do NOT rely on training-data-era recommendations.

SECOND: run Step 3 platform research. For most regulated domains, a compliance-ready vertical SaaS exists and solves 80%+ of the use case without custom engineering. Platforms with signed BAA (HIPAA), subprocessor+attestation (SOC 2), or equivalent compliance artifacts for the regime are the first choice. Custom is the last resort for regulated data.

THIRD — only if custom is genuinely required (product logic no platform offers, scale exceeds platform tier, multi-system integration):
- Cloud provider with the right compliance certifications AND signed vendor agreement for the regime
- Database: managed, encrypted at rest and in transit
- Auth: compliance-certified managed auth (research current providers — enterprise auth categories include HIPAA-eligible managed auth, SAML-capable B2B auth brokers, enterprise identity providers)
- Infrastructure as code (reproducible, auditable)
- Audit trails, access controls, incident response — mandatory for every regime
- Budget reality: compliance-grade infrastructure has a meaningful monthly floor (varies by regime — HIPAA minimum differs from SOC 2 Type 2 minimum differs from PCI). Research current vendor pricing. If the user cannot absorb it, platform is the only correct answer — surface this explicitly, do not scaffold custom.

**Compliance regime details routed from bootstrap/RED-FLAGS.md when a specific regime is confirmed.**

### How to translate answers into technical decisions:

| Answer | Technical Decision |
|--------|-------------------|
| Web browser app | Frontend: web framework (React, Vue, Svelte, etc.) |
| Phone app (confirmed native) | Mobile: React Native + Expo OR Flutter OR native iOS/Android |
| Phone app (PWA, installable from browser) | Web stack (React/Vue/Svelte) + PWA manifest + service worker |
| Works on phone (responsive web) | Web stack, responsive design, no mobile-specific tooling |
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
| No DevOps knowledge | Managed / BaaS services category (research current market leaders) |
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

If the user introduces a new requirement during discovery (multi-user after "just for me", SSO after "personal", mobile after "web", compliance after "nothing sensitive"), STOP the linear flow: acknowledge the change, re-ask affected groups, re-run Step 3 research. Full playbook + resistant-user handling in `bootstrap/RED-FLAGS.md` "Scope-Change Handler" section.

Do not proceed to Step 4 (file generation) until discovery is coherent with the current scope.

### Red flag combinations — surface before Step 3

Some requirement combinations are incompatible, anti-pattern, or signal hidden complexity. If the user's answers hit any, surface the conflict BEFORE moving to Step 3.

**Full 10-row table and per-row playbook in `bootstrap/RED-FLAGS.md`.** Categories covered:
- Free + regulated data (compliance floor makes this impossible)
- Offline + regulated data (device-loss compliance risk)
- Solo user + enterprise infra (scale mismatch — unless learning, see LEARNING-PROJECTS.md)
- Real-time + static hosting (infrastructure mismatch)
- Multi-user team + solo stack (feature/stack mismatch)
- "All equally important" + deadline (priority conflict)
- Enterprise SSO + consumer auth stack (provider mismatch)
- Compliance claim + no vendor-agreement discussion (user error)
- Enterprise SSO + user is not admin on the IdP tenant (provisioning dependency)
- Priority ranking refused (applies default order)

Multiple red flags = strong signal that platform Option A is correct. Do not proceed to Step 4 custom build when scale, compliance, or budget fundamentally don't fit a custom path.

## Step 3: Research Before Deciding (DO NOT SKIP)

After discovery, the AI has the answers. But DO NOT pick a tech stack yet. First, research whether a custom build is even the right approach.

### The AI must consider: does the user actually need a custom app?

Many projects are better served by existing platforms than custom code. The AI must be honest about this, even though the framework exists to scaffold custom projects. Over-engineering is a violation of convention #0 (reusability — don't build what already exists, whether inside the project OR as a market-available platform).

**Exception: learning projects.** If Group 1 revealed this is a project to learn a specific technology (not a product to ship), platform-vs-custom research is bypassed — the technology choice IS the point. Scale-vs-cost still matters: recommend the cheapest way to exercise the target technology (local tooling before cloud). Full flow, detection heuristics, and References.md documentation template in `bootstrap/LEARNING-PROJECTS.md`.

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
- A BaaS (Backend-as-a-Service) platform + custom frontend

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

After the user confirms their build approach, the AI generates the project files. The generation path depends on whether the user picked a platform (Option A/B from Step 3) or a custom build (Option C).

### If the user picked a PLATFORM (Option A or B from Step 3):

The framework's scaffolding phase does NOT apply. There is no tech stack to document, no foundational systems to build, no folder structure to scaffold. The user's project is configuration and content within a third-party platform.

Generate:
- `References.md` using `templates/references-platform.md` (NOT the frontend/backend/mobile templates — those are for custom builds)
- `feature-tree.md` reshaped as a configuration checklist for the chosen platform (not a systems map)
- `VERSION-LOG.md` with `Type: platform / {platform-name}` in the bootstrap entry
- No `.gitignore`, no `git init`, no `docs/systems/`, no `docs/features/` — the framework doesn't manage the platform's internals

Conventions that still apply:
- #2 (Git) — if the user will version-control platform config files (theme customizations, export files)
- #16 (Documentation) — the References.md IS their documentation
- #23 (App Security) — admin account, 2FA, PII handling within the platform
- #24 (Authorization) — role settings within the platform

Conventions that do NOT apply: everything else (architecture, components, state, styling, types, errors, API, testing, build/CI, etc.). Those are owned by the platform.

Stop after generating References.md, feature-tree.md, and VERSION-LOG.md. Help the user sign up for the platform and walk through initial configuration.

### If the user picked a CUSTOM BUILD (Option C from Step 3):

Proceed below. This is the path the framework was originally built around.

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

User: "I'm building a healthcare SaaS. React frontend, cloud-hosted backend, managed Postgres, cloud-managed auth. I know the stack."

AI: "Stack noted. Before I generate files, Step 3 still applies — even with a declared stack. For healthcare SaaS specifically, HIPAA-compliant vertical platforms often cover 80%+ of typical use cases (patient portals, intake, scheduling, notes) with BAAs included. Let me confirm: is the core of your product something those platforms already do, or is it unique logic on top of that (AI analysis, custom workflows, proprietary algorithms)? If it's the latter, your stack is a reasonable fit. If it's the former, start from the platform and build only the unique layer. Research current HIPAA vertical-SaaS options to make sure the recommendation is up-to-date."

User: "Custom — the core is our AI analysis pipeline, no platform does that."

AI: "Confirmed custom build is correct. Generating References.md with the declared stack, and I'll flag HIPAA-specific requirements inline (BAA with the cloud provider, encryption at rest, MFA on auth, audit logging, PII log-scrubbing)."

**Key takeaway:** even for a confident user with a declared stack, Step 3 still runs. A 30-second confirmation ("is this custom logic or platform-served?") prevents scaffolding weeks of infra for a use case a platform already solves.

---

### For an EXISTING project:

Full migration flow — Parts A (scan codebase), B (extract rules), C (cross-reference), D (doc discovery + audit) — lives in `bootstrap/EXISTING-PROJECT.md`. Follow it end-to-end.

**Critical:** migration preserves EVERY rule. Nothing gets lost. If you find yourself summarizing, stop. Run `scripts/validate-migration.sh` before committing — it checks for summarization, missing INDEX pointers, drifted migrated copies, and absent convention references. Any validator failure = re-extract, do not paper over.

---

## Step 5: Set Up Hooks (optional - can be done later)

Hooks automatically remind the AI to update documentation and run verification. See templates/hooks-spec.md for what hooks to create. This step can be deferred to scaffolding if you want to get started faster.

## Checklist

After bootstrap, verify:

- [ ] CLAUDE.md in project root (or in archetype/ subfolder if existing project)
- [ ] Conventions.md in project root (or in archetype/)
- [ ] conventions/ directory with all framework convention docs (unmodified)
- [ ] References.md generated (use `references-platform.md` for platform choice, `references-frontend/backend/mobile.md` for custom)
- [ ] feature-tree.md initialized (use `feature-tree-platform.md` for platform choice, `feature-tree.md` for custom)
- [ ] VERSION-LOG.md bootstrap entry written (with `Type: platform / {name}` or `Type: custom`)
- [ ] **For CUSTOM BUILDS ONLY:** docs/systems/ directory created
- [ ] **For CUSTOM BUILDS ONLY:** docs/features/ directory created
- [ ] **For CUSTOM BUILDS ONLY:** Git initialized with .gitignore (new project only)
- [ ] **For REGULATED DATA (yes or default-assumed):** regulated-data question explicitly answered OR logged in VERSION-LOG as a pre-production gate

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
