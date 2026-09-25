# References

## Project

Each line must start with `- ` (dash space). `scripts/pulse-inspect.sh` parses these bullets; lines without a leading dash are ignored.

- Name: [project name]
- Purpose: [one-line description]
- Stage: [development / staging / production]
- Profile: PROFILE.md (operating stage and decision authority per #30 and #29)
- Owner channel: [where escalations go and how quickly the owner usually answers]
- Decision location: [existing decision record path or section; otherwise DECISIONS.md from templates/decisions.md, one location only]
- Reporting pace: [every session / every release / on request]
- Peer coding: [none; or the two AI assistants that take turns on this project, each as its short name with its tool in parentheses, separated by a comma (development/PEER-CODING.md)]
- Peer roles: [when Peer coding names two: who writes new work and who reviews it, in the owner's words; n/a when it is none]
- Platforms: [iOS / Android / both]

## Tech Stack

Each line must start with `- ` (dash space); content is `- Key: Value`. Inspector parses every bullet.

- Framework: [mobile framework chosen at bootstrap]
- Language: [language]
- UI Library: [selected native, library, adapter, wrapper, or project-owned approach with the #22 decision recorded]
- State: [client-state approach]
- Data Fetching: [server-state library or HTTP client]
- Validation: [schema library]
- Navigation: [navigation library]
- Testing: [test runner]
- Package Manager: [package manager and native dependency manager]

## Commands

Record each command one of three ways: the command in backticks, run exactly as written from this folder (text after the closing backtick is a note and is never run); a note in brackets while none is recorded yet; or `none` when the project has no such command. A step check that needs a command fails on a bracketed note and on a value in any other form.

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
- Platform parity: [how iOS and Android states are kept aligned in the artifact]
- Every UI state designed: [yes / the gaps per screen, against the state list in #27, platform-specific permission prompts included]
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

Complete the sections relevant to this project. Record the selected approach, its consumers, and the reason when a shared boundary is justified. Features follow those recorded decisions; they do not create competing systems silently.

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
Tokens: [selected styling source and any roles, scales, or direct-value policy it defines]
Color schemes: [committed set and reason; no additional scheme is implied (#6)]
Type scale: [selected type approach and the content or interaction evidence behind it (#31)]
Motion: [the jobs motion serves, applicable user preferences, and the recorded implementation approach (#31)]
Layout: [selected composition and adaptation rules for the committed contexts (#31)]
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
Base components: [where selected native elements, library use, adapters, wrappers, or project-owned components are discovered]
Foundation decision: [selected interface approach and its reason, per #22]
Component-size limit: [project-specific comprehension or responsibility signal, or none with the review approach (#4)]
Import rule: [the recorded import boundary, including direct platform or library imports when chosen]
Platform-specific: [components that differ between iOS/Android]
Accessibility target: [the level the project commits to, chosen at bootstrap per #14; sets the contrast floor design content keeps (#27)]
Icon set: [selected icon sources, styles, and locations, or none; record how meaning and consistency are checked (#22)]
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

Research each native capability against the chosen framework, current platform guidance, permission flow, testability, and expected change. Direct platform or library use is valid when it keeps the behavior clear and access needs verifiable. Add a project-local adapter or wrapper when it centralizes real policy, permission handling, fallback behavior, testing, or a volatile dependency. Record the selected boundary rather than assuming one architecture for every capability.

List the capability boundaries in use:
- [native capability]: [direct source, adapter, or wrapper path] - [dependency, permission behavior, and reason]

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
