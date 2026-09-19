# References

## Project

Each line must start with `- ` (dash space). `scripts/pulse-inspect.sh` parses these bullets; lines without a leading dash are ignored.

- Name: [project name]
- Purpose: [one-line description]
- Stage: [development / staging / production]
- Profile: PROFILE.md (operating stage and decision authority per #30 and #29)
- Owner channel: [where escalations go and how quickly the owner usually answers]
- Decision location: [architecture decision records path, or "References.md § Decisions" until one exists]
- Reporting pace: [every session / every release / on request]
- Platforms: [iOS / Android / both]

## Tech Stack

Each line must start with `- ` (dash space); content is `- Key: Value`. Inspector parses every bullet.

- Framework: [mobile framework chosen at bootstrap]
- Language: [language]
- UI Library: [component foundation, or "project-owned" with the #22 decision recorded]
- State: [client-state approach]
- Data Fetching: [server-state library or HTTP client]
- Validation: [schema library]
- Navigation: [navigation library]
- Testing: [test runner]
- Package Manager: [package manager and native dependency manager]

## Commands

```
dev:       [command to run on simulator/emulator]
build:ios: [command to build iOS]
build:android: [command to build Android]
test:      [command to run tests]
typecheck: [command to run type checker]
lint:      [command to lint]
deploy:    [command to deploy to each store]
clean:     [command to clean build artifacts]
capture:   [command that saves the capture set: each screen in each applicable state, per scheme and committed context (#27)]
```

## Design Artifact

Convention #27 anchor: **AI consults the artifact first. When silent, the session designs within the picked direction and records it; the owner is asked only for identity and what a screen is for.** Any design skill, plugin, canvas, or workspace that runs in this project reads this section first: it is the brief. One `- Label: value` line per field, labels exact. The framework's self-test keeps this list and convention #27 in step; `scripts/validate-design.sh` fails a line that is missing, repeated, or still a placeholder, and the independent review reads whether a recorded value is true. Where the recorded direction makes two lines the same place (under `workspace-first` the artifact and the published view; under `repository-first` the artifact and the tokens source or the catalog), write `same as <label>`.

- Primary tool: [category: a visual design tool / a design-system-as-code repository / an AI design canvas in the working session / an AI design workspace; the product's name and version, a dated fact, on this line]
- Direction of truth: [repository-first (the token source, specifications, and component previews in the repository are the artifact; a workspace or canvas is a published view or a proposal) / workspace-first (the workspace or canvas is the artifact; the token source and catalog follow it)]
- Artifact location: [path or URL; `[to be created]` until first published]
- Published view: [URL of the published view, or none]
- Tokens source: [path of the token file or module the code derives its theme from (#6)]
- Component catalog: [path or URL, or none yet]
- Brand book: [path or URL of the brand and content guidelines; none only while `Brand decided` is not yes]
- Design working files: [folder for artboards, layout manifests, images, and sync configuration, a folder a tool fixes for itself recorded as it is; committed; generated bundles ignored; or none]
- Sync: [the step that keeps the two places in step in the recorded direction: the publish under repository-first, the read-back into the repository under workspace-first; who runs it; when (after each design change, before each UI feature); or none when there is only one place]
- Brand decided: [yes only when the brand book records all six, each as a decision or an explicit none: marks, palette values, type families, voice and tone, imagery style, motion signature / deferred to downstream projects / not yet, directions pending the owner's pick]
- Platform parity: [how iOS and Android states are kept aligned in the artifact]
- Every UI state designed: [yes / the gaps per screen, against the state list in #27, platform-specific permission prompts included]
- Update responsibility: [who owns artifact edits; how code follow-ups trigger]
- Complementary tools: [exploration only, never source of truth; list or none]
- Primary context: [where people use it most of the time: a desk, a phone, a shared screen, outdoors, or two of these equally; from discovery]
- Committed contexts: [every context the product is verified in, each with its own captures (#27)]
- Density: [roomy / dense, with the reason; sets the spacing ladder's step for the whole product (#31)]
- Vocabulary: [path of the glossary, from templates/vocabulary.md: every thing named once with its verb (#31); starts from the owner's words]
- First task: [the one thing a person should be able to do within a minute of first opening it, in the owner's words; from discovery; unknown only with what was assumed]
- Return tasks: [up to three things people come back to do most, first one first; the directions and the first screen are composed for the first (bootstrap/DESIGN-INTERVIEW.md); unknown only with what was assumed]
- Session length: [a quick check a few times a day / hours at a stretch / between; from discovery; the density recommendation is built from it]
- Captures: [folder the capture set lives in, committed; regenerated in place by the `capture:` command, never kept by date, so the set does not grow with every run (#27)]

## Foundational Systems

Each system is built once following convention #0 (Reusability). Features plug into these, never build ad-hoc.

### Git & Project Init (#2)
Commit convention: [e.g., conventional commits]
Branch strategy: [e.g., trunk-based]
Pre-commit hooks: [what runs]
Pre-commit budget: [max hook runtime before a check moves to CI (#25)]

### Project Structure & Types (#1, #7)
Folder structure: [see Folder Structure section below]
Type checking: [strictest mode the language supports]
File-size limit: [lines per file the tools in use can read whole; split past it (#1, #17)]
Compaction cadence: [optional; when the AI compacts context in long sessions (#17)]
Validation library: [which one]
Shared types: [path to shared type definitions]

### Theme System (#6)
Location: [path to theme definition]
Tokens: [where design tokens are defined - colors, spacing, typography]
Color schemes: [committed set, light + dark by default; if a single scheme, the reason (#6)]
Type scale: [the steps, each with its job; the measure token (#31)]
Motion: [the duration scale and the easing set, with their jobs (#31)]
Layout: [grid or none, with the reason; container widths; the elevation levels the shadow and z-index scales share (#31)]
Platform adaptation: [how theme adapts between iOS and Android if applicable]
Usage: [how features use theme values]

### Error System (#8)
Location: [path to error service]
Error types: [custom error classes]
Build-target check: [how custom error subclasses are verified on the real build target; the constructor fix if one is required (#8)]
Error display: [how errors are shown to users - toasts, alerts, error screens]
Loading states: [unified loading and empty state components]
Crash reporting: [which service]
Usage: [how features use the error system]

### API Layer & Contract (#9, #10)
Location: [path to API client]
Client: [configured HTTP client]
Cache strategy: [how API data is cached]
Offline handling: [how the app behaves when offline]
Response format: [consistent envelope structure]
Usage: [how features define API calls]

### Auth System (#11)
Location: [path to auth service]
Auth utility: [how to get authenticated user]
Token management: [secure storage - keychain, encrypted preferences]
Session handling: [how login/logout/refresh work]
Deep linking: [auth-related deep links if applicable]
Usage: [how features check auth]

### Navigation (#21)
Router: [which navigation library]
Route definitions: [path to route config]
Navigation guards: [auth protection on routes]
Deep linking: [deep link configuration]
Usage: [how features navigate]

### State Management (#5)
Store: [path to store configuration]
Pattern: [e.g., "one slice per feature"]
Server state: [how API data integrates with state]
Offline state: [how offline data is persisted]
Usage: [how features manage state]

### Component Foundation (#4, #22)
Location: [path to shared components]
Base components: [wrapper components]
Foundation decision: [established library chosen, or "project-owned" with the reason, per #22]
Component-size limit: [lines per component before it must be composed (#4)]
Import rule: [import convention]
Platform-specific: [components that differ between iOS/Android]
Accessibility target: [the level the project commits to, chosen at bootstrap per #14; sets the contrast floor design content keeps (#27)]
Icon set: [the one set, its style, its location; sizes tied to the type scale (#22)]
Target size: [the platform minimum the project holds to, and the space between adjacent targets (#14)]
Usage: [how features use shared components]

### Form System (#20) [if applicable]
Location: [path to form utilities]
Validation: [how forms validate]
Usage: [how features build forms]

### Testing Setup (#12, #18)
Test runner: [which one]
Test utilities: [path to shared test helpers]
Device testing: [simulator/emulator/physical device testing setup]
Verification commands: [exact commands]

### CI/CD & Build (#15)
CI platform: [which one]
Pipeline: [sequence]
iOS deployment: [beta distribution and store submission process]
Android deployment: [beta distribution and store submission process]
Code signing: [how certificates/keys are managed]

## Folder Structure

```
[paste actual folder structure here]
```

## Backend

Mobile apps almost always talk to a backend. Document which stack serves this mobile app:
- Backend approach: [Custom backend (separate folder with its own References.md) / Platform backend (BaaS — uses references-platform.md) / None (offline-only, no backend)]
- Backend location: [path to backend folder if custom, or platform name + admin URL if BaaS]
- API contract: [REST base URL / GraphQL endpoint / SDK name]
- Offline sync: [strategy for reconnecting after offline use]
- Auth flow: [how mobile obtains and refreshes tokens — deep-link OAuth, embedded SDK, etc.]

If backend is a separate custom folder, it has its own `References.md` using `references-backend.md`. If it's a BaaS platform, it has its own folder (e.g., `backend-<platform>/`) using `references-platform.md`. Cross-reference here.

## Native-Module Wrapping

Mobile projects need native-module wrappers for the same reason convention #22 requires UI-library wrappers: features should not import the native-capability library directly. Features that need a native capability (camera, HealthKit/Google Fit, haptics, biometrics, secure storage, geolocation, push notifications, BLE) import from a project-local wrapper that:
- Configures the native library with the project's defaults
- Handles permission request UX consistently
- Falls back gracefully when permission denied
- Provides a stable API the rest of the project uses

This applies to cross-platform frameworks and native platforms alike. Research the current native-module approach for the chosen mobile framework at bootstrap time.

List the wrappers in use:
- [native capability]: [wrapper path] — [what native library it wraps, why]

## Platform-Specific Notes

### iOS
- Minimum iOS version: [minimum supported version]
- Required Info.plist permission strings: [NSCameraUsageDescription, NSHealthShareUsageDescription, etc. Missing entries cause App Store rejection.]
- Code signing / provisioning: [how certificates and profiles are managed]
- Store submission: [process, developer-program fee, and typical review time — verify current values at bootstrap and record the date checked]

### Android
- Minimum API level: [minimum supported level]
- Required manifest permissions: [CAMERA, ACCESS_FINE_LOCATION, etc.]
- Signing config: [how release keystore is managed]
- Store submission: [process, developer-program fee, and typical review time — verify current values at bootstrap and record the date checked]

### Managed vs bare native toolchain (cross-platform frameworks)
- **Managed workflow:** the framework's tooling handles native config, build, and over-the-air updates. Faster to start. Limited to the native modules the managed layer supports unless you eject.
- **Bare workflow:** full native project; can use any native module. Requires the native platform toolchains.
- Choice depends on which native capabilities you need and whether the user owns the toolchain. Decide at bootstrap time.

## Existing Patterns to Study

- [feature name]: [path] - [what it demonstrates]

## Critical Lessons

- [lesson]: [what happened and the rule that prevents it]

## Convention Overrides

- [convention #]: [what's different and why]
