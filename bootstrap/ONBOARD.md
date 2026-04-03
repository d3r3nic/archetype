# Phase 1: Bootstrap

Onboard a project into the framework. Run once at project creation or when adopting the framework on an existing project.

## Prerequisites

- You know what you want to build (even just "a todo app" is enough to start)
- Tech stack chosen (or let the framework help you choose in Step 2)

## Step 1: Initialize Project

Tell your AI assistant to set up the project. Alternatively, run these commands yourself:

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

After setup, each project folder has:
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

For fullstack: each endpoint (frontend/, backend/) is a separate project with its own copy of the framework, its own References.md, feature-tree.md, and docs/. They are separate git repos. If you prefer a monorepo, put both folders under one git repo and manage them together.

## Step 2: Choose Tech Stack (if you don't have one yet)

If you already know your tech stack, skip to Step 3.

If you're unsure, here are common proven stacks to choose from:

Frontend web app:
- React + TypeScript + Vite + Tailwind + TanStack Query + Zod

Backend API:
- Node.js + TypeScript + Express/Fastify + Prisma + PostgreSQL + Zod
- Python + FastAPI + SQLAlchemy + PostgreSQL + Pydantic
- C# + ASP.NET + Entity Framework + SQL Server + FluentValidation

Mobile app:
- React Native + TypeScript + Expo
- Flutter + Dart + Riverpod

Tell your AI assistant what you want to build. It can help you pick a stack if you're not sure. Example: "I want to build a todo app with a web frontend and a backend API. What tech stack do you recommend?"

## Step 3: Generate Project Context

### For a fullstack project (frontend + backend):

Run the bootstrap prompt TWICE - once in the frontend/ folder using templates/references-frontend.md, and once in the backend/ folder using templates/references-backend.md. Each endpoint gets its own References.md and feature-tree.md.

### For a single endpoint (frontend only, backend only, or mobile):

Run the bootstrap prompt once in the project folder, using the matching template.

### Bootstrap Prompt:

Use this prompt with your AI assistant. Example answers are shown below the prompt.

---

Read Conventions.md to understand the convention index. Do NOT read all 23 convention docs upfront. You will read each one as needed during References.md generation.

I'm building [describe your project in plain English - what it does, who uses it].

My tech stack is: [list your tech stack, or say "help me choose" and describe what you want to build]

Based on my project, generate:
- References.md using the appropriate template from templates/ (references-frontend.md, references-backend.md, or references-mobile.md)
- feature-tree.md using templates/feature-tree.md (systems listed as "not started", remove systems that don't apply to this project)
- docs/systems/ directory (empty)
- docs/features/ directory (empty)
- .gitignore appropriate for the tech stack
- Initialize git with an initial commit

For each foundational system section in References.md:
1. Read the corresponding convention doc (the # number is in the section header)
2. Read its Research Notes section
3. Research the current best practices for that convention in the chosen tech stack. If you can do web searches, search for the latest patterns. If not, use your best knowledge and note what should be verified.
4. Describe HOW the system will be implemented
5. Report what you found so I can verify
6. Leave Location fields empty (scaffolding fills them in)

---

### Example bootstrap conversation:

User: "I'm building a todo app. Users can add, complete, and delete todos. React frontend, Node.js backend with a database."

AI: "Got it. Let me suggest a tech stack and generate your References.md..."
(AI reads Conventions.md, reads convention docs one at a time, generates References.md)

User: "Looks good, but we don't need auth for now."

AI: "I'll remove the Auth System from feature-tree.md and mark it as not applicable in References.md."

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

## Step 4: Set Up Hooks (optional - can be done later)

Hooks automatically remind the AI to update documentation and run verification. See templates/hooks-spec.md for what hooks to create. This step can be deferred to scaffolding if you want to get started faster.

## Checklist

After bootstrap, verify:

- [ ] CLAUDE.md in project root
- [ ] Conventions.md in project root
- [ ] conventions/ directory with all convention docs
- [ ] References.md generated with relevant sections filled (irrelevant systems removed)
- [ ] feature-tree.md initialized (irrelevant systems removed)
- [ ] docs/systems/ directory created
- [ ] docs/features/ directory created
- [ ] Git initialized with .gitignore

## What Bootstrap Does NOT Do

- Does not create code or foundational systems (Phase 2: Scaffold)
- Does not modify existing code (for existing projects)
- Does not set up CI/CD (part of scaffolding)

Bootstrap generates the map. Scaffolding builds what the map describes.

## Next Step

Proceed to scaffolding/SCAFFOLD.md to build the foundational systems.
