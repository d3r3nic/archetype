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

Use the inject script. It copies the framework into a subfolder of your existing project without modifying any existing files.

```bash
git clone https://github.com/d3r3nic/archetype.git /tmp/archetype
cd /tmp/archetype
./inject.sh /path/to/your/existing-project

# Custom subfolder name:
./inject.sh /path/to/your/existing-project archetype-migration
```

The framework lands in `your-project/archetype/`. Run the existing-project bootstrap from there.

Then tell your AI assistant:

> Read bootstrap/ONBOARD.md and help me set up this project. I want to build [describe your idea].

The AI will interview you about what you're building, pick the right tech stack for your experience level, and generate your project's References.md and feature-tree.md.

## How It Works

4 phases. Each builds on the previous.

```
Phase 1: BOOTSTRAP → AI interviews you, picks tech stack, generates project context
Phase 2: SCAFFOLD  → builds foundational systems (error, theme, API, auth, DB, etc.)
Phase 3: DEVELOP   → build features on top of scaffolding
Phase 4: MAINTAIN  → audit feature tree, update docs, evolve conventions
```

**You don't need to be a developer.** The discovery process asks plain-English questions ("What does your app do? Who uses it? Should it work in a browser or as a phone app?") and translates your answers into technical decisions.

**The AI adjusts to your experience level.** A bakery owner gets Supabase + Vercel (zero server management). A developer gets managed cloud. An enterprise team gets AWS with full infrastructure control.

## What's Inside

```
├── CLAUDE.md                 # 21 enforcement rules with redirects to conventions
├── Conventions.md             # Index of 28 conventions
├── conventions/               # 28 framework-agnostic convention docs
│   ├── 00-reusability.md      # Meta: everything built once, configured for context
│   ├── 01-27.md               # Project setup, git, architecture, components, state,
│   │                          # styling, types, errors, API, contract, authentication,
│   │                          # testing, performance, accessibility, CI/CD, documentation,
│   │                          # context management, verification, steering,
│   │                          # forms, routing, design system, app security, authorization,
│   │                          # automated enforcement, pulse monitor
│   └── (see Conventions.md)
│
├── bootstrap/ONBOARD.md       # Phase 1: discovery interview + project setup
├── scaffolding/SCAFFOLD.md    # Phase 2: build foundational systems in order
├── development/
│   ├── DEVELOP.md             # Phase 3: feature development workflow
│   └── MAINTAIN.md            # Phase 4: audit, tech debt, convention evolution
│
├── libraries/                 # Optional framework-specific references (React, etc.)
│
└── templates/
    ├── references-frontend.md  # Project context template (frontend)
    ├── references-backend.md   # Project context template (backend)
    ├── references-mobile.md    # Project context template (mobile)
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

## Key Principles

- **Everything built once, configured for context.** One error system, one API layer, one theme, one auth system. Features plug in.
- **Use established UI libraries.** Don't reinvent buttons and modals. Configure MUI/Chakra/Radix with your theme (light + dark), wrap, export.
- **Dark mode always.** The theme supports light and dark from day one.
- **Conventions describe WHAT, not HOW.** The bootstrapping AI researches the latest patterns for your specific tech stack.
- **Feature tree as living map.** Every system and feature tracked. New AI agents read it to understand the project instantly.
- **Documentation flows with code.** Not after. System docs, feature docs, and feature tree updated as you build.
