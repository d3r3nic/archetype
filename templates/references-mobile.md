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
- Peer coding: [none; or peer-coding/SETTINGS.md, when the owner chose two AI assistants taking turns (development/PEER-CODING.md)]
- Platforms: [the phone and tablet platforms it ships to]

## Tech Stack

Each line must start with `- ` (dash space); content is `- Key: Value`. Inspector parses every bullet.

- Framework: [mobile framework chosen at bootstrap]
- Language: [language]
- UI Library: [selected native, library, adapter, wrapper, or project-owned approach with the #22 decision recorded]
- State: [the shared-state approach, or none when screens keep their own state (#5)]
- Data Fetching: [the approach to reading remote data and caching it, or none (#9)]
- Validation: [how outside data is validated, with one definition per shape (#7)]
- Navigation: [the navigation approach]
- Testing: [test runner]
- Package Manager: [package manager and native dependency manager]

## Commands

Record each command one of three ways: the command in backticks, run exactly as written from this folder (text after the closing backtick is a note and is never run); a note in brackets while none is recorded yet; or `none` when the project has no such command. A step check that needs a command fails on a bracketed note and on a value in any other form.

```
dev:       [command to run on simulator/emulator]
build:<platform>: [command to build for each platform the app ships to, one line per platform]
test:      [command to run tests]
typecheck: [command to run type checker]
lint:      [command to lint]
deploy:    [command to deploy to each store]
clean:     [command to clean build artifacts]
capture:   [command that saves the capture set: each screen in each applicable state, per scheme and committed context (#27)]
```

## Boundaries

What only each shared system may use, one line per concern (#0, #25): `` - <concern>: `<pattern>` only in `<path>`, `<path>` ``. The pattern is an extended regular expression for this project's own tool, such as the call that reaches the network, reads the environment or opens a native capability. Each path is a folder ending in `/`, a file, or a glob such as `*.test.*`, from this folder. `scripts/validate-develop.sh` fails when a file outside those paths contains the pattern (Markdown files are not read), and the scaffold's exit gate checks the lines that exist. Add a line as each shared system is built. With no shared concern to guard, record `- none: <reason>`.

- [Configuration: `<the pattern that reads the environment>` only in `<the configuration owner's path>`]
- [Network: `<the network call pattern>` only in `<the API client's path>`]

## Compliance

PROFILE.md records whether the project handles regulated data (#30). This section records what follows from that for this unit. Keep an unanswered fact unknown.

- Regulated data: see PROFILE.md
- Regimes: [each law, contract or standard that applies, with the discovery answer or research behind it; none, with why; or unknown, with the open question]
- Obligations: [what each regime requires of this unit, such as an audit log, encryption, retention and deletion, or access review; none]
- Audit log: [where this unit keeps its audit log when a regime requires one: its path in this unit, recorded when scaffold builds it; kept by <another unit or service>; or not required, with why]
- Promises to users: [what the project has already told its users about their data, in the owner's words; none]

## Design Artifact

Convention #27 anchor: **AI consults the artifact first. When silent, the session designs within the picked direction and records it; the owner is asked only for identity and what a screen is for.** Any design skill, plugin, canvas, or workspace that runs in this project reads this section first: it is the brief. One `- Label: value` line per field. `scripts/validate-design.sh` checks that no line still holds its template placeholder and that `Brand decided: yes` waits until `First task` and `Return tasks` are known; the independent review reads whether a recorded value is true. Where the recorded direction makes two lines the same place (under `workspace-first` the artifact and the published view; under `repository-first` the artifact and the recorded styling source or discovery surface), write `same as <label>`.

- Primary tool: [category: a visual design tool / a design system kept as code / a design canvas in the working session / a design workspace; the product's name and version, a dated fact, on this line]
- Direction of truth: [repository-first (the recorded styling source, specifications, and any interface previews in the repository are the artifact; a workspace or canvas is a published view or a proposal) / workspace-first (the workspace or canvas is the artifact; the repository styling source and any discovery surface follow it)]
- Artifact location: [path or URL; `[to be created]` until first published]
- Published view: [URL of the published view, or none]
- Tokens source: [path to the recorded styling source under #6, such as a token file, theme module, native style source, or decision record for justified direct values]
- Component catalog: [path or URL of the selected component or interaction-pattern discovery surface, or none]
- Brand book: [path or URL of the brand and content guidelines; none only while `Brand decided` is not yes]
- Design working files: [folder for artboards, layout manifests, images, and sync configuration, a folder a tool fixes for itself recorded as it is; committed; generated bundles ignored; or none]
- Sync: [the step that keeps the two places in step in the recorded direction: the publish under repository-first, the read-back into the repository under workspace-first; who runs it; when (after each design change, before each UI feature); or none when there is only one place]
- Brand decided: [yes only when the brand book records all six, each as a decision or an explicit none: marks, palette values, type families, voice and tone, imagery style, motion signature / deferred to downstream projects / not yet, directions pending the owner's pick]
- Platform parity: [how the platforms' states are kept aligned in the artifact]
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

Complete only the sections for systems this app builds; each convention's Applies when decides. For each, record the choice, where it lives, how features use it, and the reason where it is not obvious. Features use these systems; they never build competing ones (#0), and § Boundaries keeps them from going around them.

### Git & Project Init (#2)
Commit convention: [the convention the team follows]
Branch strategy: [the branch model and why]
Checks run: [where the project's checks run before work reaches the main line: a hook at `<path>`, a pipeline at `<path>`, both, or none, with why (#2, #15)]
Hook budget: [how long a check before each commit may take before it moves to the pipeline (#25), or none]

### Project Structure & Types (#1, #7)
Folder structure: [see Folder Structure section below]
Configuration: [the configuration owner's path, and how it validates required values at startup]
Type checking: [the level the project holds to, and where it is configured]
Validation: [how outside data is validated, and where the shared data shapes live]

### Theme System (#6)
Location: [path to theme definition]
Tokens: [selected styling source and any roles, scales, or direct-value policy it defines]
Color schemes: [committed set and reason; no additional scheme is implied (#6)]
Type scale: [selected type approach and the content or interaction evidence behind it (#31)]
Motion: [the jobs motion serves, applicable user preferences, and the recorded implementation approach (#31)]
Layout: [selected composition and adaptation rules for the committed contexts (#31)]
Platform adaptation: [how the theme adapts to each platform, if it does]
Usage: [how features use theme values]

### Error System (#8)
Location: [where the error system lives]
Kinds: [the kinds of error the app distinguishes]
Build-target check: [how custom error types are verified on the real build target; the fix if one is required (#8)]
Error display: [how errors are shown to users - toasts, alerts, error screens]
Shared states: [where the waiting, error, empty and offline components live]
Crash reporting: [which service]
Usage: [how features use the error system]

### API Layer & Contract (#9, #10)
Location: [where each service's client lives]
Contract: [how the exchanged shapes are shared with the service (#10)]
Caching: [the rule for how fresh each kind of remote data must be (#5, #9)]
Offline handling: [how the app behaves when offline]
Usage: [how features ask a client for data]

### Auth System (#11)
Location: [the auth owner's path, or none when the app has no accounts]
Identity: [how screens learn who is signed in]
Credentials: [how credentials are kept in the platform's secure store and renewed]
Session handling: [how login/logout/refresh work]
Deep linking: [auth-related deep links if applicable]
Usage: [how features check auth]

### Navigation (#21)
Navigation: [the navigation approach]
Screen definitions: [where each screen is defined once]
Guard: [how protected screens are guarded]
Deep linking: [deep link configuration]
Usage: [how features navigate]

### State Management (#5)
State owners: [each fact several screens use, and its one owner; or none when screens keep their own state]
Remote data: [how remote data is cached and refreshed, or none]
Offline state: [how offline data is persisted]
Usage: [how features read and change shared state]

### Component Foundation (#4, #22)
Location: [path to shared components]
Base components: [where selected native elements, library use, adapters, wrappers, or project-owned components are discovered]
Foundation decision: [selected interface approach and its reason, per #22]
Component-size limit: [project-specific comprehension or responsibility signal, or none with the review approach (#4)]
Import rule: [the recorded import boundary, including direct platform or library imports when chosen]
Platform-specific: [components that differ between platforms]
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
Shared setup: [where the one test setup, the data builders and the fakes live]
Device testing: [simulator/emulator/physical device testing setup]
Verification commands: [exact commands]

### CI/CD & Build (#15)
Pipeline: [where the checks run and what a merge requires]
Distribution: [for each platform: the beta channel and the store submission process]
Code signing: [how certificates and keys are managed]

## Folder Structure

```
[paste actual folder structure here]
```

## Backend

Mobile apps almost always talk to a backend. Document which stack serves this mobile app:
- Backend approach: [its own service (a separate folder with its own References.md) / a hosted backend service (uses references-platform.md) / none (offline-only)]
- Backend location: [path to the backend folder, or the service's name and admin address]
- API contract: [the API's address and style, or the provider library the app uses]
- Offline sync: [strategy for reconnecting after offline use]
- Auth flow: [how mobile obtains and refreshes tokens — deep-link OAuth, embedded SDK, etc.]

A separate backend folder has its own `References.md` from `references-backend.md`. A hosted backend service has its own folder (for example `backend-<service>/`) using `references-platform.md`. Cross-reference it here.

## Native-Module Wrapping

Research each native capability against the chosen framework, current platform guidance, permission flow, testability, and expected change. Direct platform or library use is valid when it keeps the behavior clear and access needs verifiable. Add a project-local adapter or wrapper when it centralizes real policy, permission handling, fallback behavior, testing, or a volatile dependency. Record the selected boundary rather than assuming one architecture for every capability.

List the capability boundaries in use:
- [native capability]: [direct source, adapter, or wrapper path] - [dependency, permission behavior, and reason]

## Platform-Specific Notes

One block per platform the app ships to:

### [platform]
- Minimum supported version: [the oldest operating-system version supported]
- Permission declarations: [each permission the platform requires the app to declare, with the rationale text people see; a missing declaration can get the app rejected]
- Signing: [how certificates, profiles or keys are managed]
- Store submission: [process, developer-program fee, and typical review time; verify current values at bootstrap and record the date checked]

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
