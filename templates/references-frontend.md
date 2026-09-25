# References

## Project

Each line must start with `- ` (dash space). `scripts/pulse-inspect.sh` parses these bullets; lines without a leading dash are ignored.

- Name: [project name]
- Purpose: [one-line description of what the app does]
- Stage: [development / staging / production]
- Profile: PROFILE.md (operating stage and decision authority per #30 and #29)
- Owner channel: [where escalations go and how quickly the owner usually answers]
- Decision location: [existing decision record path or section; otherwise DECISIONS.md from templates/decisions.md, one location only]
- Reporting pace: [every session / every release / on request]
- Mobile mode: [how people use it on a phone: in the phone's browser; added to the home screen, with each capability it commits to, such as offline use or notifications; or not on phones]
- URL: [deployed URL if any]

## Tech Stack

Each line must start with `- ` (dash space); content is `- Key: Value`. Inspector parses every bullet.

- Framework: [UI framework chosen at bootstrap]
- Language: [language]
- UI Library: [selected native, direct library, adapter, wrapper, or project-owned approach with the #22 decision recorded below]
- State: [client-state approach]
- Data Fetching: [server-state library]
- Validation: [schema library — one schema = types + validation]
- Bundler: [build tool]
- Testing: [test runner, end-to-end tool]
- Package Manager: [package manager]

## Commands

Record each command one of three ways: the command in backticks, run exactly as written from this folder (text after the closing backtick is a note and is never run); a note in brackets while none is recorded yet; or `none` when the project has no such command. A step check that needs a command fails on a bracketed note and on a value in any other form.

```
dev:       [command to start dev server]
build:     [command to build]
test:      [command to run tests]
typecheck: [command to run type checker]
lint:      [command to lint]
deploy:    [command to deploy]
capture:   [command that saves the capture set: each screen in each applicable state, per scheme and committed context (#27)]
```

## Compliance

PROFILE.md records whether the project handles regulated data (#30). This section records what follows from that for this unit. Keep an unanswered fact unknown.

- Regulated data: see PROFILE.md
- Regimes: [each law, contract or standard that applies, with the discovery answer or research behind it; none, with why; or unknown, with the open question]
- Obligations: [what each regime requires of this unit, such as an audit log, encryption, retention and deletion, or access review; none]
- Audit log: [where this unit keeps its audit log when a regime requires one: its path in this unit, recorded when scaffold builds it; kept by <another unit or service>; or not required, with why]
- Promises to users: [what the project has already told its users about their data, in the owner's words; none]

## Design Artifact

Convention #27 anchor: **AI consults the artifact first. When silent, the session designs within the picked direction and records it; the owner is asked only for identity and what a screen is for.** Any design skill, plugin, canvas, or workspace that runs in this project reads this section first: it is the brief. One `- Label: value` line per field, labels exact. The framework's self-test keeps this list and convention #27 in step; `scripts/validate-design.sh` fails a line that is missing, repeated, or still a placeholder, and the independent review reads whether a recorded value is true. Where the recorded direction makes two lines the same place (under `workspace-first` the artifact and the published view; under `repository-first` the artifact and the recorded styling source or discovery surface), write `same as <label>`.

- Primary tool: [category: a visual design tool / a design-system-as-code repository / an AI design canvas in the working session / an AI design workspace; the product's name and version, a dated fact, on this line]
- Direction of truth: [repository-first (the recorded styling source, specifications, and any interface previews in the repository are the artifact; a workspace or canvas is a published view or a proposal) / workspace-first (the workspace or canvas is the artifact; the repository styling source and any discovery surface follow it)]
- Artifact location: [path or URL; `[to be created]` until first published]
- Published view: [URL of the published view, or none]
- Tokens source: [path to the recorded styling source under #6, such as a token file, theme module, native style source, or decision record for justified direct values]
- Component catalog: [path or URL of the selected component or interaction-pattern discovery surface, or none]
- Brand book: [path or URL of the brand and content guidelines; none only while `Brand decided` is not yes]
- Design working files: [folder for artboards, layout manifests, images, and sync configuration, a folder a tool fixes for itself recorded as it is; committed; generated bundles ignored; or none]
- Sync: [the step that keeps the two places in step in the recorded direction: the publish under repository-first, the read-back into the repository under workspace-first; who runs it; when (after each design change, before each UI feature); or none when there is only one place]
- Brand decided: [yes only when the brand book records all six, each as a decision or an explicit none: marks, palette values, type families, voice and tone, imagery style, motion signature / deferred to downstream projects / not yet, directions pending the owner's pick]
- Every UI state designed: [yes / the gaps per screen, against the state list in #27]
- Update responsibility: [who owns artifact edits; how code follow-ups trigger]
- Complementary tools: [exploration only, never source of truth; list or none]
- Primary context: [where people use it most of the time: a desk, a phone, a shared screen, outdoors, or two of these equally; from discovery]
- Committed contexts: [every context the product is verified in, each with its own captures (#27)]
- Density: [strategy by context and activity, with the reason; comparable contexts stay coherent (#31)]
- Vocabulary: [path of the glossary, from templates/vocabulary.md: every thing named once with its verb (#31); starts from the owner's words]
- First task: [the one thing a person should be able to do within a minute of first opening it, in the owner's words; from discovery; unknown only with what was assumed]
- Return tasks: [up to three things people come back to do most, first one first; the directions and the first screen are composed for the first (bootstrap/DESIGN-INTERVIEW.md); unknown only with what was assumed]
- Session length: [a quick check a few times a day / hours at a stretch / between; from discovery; informs density and interaction research]
- Captures: [folder the capture set lives in, committed; regenerated in place by the `capture:` command, never kept by date, so the set does not grow with every run (#27)]

## Foundational Systems

Complete the sections relevant to this project. Record the selected approach, its consumers, and the reason when a shared boundary is justified. Features follow those recorded decisions; they do not create competing systems silently. Sections are ordered by scaffold build sequence.

### Git & Project Init (#2)
Commit convention: [e.g., conventional commits - feat:, fix:, chore:]
Branch strategy: [e.g., trunk-based, feature branches]
Pre-commit hooks: [what runs - lint, format, typecheck]
Pre-commit budget: [max hook runtime before a check moves to CI (#25)]
Branch protection: [rules for main branch]

### Project Structure & Types (#1, #7)
Folder structure: [see Folder Structure section below]
Path alias: [e.g., @/ maps to src/]
Type checking: [strictest mode the language supports; config location]
File-size limit: [lines per file the tools in use can read whole; split past it (#1, #17)]
Compaction cadence: [optional; when the AI compacts context in long sessions (#17)]
Validation library: [name - one schema = types + validation]
Shared types: [path to shared type definitions]
Barrel exports: [pattern used for module public APIs]

### Theme System (#6)
Location: [e.g., src/shared/ui/theme/]
Tokens: [selected styling source and any roles, scales, or direct-value policy it defines]
Color schemes: [committed set and reason; no additional scheme is implied (#6)]
Type scale: [selected type approach and the content or interaction evidence behind it (#31)]
Motion: [the jobs motion serves, applicable user preferences, and the recorded implementation approach (#31)]
Layout: [selected composition and adaptation rules for the committed contexts (#31)]
Wrappers: [selected interface boundary and path, or none when direct native or library use is chosen]
Usage: [how features use theme values]

### Error System (#8)
Location: [e.g., src/shared/errors/]
Error service: [path to centralized error handler]
Error boundaries: [path to boundary components]
Build-target check: [how custom error subclasses are verified on the real build target; the constructor fix if one is required (#8)]
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
Base components: [where selected native elements, library use, adapters, wrappers, or project-owned components are discovered]
Foundation decision: [selected interface approach and its reason, per #22]
Component-size limit: [project-specific comprehension or responsibility signal, or none with the review approach (#4)]
Import rule: [the recorded import boundary, including direct platform or library imports when chosen]
Accessible components: [path to modal, dialog, dropdown with proper keyboard/ARIA support]
Component catalog: [catalog URL or equivalent, if applicable]
Icon set: [selected icon sources, styles, and locations, or none; record how meaning and consistency are checked (#22)]
A11y testing: [which tools are configured]
Accessibility target: [the level the project commits to, chosen at bootstrap per #14; sets the contrast floor design content keeps (#27)]
Target size: [the platform minimum the project holds to, and the space between adjacent targets (#14)]

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
Lint rules: [AI-targeted rules configured - no untyped escape hatch, no console-level output, no direct imports]
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
│       ├── types       # Feature types
│       └── index       # Public API (barrel export)
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

## Project-Specific Documentation

For existing projects migrated to the framework, additional documentation locations:

### Convention Overrides (per-convention project rules)
- conventions/overrides/{N}-{name}.md - project-specific rules extending the base conventions
- (List each override file that exists with a one-line description)

### Workflow Protocols
- protocols/{name}.md - workflow protocols beyond the base framework
- (List each protocol with a one-line description, e.g., "feature-audit-protocol.md - mandatory audit before feature work")

### Reference Catalogs
- catalogs/{name}.md - reference materials for quick lookup
- (List each catalog, e.g., "feature-directory.md - every feature with its purpose and location")

### Project-Specific Docs
- (List any links to existing project /docs/ that contain critical information)
