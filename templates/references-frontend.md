# References

## Project

Name: [project name]
Purpose: [one-line description of what the app does]
Stage: [development / staging / production]
URL: [deployed URL if any]

## Tech Stack

Framework: [React / Next.js / Vue / Svelte / etc.]
Language: [TypeScript / JavaScript]
UI Library: [MUI / Chakra / Tailwind / Radix / etc.]
State: [Redux Toolkit / Zustand / Jotai / Context / etc.]
Data Fetching: [RTK Query / React Query / SWR / Apollo / etc.]
Validation: [Zod / Yup / Valibot / etc.]
Bundler: [Vite / Next.js / Webpack / Turbopack / etc.]
Testing: [Vitest / Jest / Playwright / Cypress / etc.]
Package Manager: [npm / pnpm / yarn / bun]

## Commands

```
dev:       [command to start dev server]
build:     [command to build]
test:      [command to run tests]
typecheck: [command to run type checker]
lint:      [command to lint]
deploy:    [command to deploy]
```

## Foundational Systems

Each system is built once following convention #0 (Reusability). Features plug into these, never build ad-hoc. Sections ordered by scaffold build sequence.

### Git & Project Init (#2)
Commit convention: [e.g., conventional commits - feat:, fix:, chore:]
Branch strategy: [e.g., trunk-based, feature branches]
Pre-commit hooks: [what runs - lint, format, typecheck]
Branch protection: [rules for main branch]

### Project Structure & Types (#1, #7)
Folder structure: [see Folder Structure section below]
Path alias: [e.g., @/ maps to src/]
Type checking: [e.g., strict mode enabled in tsconfig]
Validation library: [e.g., Zod - one schema = types + validation]
Shared types: [path to shared type definitions]
Barrel exports: [pattern used for module public APIs]

### Theme System (#6)
Location: [e.g., src/shared/ui/theme/]
Tokens: [where design tokens are defined]
Wrappers: [where UI library wrappers live]
Usage: [how features use theme values]

### Error System (#8)
Location: [e.g., src/shared/errors/]
Error service: [path to centralized error handler]
Error boundaries: [path to boundary components]
Loading states: [path to unified loading/empty/error components]
Usage: [how features use the error system]

### API Layer & Contract (#9, #10)
Location: [e.g., src/shared/api/]
Client: [path to configured API client]
Cache strategy: [Network-First / Stale-While-Revalidate / etc.]
Response format: [consistent envelope structure]
Contract: [how types are shared with backend - generated client, shared schemas, etc.]
Usage: [how features define endpoints or queries]

### Auth System (#11)
Location: [e.g., src/shared/auth/]
Auth utility: [path to auth helper]
Token management: [how tokens are stored and refreshed]
Route protection: [path to route guard component]
Usage: [how features check auth]

### Routing & Layouts (#21)
Router: [which routing library]
Route definitions: [path to route constants/config]
Layout components: [path to persistent layout shells]
Route guard: [path to auth route wrapper]
URL state: [how filters/pagination are encoded in URL]

### State Management (#5)
Store: [path to store configuration]
Pattern: [e.g., "one slice per feature, flat registration"]
Server state library: [which one and how it integrates with API layer]
Usage: [how features create and register slices]

### Component Foundation & Accessibility (#4, #14, #22)
Location: [e.g., src/shared/ui/]
Base components: [where wrapper components live]
Import rule: [e.g., "always from @/shared/ui, never from UI library directly"]
Accessible components: [path to modal, dialog, dropdown with proper keyboard/ARIA support]
Component catalog: [Storybook URL or equivalent, if applicable]
Icons: [exception rule if any]
A11y testing: [which tools are configured]

### Form System (#20)
Location: [e.g., src/shared/forms/]
Library: [form handling library]
Validation: [how schemas connect - one schema = types + validation]
Usage: [how features build forms]

### Testing Setup (#12, #18)
Test runner: [which one and command]
Test utilities: [path to shared render wrapper, factories, mocks]
API mocking: [which tool for network-level mocking]
Verification commands: [exact commands to run - test, typecheck, build]
Coverage: [thresholds and what's enforced]

### CI/CD & Performance (#15, #13)
CI platform: [which one]
Pipeline: [sequence - lint → typecheck → test → build → deploy]
Code splitting: [how routes are split]
Bundle budget: [size limits and enforcement]
Lint rules: [AI-targeted rules configured - no any, no console.log, no direct imports]
Preview deployments: [per-PR deployments, if applicable]

## Folder Structure

```
[paste actual folder structure here]

Example:
src/
├── features/           # Feature code (self-contained)
│   └── [feature]/
│       ├── components/ # Feature UI
│       ├── hooks/      # Feature logic
│       ├── api/        # Feature API endpoints
│       ├── types.ts    # Feature types
│       └── index.ts    # Public API (barrel export)
│
├── shared/             # Foundational systems
│   ├── ui/             # Component foundation + theme
│   ├── api/            # API layer
│   ├── auth/           # Auth system
│   ├── errors/         # Error system
│   └── forms/          # Form system
│
└── app/                # App shell, routing, providers
```

## Existing Patterns to Study

Before building anything new, study these reference implementations:

- [feature name]: [path] - [what it demonstrates]
- [feature name]: [path] - [what it demonstrates]
- [feature name]: [path] - [what it demonstrates]

## Critical Lessons

Production bugs and hard-won rules specific to this project:

- [lesson]: [what happened and the rule that prevents it]
- [lesson]: [what happened and the rule that prevents it]

## Convention Overrides

Any project-specific deviations from standard conventions:

- [convention #]: [what's different and why]
