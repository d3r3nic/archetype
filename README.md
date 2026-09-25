# Archetype - AI Development Framework

A layered knowledge system for AI-assisted software development. It guides research, decisions and verification around the owner's goals. Adapt the relevant guidance to the project; the included playbooks and checks cover particular project shapes, not every language or runtime.

## Quick Start

### New project

```bash
# Single project (frontend, backend, or mobile):
git clone https://github.com/d3r3nic/archetype.git /tmp/archetype
mkdir my-project
/tmp/archetype/inject.sh "$PWD/my-project"

# Fullstack (separate frontend + backend units, each with its own engine folder):
mkdir -p my-project/frontend my-project/backend
/tmp/archetype/inject.sh "$PWD/my-project/frontend"
/tmp/archetype/inject.sh "$PWD/my-project/backend"
```

The framework lands in `my-project/archetype/`; the project root, its README, and its license stay the project's own.

### Existing project (safe migration)

Use the inject script. It installs the framework in a subfolder and preserves existing root AGENTS.md/CLAUDE.md guidance in .pre-archetype backups before replacing those entry points. Symlinks and backup collisions are refused before writes; other project files remain in place.

```bash
git clone https://github.com/d3r3nic/archetype.git /tmp/archetype
cd /tmp/archetype
./inject.sh /path/to/your/existing-project

# Custom subfolder name:
./inject.sh /path/to/your/existing-project archetype-migration
```

The framework lands in `your-project/archetype/`. Run the existing-project bootstrap from there.

The framework's LICENSE and NOTICE travel in the engine folder and cover the framework files. An older full-clone install carries them at its root: if that project needs its own license, rename them to LICENSE-ARCHETYPE and NOTICE-ARCHETYPE and add yours.

Then tell your AI assistant:

> Read archetype/bootstrap/ONBOARD.md and help me set up this project. I want to build [describe your idea].

The AI interviews you about the intended outcome, researches viable approaches against your constraints, and records the chosen path in project context such as References.md and feature-tree.md.

## Workflow coverage

Bootstrap and the frontend scaffold declare automated step routes. Backend, mobile and platform scaffolding, feature development and maintenance use the implementer's existing task or project plan for sequencing, checks and manual dependency review under development/TASKS.md. These workflows can be followed without converting them into runner metadata; their required verification still applies. Do not infer full project completion from a completed bootstrap ledger.

## Shared task rules and updates

[Repository adoption](bootstrap/REPOSITORIES.md), [task rules](development/TASKS.md), and [freshness rules](development/FRESHNESS.md) define the shared contract. The installed AGENTS.md holds the shared rules; CLAUDE.md imports it for hosts that load only that name. Project-root References.md, CLAUDE.md.additions, and protocols/task-context.md provide local facts and capabilities; updates preserve them. A task service and enforced freshness are consuming-project responsibilities.

Run the installed update.sh to fetch current shared rules. It is a manual latest-source updater, not an immutable release manager or automatic fleet controller. Full-clone installations at their own Git root and injected engines with parent CLAUDE.md/VERSION-LOG.md resolve automatically. For an unpacked or ambiguous layout, use `bash update.sh --project-root /absolute/project/path`; the directory must be the engine itself or its direct parent. Review the reported Project and Engine paths.

**Updating:** development/UPDATE.md says who owns which file and what a session does before and after. Root AGENTS.md holds the rules and root CLAUDE.md imports it; both are replaced by each update, and lines a project added to them are carried into CLAUDE.md.additions for audit, never deleted. An old injected updater first replaces itself: run it twice. For an old full-clone installation, use the current updater with an explicit verified root instead of running the legacy root-detection code.

**Peer coding:** two AI assistants, each in its own chat, can take turns on a branch: the one holding the writing turn implements, the other reviews every change and can repair what it finds and hand it back for another review. The owner passes one short line between the chats at each hand-over. The framework owns the rules; each project tailors them in one settings file, `peer-coding/SETTINGS.md` (which two assistants, who writes new work, the checks before each hand-over, branch naming, push and merge, extra project rules), and each branch keeps its hand-over record in `peer-coding/<branch>/`, committed with the branch and renamed `<branch>--done` when it closes for its merge. Setup asks whether a second assistant will work on the project. See [development/PEER-CODING.md](development/PEER-CODING.md); `python3 scripts/test-peer-coding.py` exercises the helper script.

Verification: `bash scripts/validate-framework.sh` checks structural consistency and runs the timeless-content check (`scripts/validate-timeless.sh`: no tool or vendor names outside Research Notes, no factory step references, no dated AI statistics, no tool-bound numeric limits, no changelog language); `python3 scripts/test-entrypoints.py` exercises distribution and preservation. Set `ARCHETYPE_LEGACY_SOURCE` to an exported previous release directory to include the two-step upgrade regression. These checks do not prove that an agent obeys instructions or that a platform enforces them.

## How It Works

4 phases. Each builds on the previous.

```
Phase 1: BOOTSTRAP → AI interviews you, picks tech stack, generates project context
Phase 2: SCAFFOLD  → builds foundational systems (error, theme, API, auth, DB, etc.)
Phase 3: DEVELOP   → build features on top of scaffolding
Phase 4: MAINTAIN  → audit feature tree, update docs, evolve conventions
```

**You don't need to be a developer.** The discovery process asks plain-English questions ("What does your app do? Who uses it? Should it work in a browser or as a phone app?") and translates your answers into technical decisions.

