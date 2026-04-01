# AI Development Framework

A layered knowledge system for AI-assisted software development. Applies to any language, framework, or AI assistant.

## How It Works

4 phases. Each phase produces artifacts that the next phase builds on.

```
Phase 1: BOOTSTRAP → onboard a project (tech stack, architecture decisions)
Phase 2: SCAFFOLD  → build foundational systems (error, theme, API, auth, etc.)
Phase 3: DEVELOP   → build features on top of scaffolding
Phase 4: MAINTAIN   → audit, update feature tree, evolve conventions
```

## Structure

```
├── CLAUDE.md               # The enforcer. Lean rules with redirects.
├── Conventions.md           # Index of all conventions with links.
├── conventions/             # Convention docs (framework-agnostic principles)
│   ├── 00-reusability.md    # Meta-convention: everything built once
│   ├── 01-22.md             # 22 core conventions
│   └── (see Conventions.md for full list)
│
├── bootstrap/               # Phase 1: project onboarding
│   ├── ONBOARD.md           # Bootstrapping prompt and checklist
│   └── (generates → References.md in your project)
│
├── scaffolding/             # Phase 2: foundational systems
│   ├── SCAFFOLD.md          # Scaffolding prompt and checklist
│   └── (generates → foundational systems + system docs)
│
└── templates/               # Reusable templates
    ├── references-frontend.md
    ├── references-backend.md
    ├── feature-tree.md       # Feature tree template
    └── convention-template.md
```

## Per-Project Output (what gets generated in YOUR project)

```
your-project/
├── CLAUDE.md               # Copied from framework (the enforcer)
├── Conventions.md           # Copied from framework (the index)
├── conventions/             # Copied from framework (the principles)
├── References.md            # Generated at bootstrap (project-specific)
├── docs/
│   ├── systems/             # Generated at scaffolding (one per foundational system)
│   │   ├── error-system.md
│   │   ├── theme-system.md
│   │   ├── api-layer.md
│   │   └── ...
│   └── features/            # Generated during development (one per feature)
│       ├── authentication.md
│       ├── dashboard.md
│       └── ...
├── feature-tree.md          # Living map, auto-maintained by hooks
└── src/                     # Your code
```

## Usage

1. Copy CLAUDE.md, Conventions.md, and conventions/ into your project
2. Run bootstrap (Phase 1) → generates References.md
3. Run scaffolding (Phase 2) → builds foundational systems
4. Develop features (Phase 3) → feature tree maintained automatically
