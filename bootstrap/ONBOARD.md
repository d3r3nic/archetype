# Phase 1: Bootstrap

Onboard a project into the framework. Run once at project creation or when adopting the framework on an existing project.

## Prerequisites

- Tech stack decided (framework, language, UI library, state management, etc.)
- Project purpose defined (what the app does, who it's for)

## Step 1: Copy Framework Files

Clone or copy from the archetype repo (github.com/d3r3nic/archetype):

```
your-project/
├── CLAUDE.md          # copy from archetype
├── Conventions.md     # copy from archetype
├── conventions/       # copy entire directory from archetype
├── bootstrap/         # copy (this file)
├── scaffolding/       # copy
└── templates/         # copy
```

## Step 2: Generate Project Context

### For a NEW project:

Use this prompt with your AI assistant:

---

Read Conventions.md and all convention docs in conventions/. Then I'll tell you about this project:

1. What is the project? (name, purpose, one-line description)
2. What tech stack are we using? (framework, language, UI library, state management, data fetching, validation, bundler, testing, package manager)
3. What are the dev/build/test/deploy commands?
4. Are there any architecture decisions already made?

Based on my answers, generate:
- References.md using the template at templates/references-frontend.md (or references-backend.md)
- feature-tree.md using the template at templates/feature-tree.md (foundational systems listed as "not started")
- docs/systems/ directory (empty)
- docs/features/ directory (empty)
- .gitignore appropriate for the tech stack
- Initialize git with an initial commit

For each foundational system section in References.md, describe HOW the system will be implemented in this tech stack. Leave the Location fields as [to be created in scaffolding].

---

### For an EXISTING project:

Use this prompt with your AI assistant:

---

Read Conventions.md and all convention docs in conventions/. Then scan this codebase to understand what already exists.

For each convention (#0-#22), determine:
1. Does a foundational system for this convention already exist?
2. If yes: where does it live? Document it in References.md.
3. If partially: what exists and what's missing? Note gaps.
4. If no: mark as "not started" in feature-tree.md.

Generate:
- References.md using the template at templates/references-frontend.md (or references-backend.md), filling in actual paths for systems that already exist
- feature-tree.md with actual status of each system and all existing features mapped
- docs/systems/ with a doc for each system that already exists
- docs/features/ with a doc for each feature that already exists

For existing systems that don't fully match the convention, note the gap under "Convention Overrides" in References.md. Do not change any existing code during bootstrap.

---

## Step 3: Set Up Hooks

Create hooks based on templates/hooks-spec.md. At minimum:

- PostToolUse (Write/Edit): remind to update feature docs and feature-tree.md
- PostToolUse (TaskComplete): remind to run verification

## Checklist

After bootstrap, verify:

- [ ] CLAUDE.md in project root
- [ ] Conventions.md in project root
- [ ] conventions/ directory with all convention docs
- [ ] References.md generated with all sections filled
- [ ] feature-tree.md initialized
- [ ] docs/systems/ directory created
- [ ] docs/features/ directory created
- [ ] Git initialized with .gitignore
- [ ] Hooks configured

## What Bootstrap Does NOT Do

- Does not create code or foundational systems (Phase 2: Scaffold)
- Does not modify existing code (for existing projects)
- Does not set up CI/CD (part of scaffolding)

Bootstrap generates the map. Scaffolding builds what the map describes.