**The AI adjusts its explanation to you.** It researches options against your goals, constraints, existing work and willingness to operate the result. Your experience level alone does not determine a platform, architecture or hosting model.

**Two facts every session reads first.** `PROFILE.md` records how careful the project must be (its operating stage, derived from facts such as who uses it, whether the data is real, and whether anyone depends on it) and who decides technical questions (the owner, or the AI with a written record). Deferred work carries the trigger that ends the deferral, and a short floor is never deferred. Conventions #29 and #30 define both; `templates/profile.md` is the template and `scripts/validate-profile.sh` checks the record.

## What's Inside

```
├── AGENTS.md                 # Shared guidance with convention routing
├── CLAUDE.md                 # Imports AGENTS.md for hosts that load only this name
├── Conventions.md             # Convention lookup index
├── LICENSE                    # Apache License 2.0
├── NOTICE                     # Copyright and license attribution
├── conventions/               # Framework-agnostic convention docs
│   ├── 00-reusability.md      # Meta: evaluate reuse and abstraction in context
│   ├── 01-31.md               # Project setup, git, architecture, components, state,
│   │                          # styling, types, errors, API, contract, authentication,
│   │                          # testing, performance, accessibility, CI/CD, documentation,
│   │                          # context management, verification, steering,
│   │                          # forms, routing, design system, app security, authorization,
│   │                          # automated enforcement, pulse monitor, design foundation,
│   │                          # config-driven brand and content, interface craft
│   └── (see Conventions.md)
│
├── bootstrap/ONBOARD.md       # Phase 1: discovery interview + project setup
├── scaffolding/SCAFFOLD.md    # Phase 2: build foundational systems in order
├── development/
│   ├── DEVELOP.md             # Phase 3: feature development workflow
│   ├── MAINTAIN.md            # Phase 4: audit, tech debt, convention evolution
│   └── PEER-CODING.md         # Two AI assistants taking turns on a branch
│
├── libraries/                 # Optional library-specific references
│
└── templates/
    ├── references-frontend.md  # Project context template (frontend)
    ├── references-backend.md   # Project context template (backend)
    ├── references-mobile.md    # Project context template (mobile)
    ├── profile.md              # Operating stage, facts, and decision authority (PROFILE.md)
    ├── technical-debt.md       # Shortcuts and deferrals with triggers
    ├── feature-tree.md         # Living project map template
    ├── feature-doc-template.md # Feature documentation template
    ├── hooks-spec.md           # Auto-documentation hooks
    ├── global-claude.md        # Personal behavioral rules (~/.claude/CLAUDE.md)
    └── convention-template.md  # Template for adding new conventions
```

## What Your Project Gets

For a custom application using the included feature-oriented scaffold, the resulting project can look like this. Choose a different structure when its runtime and responsibilities warrant it:

```
your-project/
├── AGENTS.md                 # Shared guidance (from framework, replaced by updates)
├── CLAUDE.md                 # Imports AGENTS.md (from framework, replaced by updates)
├── CLAUDE.md.additions        # YOUR project's own standing rules
├── archetype/                 # The engine: conventions, playbooks, templates, scripts (from framework)
├── conventions/overrides/     # YOUR project-specific rules per convention, when needed
├── PROFILE.md                 # YOUR operating stage and who decides technical questions
├── References.md              # YOUR project's tech stack, systems, commands
├── feature-tree.md            # Living map of YOUR systems and features
├── peer-coding/               # When two AI assistants take turns: SETTINGS.md, and one hand-over folder per branch
├── .env.example               # Required environment variables documented
├── docs/
│   ├── systems/               # One doc per foundational system (how to use it)
│   └── features/              # One doc per feature (what, why, how)
└── src/
    ├── shared/                # Foundational systems (error, API, auth, theme, etc.)
    └── features/              # Feature code (self-contained, plugs into shared)
```

inject.sh installs the framework files into the engine folder (`archetype/` by default), LICENSE and NOTICE with them. The managed AGENTS.md and CLAUDE.md entry points are also written to the project root and carry the same license.

## Key Principles

- **Investigate before choosing.** Understand the purpose, inspect existing work and research material uncertainty. Current evidence may overturn the first idea.
- **Patterns need context.** Reuse, abstraction, architecture and visual style are choices to justify. Respect accepted project commitments; record consequential changes and their dependencies.
- **The owner sets the intent.** The AI recommends and implements within the recorded authority. Supplied requirements survive delegation of the look.
- **Evidence supports completion.** Verify behavior and inspect the resulting interface. Record limits honestly; a script cannot certify judgment or prove that instructions were read.
- **Read what the work needs.** The root and playbooks route relevant knowledge; current facts have one authoritative home, with links for other readers.
- **Recover when the basis changes.** Declared decisions and inputs identify affected work. Preserve history and unrelated work while rechecking dependent evidence.

## License

Apache License 2.0. See LICENSE and NOTICE.

The license covers the framework files in this repository, the engine folder they install into a project, and verbatim copies of framework files placed elsewhere in a project. It does not cover the project you build with them: your project's code, content, and data stay yours, and a template you copy and fill in with your project's facts is your content, not a framework file.

Keep LICENSE and NOTICE with the framework files when a project that carries them is shared. The installer places both inside the engine folder. The updater adds them only when both are missing, never replaces a copy you changed, and in a full-clone layout installs them as LICENSE-ARCHETYPE and NOTICE-ARCHETYPE so your own license file is never touched. An engine installed before this release receives them on the update run after its updater has replaced itself (see the two-step note above).
