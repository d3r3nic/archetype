# References

## Project

Each line must start with `- ` (dash space). `scripts/pulse-inspect.sh` parses these bullets; lines without a leading dash are ignored.

- Name: [project name]
- Purpose: [one-line description]
- Stage: [development / staging / production]
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
```

## Design Artifact

Convention #27 anchor: **AI consults the artifact first. When silent, AI asks. AI never invents UX.**

- Primary tool: [AI researches current best-in-class tool at bootstrap time]
- Artifact location: [URL or path; `[to be created]` if not yet produced]
- Platform parity: [how iOS + Android states are kept aligned in the artifact]
- Every UI state is designed: empty, loading, error, success, disabled; platform-specific permission prompts included
- Update responsibility: [who owns edits; how code follow-ups trigger]

If the artifact is silent, AI asks — it does not invent visual or interaction patterns.

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
