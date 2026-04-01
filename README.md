# Archetype - AI Development Framework

A layered knowledge system for AI-assisted software development. Applies to any language, framework, or AI assistant.

## How It Works

4 phases. Each phase produces artifacts that the next phase builds on.

```
Phase 1: BOOTSTRAP → onboard a project (tech stack, architecture decisions)
Phase 2: SCAFFOLD  → build foundational systems (error, theme, API, auth, etc.)
Phase 3: DEVELOP   → build features on top of scaffolding
Phase 4: MAINTAIN  → audit feature tree, update docs, evolve conventions
```

## Structure

```
├── CLAUDE.md                # The enforcer. Rules with redirects to conventions.
├── Conventions.md            # Index of all conventions with links.
├── conventions/              # Convention docs (framework-agnostic principles)
│   ├── 00-reusability.md     # Meta-convention: everything built once
│   └── 01-22.md              # 22 core conventions
│
├── bootstrap/                # Phase 1: project onboarding
│   └── ONBOARD.md            # New project + existing project paths
│
├── scaffolding/              # Phase 2: foundational systems
│   └── SCAFFOLD.md           # Ordered build with verification at each step
│
├── development/              # Phase 3 & 4: ongoing work
│   ├── DEVELOP.md            # Feature development workflow
│   └── MAINTAIN.md           # Audit, documentation, convention evolution
│
└── templates/                # Reusable templates
    ├── references-frontend.md  # References.md for frontend projects
    ├── references-backend.md   # References.md for backend projects
    ├── feature-tree.md         # Feature tree template
    ├── hooks-spec.md           # Hook specifications
    └── convention-template.md  # Template for new conventions
```

## Per-Project Output

```
your-project/
├── CLAUDE.md                # Copied from framework
├── Conventions.md            # Copied from framework
├── conventions/              # Copied from framework
├── References.md             # Generated at bootstrap (project-specific)
├── feature-tree.md           # Living map, auto-maintained by hooks
├── docs/
│   ├── systems/              # Generated at scaffolding (one per foundational system)
│   └── features/             # Generated during development (one per feature)
└── src/                      # Your code
```

## Usage

1. Copy framework files into your project (see bootstrap/ONBOARD.md)
2. Bootstrap (Phase 1) → generates References.md and feature-tree.md
3. Scaffold (Phase 2) → builds foundational systems with docs
4. Develop (Phase 3) → build features, maintain feature tree
5. Maintain (Phase 4) → audit periodically, evolve as needed
