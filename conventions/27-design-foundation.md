# Convention #27: Design Foundation

## Principle

A design artifact exists before features are built and stays in sync with the code. UI decisions — including empty, loading, error, success, and disabled states; interaction feedback; primary vs secondary actions; visual hierarchy — come from the artifact, not the AI's improvisation. AI consults the artifact first. When it doesn't cover something, AI asks; AI never invents UX.

Design is upstream of #6 (tokens) and #22 (components). This convention governs the discipline; tools are chosen per project.

## Reusable System

Establish one design artifact per project that is:
- Living — updated alongside the code, not a one-off handoff
- Referenced — every UI decision traces back to it
- Tool-agnostic — artifact format (visual deck, design-system-as-code file, interactive prototype, AI-generated design assistant output) is the project's choice
- Discoverable — location and access documented in References.md so every new session finds it

## Rules

- A design artifact exists before feature implementation begins. AI researches the current best-in-class tools at bootstrap time and documents the chosen tool + artifact location in References.md.
- Every UI state is designed: empty, loading, error, success, disabled — not just the happy path.
- When the artifact doesn't cover something, AI asks the developer. AI does not invent visual or interaction patterns.
- When code and artifact diverge, update one or the other. Silent drift is a violation.
- Design tokens (#6) and component wrappers (#22) derive from the artifact; if the artifact changes its tokens, tokens must follow.

## Violations

- UI shipped without a corresponding artifact entry
- Undesigned states in production ("error state TBD", bespoke inline loading spinners, hand-rolled empty placeholders)
- Artifact not updated when UI changes land in code
- AI inventing a pattern when the artifact is silent, instead of asking

## Wrong vs Right

- WRONG: AI invents a loading indicator location because the artifact doesn't show one. The app ends up with inconsistent loading patterns.
- RIGHT: AI notices the artifact is silent on loading here, flags it to the developer, developer adds it, code implements what was agreed.
- WRONG: developer updates the artifact with a new button variant; code keeps the old variant. Six weeks later they diverge irreversibly.
- RIGHT: any artifact update triggers a code follow-up (and vice versa); the two are treated as two views of one source of truth.

## Research Notes

When bootstrapping this convention:
- Survey the current design-artifact tooling landscape: visual design tools, design-system-as-code tools, AI-driven design assistants. Pick what fits the team, stack, and workflow now.
- Decide artifact format (single file, linked cloud workspace, component library in code) and persistence (versioned with code, external).
- Document the chosen tool, artifact location, and update responsibility in References.md. Tool choice is expirable; the discipline of "design before code, living artifact, AI consults it" is durable.
