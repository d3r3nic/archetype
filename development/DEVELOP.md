# Phase 3: Develop

Build features on top of the scaffolded foundational systems. This is the ongoing development phase - it runs for the life of the project.

## Prerequisites

- Phase 2 (Scaffold) complete
- All foundational systems built and documented
- feature-tree.md reflects current state

## Feature Development Workflow

Every feature follows this process:

### 1. Understand

- Read feature-tree.md to see what exists
- Check if a similar feature or reusable system already covers the need
- Read References.md for project conventions and system locations

### 2. Plan

- For simple changes (single file, obvious fix): skip to step 3
- For multi-file features: write a plan before implementing
  - What files will change
  - Which foundational systems will be used
  - What new components/services are needed
  - Get approval on the plan

### 3. Implement

- Use foundational systems. Never build ad-hoc.
  - Errors → use the error system
  - API calls → use the API layer
  - Styling → use the theme system
  - Auth → use the auth utility
  - Forms → use the form system
  - Loading/empty states → use unified components
- Follow the project's folder structure for the new feature
- Follow convention #0: if this component/service could be reused, build it reusable

### 4. Verify

- Run tests after every significant change (convention #18)
- Run build and type-check
- For UI changes: verify visual output
- Work is not done until verification passes

### 5. Document

- Create docs/features/{feature-name}.md using the feature documentation template
- Update feature-tree.md with the new feature entry:
  - Feature name
  - Routes (if applicable)
  - Which foundational systems it uses
  - Status: implemented
  - Doc path

### 6. Commit

- Commit as a save point (convention #2)
- Descriptive commit message explaining what changed and why

## Feature Documentation Template

Each feature gets a doc at docs/features/{feature-name}.md:

```
# {Feature Name}

## What It Does
[One paragraph: what the feature does from the user's perspective]

## Why It Exists
[Business reason this feature was built]

## Systems Used
[Which foundational systems this feature plugs into]
- Error system: [how]
- API layer: [endpoints used]
- Theme: [any custom tokens]
- Auth: [permission requirements]

## Structure
[Files and folders this feature contains]

## Key Decisions
[Any decisions made during implementation that aren't obvious from the code]
```

## When a New AI Agent Joins Mid-Project

1. Read CLAUDE.md (the enforcer - learn the rules)
2. Read Conventions.md (scan the convention index)
3. Read References.md (understand this project's tech stack and system locations)
4. Read feature-tree.md (understand what exists, what's in progress, what's missing)
5. Read docs/systems/ for the systems relevant to the current task
6. Read docs/features/ for the feature being worked on
7. Start working - the foundational systems are already in place
