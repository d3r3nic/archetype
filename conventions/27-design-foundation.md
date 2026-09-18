# Convention #27: Design Foundation

## Principle

A design artifact exists before features are built and stays in sync with the code. UI decisions — every state in the list under Rules; interaction feedback; primary vs secondary actions; visual hierarchy — come from the artifact, not the AI's improvisation. AI consults the artifact first. When it does not cover something, the session designs the missing piece within the picked direction, from the artifact's own patterns and #31, and records it; the owner is asked only when the gap is theirs (#29). AI never improvises a screen outside the system.

Design is upstream of #6 (tokens) and #22 (components). This convention governs the discipline; tools are chosen per project. A design tool that runs in the project (a design skill, a plugin, a canvas, a design workspace) works from the artifact and the token source, never around them; the section "Design tools" below says what governs its output and who decides.

## Reusable System

Establish one design artifact per project that is:
- Living — updated alongside the code, not a one-off handoff
- Referenced — every UI decision traces back to it
- Tool-agnostic — artifact format (visual deck, design-system-as-code file, interactive prototype, AI-generated design assistant output) is the project's choice
- Discoverable — recorded in References.md § Design Artifact, one labelled line per field (the tool, the direction of truth, the locations, the sync, whether the brand is decided), so every new session and every design tool finds it and reads it first

## Rules

