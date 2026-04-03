# Phase 1: Bootstrap

Onboard a project into the framework. Run once at project creation or when adopting the framework on an existing project.

## Prerequisites

- Tech stack decided (framework, language, UI library, state management, etc.)
- Project purpose defined (what the app does, who it's for)

## Step 1: Initialize Project

Run from the directory where you want the project created:

```bash
# For a frontend project:
git clone https://github.com/d3r3nic/archetype.git my-project-name
cd my-project-name
rm -rf .git libraries/  # remove archetype git history and optional libraries

# For a backend project:
git clone https://github.com/d3r3nic/archetype.git my-api-name
cd my-api-name
rm -rf .git libraries/

# For a fullstack project (frontend + backend):
mkdir my-project && cd my-project
git clone https://github.com/d3r3nic/archetype.git frontend
git clone https://github.com/d3r3nic/archetype.git backend
rm -rf frontend/.git frontend/libraries/ backend/.git backend/libraries/
```

After cloning, your project has:
```
your-project/
├── CLAUDE.md          # the enforcer
├── Conventions.md     # convention index
├── conventions/       # 23 convention docs
├── bootstrap/         # this file
├── scaffolding/       # scaffold guide
├── development/       # develop + maintain guides
└── templates/         # references, feature-tree, hooks
```

For fullstack: each endpoint (frontend/, backend/) gets its own copy of the framework. They share conventions but have separate References.md, feature-tree.md, and docs/.

## Step 2: Generate Project Context

### For a NEW project:

Use this prompt with your AI assistant:

---

Read Conventions.md to understand the convention index. Do NOT read all 23 convention docs upfront. You will read each one as needed during References.md generation.

Then I'll tell you about this project:

1. What is the project? (name, purpose, one-line description)
2. What tech stack are we using? (framework, language, UI library, state management, data fetching, validation, bundler, testing, package manager)
3. What are the dev/build/test/deploy commands?
4. Are there any architecture decisions already made?

Based on my answers, generate:
- References.md using the template at templates/references-frontend.md (or references-backend.md or references-mobile.md)
- feature-tree.md using the template at templates/feature-tree.md (foundational systems listed as "not started")
- docs/systems/ directory (empty)
- docs/features/ directory (empty)
- .gitignore appropriate for the tech stack
- Initialize git with an initial commit

For each foundational system section in References.md:
1. Read the corresponding convention doc (only that one, not all of them)
2. Read its Research Notes section
3. Research the current best practices for that convention in the chosen tech stack (do not rely on training data alone - search for the latest patterns)
4. Describe HOW the system will be implemented based on your research findings
5. Report what you researched and what you found (so the user can verify)
6. Leave the Location fields as [to be created in scaffolding]

---

### For an EXISTING project:

Use this prompt with your AI assistant:

---

Read Conventions.md and all convention docs in conventions/. Then scan this codebase to understand what already exists.

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

## Next Step

Proceed to scaffolding/SCAFFOLD.md to build the foundational systems.
