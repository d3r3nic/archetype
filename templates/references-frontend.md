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
- Peer coding: [none; or peer-coding/SETTINGS.md, when the owner chose two AI assistants taking turns (development/PEER-CODING.md)]
- Mobile mode: [how people use it on a phone: in the phone's browser; added to the home screen, with each capability it commits to, such as offline use or notifications; or not on phones]
- URL: [deployed URL if any]

## Tech Stack

Each line must start with `- ` (dash space); content is `- Key: Value`. The inspector parses every bullet. Record what bootstrap chose and add a line for anything else the project depends on.

- Framework: [the interface framework chosen at bootstrap, or none]
- Language: [language]
- UI Library: [the selected native, direct library, adapter, wrapper, or project-owned approach, with the #22 decision recorded below]
- State: [the shared-state approach, or none when screens keep their own state (#5)]
- Data Fetching: [the approach to reading remote data and caching it, or none (#9)]
- Validation: [how outside data is validated, with one definition per shape (#7)]
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

## Boundaries

What only each shared system may use, one line per concern (#0, #25): `` - <concern>: `<pattern>` only in `<path>`, `<path>` ``. The pattern is an extended regular expression for this project's own tool, such as the call that reaches the network or reads the environment. Each path is a folder ending in `/`, a file, or a glob such as `*.test.*`, from this folder. `scripts/validate-develop.sh` fails when a file outside those paths contains the pattern (Markdown files are not read), and the scaffold's exit gate checks the lines that exist. Add a line as each shared system is built. With no shared concern to guard, record `- none: <reason>`.

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

Complete only the sections for systems this project builds; each convention's Applies when decides. For each, record the choice, where it lives, how features use it, and the reason where it is not obvious. Features use these systems; they never build competing ones (#0), and § Boundaries keeps them from going around them. Sections follow the scaffold's build order.

### Git & Project Init (#2)
Commit convention: [the convention the team follows]
Branch strategy: [the branch model and why]
Checks run: [where the project's checks run before work reaches the main line: a hook at `<path>`, a pipeline at `<path>`, both, or none, with why (#2, #15)]
Hook budget: [how long a check before each commit may take before it moves to the pipeline (#25), or none]
Branch protection: [what the main branch requires]

### Project Structure & Types (#1, #7)
Folder structure: [see Folder Structure below]
Configuration: [the configuration owner's path, and how it validates required values at startup]
Type checking: [the level the project holds to, and where it is configured]
Validation: [how outside data is validated, and where the shared data shapes live]

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
Location: [where the error system lives]
Kinds: [the kinds of error the product distinguishes, and how each reaches the person]
Reporting: [where errors are reported, chosen for the stage and cost]
Shared states: [where the waiting, error, empty and offline components live]
Build-target check: [how custom error types are verified on the real build target; the fix if one is required (#8)]
Usage: [how features use the error system]

### API Layer & Contract (#9, #10)
Location: [where each service's client lives, or none when the product calls no remote service]
Contract: [how the exchanged shapes are shared with the service: generated, shared or checked (#10)]
Response format: [the service's recorded response format]
Caching: [the rule for how fresh each kind of remote data must be (#5, #9)]
Usage: [how features ask a client for data]

### Auth System (#11)
Location: [the auth owner's path, or none when the product has no accounts]
Provider: [the provider and why]
Credentials: [how credentials are stored and renewed]
Guard: [how protected places are guarded (#21)]
Usage: [how screens learn who is signed in]

### Routing & Layouts (#21)
Router: [the routing approach, or none for a single view]
Route definitions: [where each place is defined once]
Layouts: [the persistent frames, where they live]
Guard: [the one guard for protected places]
View state: [which view state survives a refresh, a back step or a shared link, and how (#5)]

### State Management (#5)
State owners: [each fact several screens use, and its one owner; or none when screens keep their own state]
Remote data: [how remote data is cached and refreshed, or none]
Usage: [how features read and change shared state]

### Component Foundation & Accessibility (#4, #14, #22)
Location: [e.g., src/shared/ui/]
Base components: [where selected native elements, library use, adapters, wrappers, or project-owned components are discovered]
Foundation decision: [selected interface approach and its reason, per #22]
Component-size limit: [project-specific comprehension or responsibility signal, or none with the review approach (#4)]
Import rule: [the recorded import boundary, including direct platform or library imports when chosen]
Accessible components: [where the dialog, menu and other components with focus and keyboard behavior live]
Component catalog: [catalog URL or equivalent, if applicable]
Icon set: [selected icon sources, styles, and locations, or none; record how meaning and consistency are checked (#22)]
A11y testing: [the automated accessibility check and where it runs]
Accessibility target: [the standard and level the project commits to, chosen at bootstrap per #14; sets the contrast floor design content keeps (#27)]
Target size: [the platform minimum the project holds to, and the space between adjacent targets (#14)]

### Form System (#20)
Location: [where the form system lives, or none when the product has no form]
Validation: [how forms use the one shape definition (#7)]
Drafts: [how input is kept, or the leave warning]
Usage: [how features build a form]

### Testing Setup (#12, #18)
Test runner: [which one and command]
Shared setup: [where the one test setup, the data builders and the network fakes live]
Isolation: [how tests stay independent of each other's data]
Verification commands: [the commands to run: test, typecheck, build]
Coverage: [where testing effort goes and any thresholds]

### CI/CD & Performance (#15, #13)
Pipeline: [where the checks run and what a merge requires, or none yet, with why]
Budgets: [each size or performance budget the product set, how it is measured, and where it is enforced; or none, with why]
Measurement: [how real use is measured once people depend on it, or none yet]
Rollback: [the way back from a release people depend on]

## Folder Structure

```
[paste actual folder structure here]
```

## Existing Patterns to Study

Before building anything new, study these reference implementations:

- [feature name]: [path] - [what it demonstrates]

## Critical Lessons

Production bugs and hard-won rules specific to this project:

- [lesson]: [what happened and the rule that prevents it]

## Convention Overrides

Any project-specific departures from the conventions:

- [convention #]: [what's different and why]

## Project-Specific Documentation

Where this project's own rules and documents live, when it has them:

- conventions/overrides/{N}-{name}.md: [each override file with a one-line description]
- protocols/{name}.md: [each workflow protocol with a one-line description]
- [other documents]: [each location with what it holds]