- A design artifact exists before feature implementation begins. AI researches the current best-in-class tools at bootstrap time and documents the chosen tool + artifact location in References.md.
- Every applicable state of a screen is designed, and each state tells the person what happened, what they can do next, and what was kept. The states: empty (nothing yet), no results (filtered to nothing), loading, partial, error, success, disabled, offline, stale, conflict, first run, permission denied, overflow (long text, long lists, many of a thing). Empty shows what this will hold and the one action to start. No results says what filtered it and how to widen. Loading holds the layout in place and appears only after the delay the project sets. Error says what happened, what to do, and what was kept. Success says what changed and offers undo where undo is possible. Disabled says why, or the control stays enabled and explains. Offline says what still works. Stale says how old and how to refresh. Conflict shows both versions and a choice. First run appears once. Undo over confirm: confirmation is reserved for what cannot be undone, and it names the thing. This is the one list; other files cite it.
- When the artifact is silent, the session designs the missing piece from the artifact's own patterns and #31, records it in the artifact as a session-decided entry in the same change, and ships it with the record. It neither waits nor improvises outside the system. The owner is asked only when the gap is theirs: a new visual identity, a change to what a primary screen lets a person accomplish, or a pattern the product would be recognized by (#29). A session-decided entry stays marked until the owner's later word supersedes it; silence adopts nothing.
- When code and artifact diverge, update one or the other. Silent drift is a violation.
- Design tokens (#6) and component wrappers (#22) derive from the artifact; if the artifact changes its tokens, tokens must follow.
- The owner picks the visual direction from directions the AI proposes (#29); after the pick the artifact governs and the AI executes it without asking again. A design tool's output is a proposal until it is adopted into the artifact. Design content follows this discipline; code follows the tokens. See "Design tools" below.

## Violations

- UI shipped without a corresponding artifact entry
- Undesigned states in production ("error state TBD", bespoke inline loading spinners, hand-rolled empty placeholders)
- Artifact not updated when UI changes land in code
- A screen or state coded with no artifact entry; a session that waits on the owner for a composition question the direction already settles
- A screen merged with captures of the happy path only, or reviewed by the session that built it
- A design tool's aesthetic default applied over the brief: a typeface, a palette, or a direction the artifact already fixed
- The AI choosing the product's visual identity instead of proposing directions for the owner's pick
- Two design sources with no recorded direction of truth, or a mockup's literal value copied into code without a token
- Design working files scattered outside the recorded folder, inside the engine folder, or uncommitted; a generated bundle committed

## Wrong vs Right

- WRONG: the artifact has no error state for a list; the session sends the owner three placements and waits, or codes one with no record. RIGHT: the session applies the error pattern the artifact already uses elsewhere, records the entry as session-decided, and the owner sees it in the session summary.
- WRONG: the artifact gains a new button variant; code keeps the old variant. Six weeks later they diverge irreversibly.
- RIGHT: any artifact update triggers a code follow-up (and vice versa); the two are treated as two views of one source of truth.
- WRONG: a design tool run in a product with a settled artifact chooses new typefaces and a fresh palette because its own guidance says to be distinctive. RIGHT: the artifact and the token source are the brief; the tool draws with them, and its distinctiveness goes into composition, hierarchy, and states.
- WRONG: under `ai-decides` the AI picks the brand palette and moves on. RIGHT: three sketched directions, one recommended, the owner picks, the pick is recorded with the artifact revision, then the AI executes without asking again.

## Where in the project lifecycle UI/UX decisions happen

This is a TIMING rule, not just a scoping rule:

| Lifecycle moment | Who decides UI/UX | What they decide |
|---|---|---|
| Factory authoring a framework Step | Nobody decides brand UI/UX | Framework governs character (tokens layering, wrapper boundaries, every-state discipline) — NOT values |
| Template project bootstrap (project type: template) | Nobody decides brand UI/UX | Template ships structural primitives with neutral placeholder tokens. AI must NOT invent colors, type, iconography. Design Artifact is deferred. |
| Template project scaffolding | Nobody decides brand UI/UX | Structural components (Button, Input, Dialog, etc.) get API + tokens wiring only. No brand values land here. |
| **Product project bootstrap (project type: product)** | **This is where UI/UX is decided** | AI researches the tool and records the direction of truth. Artifact gets authored. Brand primitives committed, or the directions are prepared and the pick stays open: the scaffold builds neutral placeholder values and no UI feature ships until the owner picks. |
| Product project feature work | UI/UX decisions come from the Artifact | AI consults the artifact first; a gap is designed by the session within the picked direction and recorded as session-decided; the owner is asked only when the gap is theirs. |

So: any "change the button color" / "add an icon" / "tweak the hover state" prompt belongs at the product-bootstrap or product-feature stage. At template or framework level, the same prompt should be deflected: "this template is brand-neutral; UI/UX decisions land when a product spawns from it."

## Design tools

A design skill, plugin, canvas, or design workspace that runs in the project works from the same brief the code does. These rules say what the brief is, which rules govern what the tool produces, where its files live, and who decides.

- The brief. The artifact, the token source, the component catalog, PROFILE.md, and the project type (template or product), all found through References.md § Design Artifact, are the standing brief for any design tool. Where a tool's own defaults conflict with the brief (choose new typefaces, invent a palette, commit to a bold direction, match whatever the code happens to do), the brief wins. Where the brief is silent, the tool's process for proposing directions is welcome, and the choice is the owner's.
- Design content versus code. A mockup, artboard, canvas file, preview, or prototype a design tool produces is design content. Design content for a screen or flow shows every state; a piece that is not a screen (a poster, a one-page document, a report) shows what its purpose needs, follows the brand layer and #31 "Words", is exempt from screen states, and is reviewed in the order below minus states. It respects the accessibility floor (#14): visible focus, meaning never carried by color alone, reduced motion, touch targets, semantic structure where the format allows it, and the contrast level the project's accessibility target sets (the `Accessibility target` line of the component foundation section in References.md). It carries synthetic content only, never real customer or personal data (#30), with a bracketed placeholder where a fact is unknown; in a template project it carries no brand values. It is exempt from the code-construction rules: never-hardcode (#6), wrapper imports and no hand-built standard controls (#22, #4), tests (#12), lint gates (#25). A canvas format that needs literal inline values and draws its own controls is not a violation. Code never inherits a mockup's literal values: a value a mockup introduces is either an existing token or a token proposal, adopted into the token source before code uses it.
- A tool's output is a proposal until adopted. A direction is adopted by the owner's pick; a change within the settled direction is adopted by updating the artifact. Then the token source or the canvas carries it, in the recorded direction of truth, and then the code.
- Direction of truth, recorded once. References.md § Design Artifact declares `repository-first` (the token source, the specifications, and the component previews in the repository are the artifact; a design workspace or canvas is a published view or a proposal) or `workspace-first` (the workspace or canvas is the artifact; the repository's token source and catalog follow it). Never both. The sync between the two is recorded with it: the command or publish step, who runs it, and when (after each design change, before each UI feature). A state in which the two disagree is drift. The choice is a consequential decision and is recorded at the decision location (#29).
- Who picks. Visual identity (palette, type, tone, brand marks) and what each primary screen must let a person accomplish are the owner's, part of what the product is (#29). The AI proposes two to four genuinely different directions at decision fidelity (sketches, not finished screens), each with its motivation and its trade-off, one recommended; the owner picks; the pick is recorded at the decision location with the artifact revision as evidence. After the pick the artifact governs and the session executes without asking again; the no-owner case and the fidelity rule are stated in #29 and hold here. Composition within the direction is the session's (#31 and the silence rule above). The design interview (bootstrap/DESIGN-INTERVIEW.md) supplies what the directions are built from and is never a substitute for the pick.
- Templates. A design tool run in a template project produces wireframes, layouts, and states with neutral placeholder tokens; the bold-direction fallback does not apply; a request for brand values is deflected to the product that spawns from the template.
- Where the files live. Working files a design tool produces (artboards, layout manifests, images, sync configuration and notes, a tool's own conventions file) are the artifact's source under `workspace-first` and supporting material under `repository-first`. Either way they live in the folder recorded on the `Design working files` line; a folder a tool fixes for itself counts and is recorded as it is; they are never scattered across the tree and never inside the engine folder; and they are committed. A template project records the folder too, so a design tool run there has a home. Generated bundles and seeded pages are build output: not committed, the ignore rule recorded with the folder, the published link recorded in References.md.

References.md § Design Artifact carries one labelled line per field: `Primary tool`, `Direction of truth`, `Artifact location`, `Published view`, `Tokens source`, `Component catalog`, `Brand book`, `Design working files`, `Sync`, `Brand decided`, `Every UI state designed`, `Update responsibility`, `Complementary tools`, `Primary context`, `Committed contexts`, `Density`, `Vocabulary`; the mobile template adds `Platform parity`. The framework self-test keeps the templates and this list aligned.

What the framework cannot check: whether a mockup was consulted, whether the owner's pick was real, whether a workspace view is current, whether a mockup's states are complete, whether a session-decided entry should have been an owner question, whether the review read the screen in order, whether a capture matches the shipped screen. The self-test checks that the References templates carry the labelled section; a project's section is read by its sessions and by the independent review.

## Design review

A screen is reviewed in this order, by someone who did not build it (#29), against the artifact, with evidence per state:

1. Purpose: can a person do what the purpose sentence says, without help.
2. Hierarchy: one primary action; the reading order leads to it (#31).
3. States: every applicable state present and telling what it must (the list in Rules).
4. Words: the vocabulary, verbs that name outcomes, errors that say what happened and what to do (#31).
5. System fidelity: tokens only, cataloged components only, no literal value copied from a mockup (#6, #22).
6. The accessibility floor: focus visible on every surface, keyboard reaches everything, contrast per scheme, targets, reflow at the target's zoom level, reduced motion (#14).
7. Every committed scheme and every committed context, each with its own captures.
8. Aesthetics, last: the tells of a generated interface (#31 "The default is not a design").

Evidence is one capture per applicable state per scheme per committed context, attached to the feature doc. An applicable state without a capture is not done. "Done" for a screen: the eight checks pass with evidence, and the artifact entry, the code, and the captures agree. A decision the review changes is recorded at the decision location with its reason. The project copies templates/design-review.md and reads it in this order. Nothing checks a capture by script; the reviewer reads it.

## The session

Before any screen work a session reads, in order: References.md § Design Artifact, the brand book, the vocabulary, the tokens, the catalog, then the artifact entries for this feature. A screen the artifact covers is built from its entry. A pattern the artifact lacks is sketched first at decision fidelity (a wireframe, or a written composition: purpose, primary action, order, components, states), recorded as session-decided, then built. The session decides alone: composition within the system, component choice, spacing from the ladder, words in the vocabulary, states and their placement. It asks the owner about: identity, what a primary screen is for, a pattern the product would be recognized by. A screen is proved by its capture set before review.

## Research Notes

Dated notes: anything named in this section is an example from the time of writing and expires. Verify current options at bootstrap.

When bootstrapping this convention:
- Survey the current design-artifact tooling landscape on equal terms: visual design tools, design-system-as-code repositories, an AI design canvas available in the working session, AI design workspaces. Weigh them on what matters: where the owner can see and change the design, cost (recurring spend is an escalation under #29), whether the tool can hold every state, whether the sync can be run from the repository.
- Decide the direction of truth (`repository-first` or `workspace-first`), the sync, and persistence (versioned with code, external), and record the decision at the decision location.
- Fill every labelled line of References.md § Design Artifact. Tool choice is expirable; the discipline of "design before code, living artifact, AI consults it, the owner picks the direction" is durable.
