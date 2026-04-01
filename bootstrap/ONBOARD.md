# Phase 1: Bootstrap

This prompt onboards a new project into the framework. Run once at project creation.

## Prerequisites

- Tech stack decided (framework, language, UI library, state management, etc.)
- Project purpose defined (what the app does, who it's for)
- This framework's CLAUDE.md, Conventions.md, and conventions/ copied into the project

## Bootstrapping Prompt

Use this prompt with your AI assistant to generate References.md:

---

Read Conventions.md and all convention docs in conventions/. Then answer these questions about this project:

1. What is the project? (name, purpose, one-line description)
2. What tech stack are we using? (framework, language, UI library, state management, data fetching, validation, bundler, testing, package manager)
3. What are the dev/build/test/deploy commands?
4. Are there any known architecture decisions already made? (ADRs, team conventions, constraints)

Based on your answers, generate a References.md using the template at templates/references-frontend.md (or references-backend.md). For each convention, describe HOW the foundational system will be implemented in this tech stack.

Also generate:
- An empty feature-tree.md using the template at templates/feature-tree.md
- A docs/systems/ directory (empty, ready for scaffolding phase)
- A docs/features/ directory (empty, ready for development phase)

---

## Checklist

After bootstrap, verify these exist:

- [ ] CLAUDE.md copied from framework
- [ ] Conventions.md copied from framework
- [ ] conventions/ directory copied from framework
- [ ] References.md generated with all sections filled
- [ ] feature-tree.md initialized (foundational systems listed as "not started")
- [ ] docs/systems/ directory created (empty)
- [ ] docs/features/ directory created (empty)
- [ ] .claude/ hooks directory created (if using Claude Code)

## What Bootstrap Does NOT Do

- Does not create any code or foundational systems (that's Phase 2: Scaffold)
- Does not set up CI/CD (that's part of scaffolding)
- Does not create features (that's Phase 3: Develop)

Bootstrap is documentation only. It generates the map. Scaffolding builds what the map describes.
