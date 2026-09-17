# Archetype - AI Development Framework

A layered knowledge system for AI-assisted software development. Works with any language, framework, or AI assistant. From vibe coders to production teams.

## Quick Start

### New project

```bash
# Single project (frontend, backend, or mobile):
git clone https://github.com/d3r3nic/archetype.git my-project
cd my-project && rm -rf .git libraries/

# Fullstack (separate frontend + backend):
mkdir my-project && cd my-project
git clone https://github.com/d3r3nic/archetype.git frontend
git clone https://github.com/d3r3nic/archetype.git backend
rm -rf frontend/.git frontend/libraries/ backend/.git backend/libraries/
```

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

A full clone brings the framework's LICENSE and NOTICE with it. They cover the framework files. If your project needs its own license, rename them to LICENSE-ARCHETYPE and NOTICE-ARCHETYPE and add yours.

Then tell your AI assistant:

> Read bootstrap/ONBOARD.md and help me set up this project. I want to build [describe your idea].

The AI will interview you about what you're building, pick the right tech stack for your experience level, and generate your project's References.md and feature-tree.md.

## Shared task rules and updates

[Repository adoption](bootstrap/REPOSITORIES.md), [task rules](development/TASKS.md), and [freshness rules](development/FRESHNESS.md) define the shared contract. The installed AGENTS.md loads CLAUDE.md explicitly. Project-root References.md, CLAUDE.md.additions, and protocols/task-context.md provide local facts and capabilities; updates preserve them. A task service and enforced freshness are consuming-project responsibilities.

Run the installed update.sh to fetch current shared rules. It is a manual latest-source updater, not an immutable release manager or automatic fleet controller. Full-clone installations at their own Git root and injected engines with parent CLAUDE.md/VERSION-LOG.md resolve automatically. For an unpacked or ambiguous layout, use `bash update.sh --project-root /absolute/project/path`; the directory must be the engine itself or its direct parent. Review the reported Project and Engine paths.

**Upgrading the previous release:** an old injected updater first replaces itself, then its next invocation installs the new AGENTS entry points. Run it twice and verify root and engine AGENTS.md. If root AGENTS.md already contains local guidance, preserve it, migrate the rules to project-owned files, and install the managed entry point before updating; do not delete guidance to satisfy the check. For an old full-clone installation, use the current updater with an explicit verified root instead of running the legacy root-detection code.

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

**The AI adjusts to your experience level.** A bakery owner gets a managed platform with zero server management. A developer gets managed cloud. An enterprise team gets full infrastructure control.

**Two facts every session reads first.** `PROFILE.md` records how careful the project must be (its operating stage, derived from facts such as who uses it, whether the data is real, and whether anyone depends on it) and who decides technical questions (the owner, or the AI with a written record). Deferred work carries the trigger that ends the deferral, and a short floor is never deferred. Conventions #29 and #30 define both; `templates/profile.md` is the template and `scripts/validate-profile.sh` checks the record.

## What's Inside

```
├── CLAUDE.md                 # Shared enforcer with convention routing
├── Conventions.md             # Convention lookup index
├── LICENSE                    # Apache License 2.0
├── NOTICE                     # Copyright and license attribution
├── conventions/               # Framework-agnostic convention docs
│   ├── 00-reusability.md      # Meta: everything built once, configured for context
│   ├── 01-30.md               # Project setup, git, architecture, components, state,
│   │                          # styling, types, errors, API, contract, authentication,
│   │                          # testing, performance, accessibility, CI/CD, documentation,
│   │                          # context management, verification, steering,
│   │                          # forms, routing, design system, app security, authorization,
│   │                          # automated enforcement, pulse monitor, design foundation,
│   │                          # config-driven brand and content
│   └── (see Conventions.md)
│
├── bootstrap/ONBOARD.md       # Phase 1: discovery interview + project setup
├── scaffolding/SCAFFOLD.md    # Phase 2: build foundational systems in order
├── development/
│   ├── DEVELOP.md             # Phase 3: feature development workflow
│   └── MAINTAIN.md            # Phase 4: audit, tech debt, convention evolution
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

After bootstrap and scaffolding, your project has:

```
your-project/
├── CLAUDE.md                 # Enforcer (from framework)
├── Conventions.md             # Convention index (from framework)
├── conventions/               # Convention docs (from framework)
├── References.md              # YOUR project's tech stack, systems, commands
├── feature-tree.md            # Living map of YOUR systems and features
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

- **Everything built once, configured for context.** One error system, one API layer, one theme, one auth system. Features plug in.
- **Prefer an established component foundation.** Don't reinvent buttons and modals when a fitting library exists. Configure it with your theme, wrap, export.
- **Every color scheme from day one.** The theme swaps schemes at the token layer; light and dark are the default pair.
- **Design before code; the look is the owner's pick.** The artifact, the tokens, and the profile are the brief for any design tool that runs in the project. Mockups follow the design discipline; code follows the tokens.
- **Conventions describe WHAT, not HOW.** The bootstrapping AI researches the latest patterns for your specific tech stack.
- **Feature tree as living map.** Every system and feature tracked. New AI agents read it to understand the project instantly.
- **Documentation flows with code.** Not after. System docs, feature docs, and feature tree updated as you build.

## License

Apache License 2.0. See LICENSE and NOTICE.

The license covers the framework files in this repository, the engine folder they install into a project, and verbatim copies of framework files placed elsewhere in a project. It does not cover the project you build with them: your project's code, content, and data stay yours, and a template you copy and fill in with your project's facts is your content, not a framework file.

Keep LICENSE and NOTICE with the framework files when a project that carries them is shared. The installer places both inside the engine folder. The updater adds them only when both are missing, never replaces a copy you changed, and in a full-clone layout installs them as LICENSE-ARCHETYPE and NOTICE-ARCHETYPE so your own license file is never touched. An engine installed before this release receives them on the update run after its updater has replaced itself (see the two-step note above).
