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

Each system is built once following convention #0 (Reusability). Features plug into these, never build ad-hoc.

### Theme System (#6)
Location: [e.g., src/shared/ui/theme/]
Tokens: [where design tokens are defined]
Wrappers: [where UI library wrappers live]
Usage: [how features use it, e.g., "import { colors, borders } from '@/shared/ui/theme'"]

### Error System (#8)
Location: [e.g., src/shared/errors/]
Error service: [path to centralized error handler]
Error boundaries: [path to boundary components]
Loading states: [path to unified loading/empty/error components]
Usage: [how features use it]

### API Layer (#9)
Location: [e.g., src/shared/api/]
Client: [path to configured API client]
Cache strategy: [Network-First / Stale-While-Revalidate / etc.]
Usage: [how features define endpoints or queries]

### Auth System (#11)
Location: [e.g., src/shared/auth/]
Auth utility: [path to auth helper, e.g., getAuthenticatedUser]
Token management: [how tokens are stored and refreshed]
Route protection: [path to route guard component]
Usage: [how features check auth]

### State Management (#5)
Store: [path to store configuration]
Pattern: [e.g., "one slice per feature, flat registration"]
Usage: [how features create and register slices]

### Component Foundation (#4)
Location: [e.g., src/shared/ui/]
Base components: [where wrapper components live]
Import rule: [e.g., "always from @/shared/ui/mui, never from @mui/material"]
Icons: [exception rule if any, e.g., "icons can be imported from @mui/icons-material"]

### Form System (#20)
Location: [e.g., src/shared/forms/]
Library: [React Hook Form / Formik / etc.]
Validation: [how schemas connect, e.g., "Zod schemas in feature/schemas.ts"]
Usage: [how features build forms]

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
