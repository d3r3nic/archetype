# Convention #27: Design Foundation

## Applies when

The product has screens or other designed surfaces people use. What varies: whether the project is a product or a template that downstream products brand (see the lifecycle table below), the design tool the project chose, and where the design lives relative to the code. A back end alone or a platform build with no screen of its own skips this convention.

## Principle

The design comes before the screen and stays in step with the code. Interface decisions (the states of a screen, the feedback an interaction gives, which action is primary, the visual hierarchy) come from the design artifact, not from improvisation. The session consults the artifact first. Where it is silent, the session designs the missing piece within the picked direction, from the artifact's own patterns and #31, and records it; the owner is asked only when the gap is theirs (#29). A screen is never improvised outside the system.

Design is upstream of #6 (styling) and #22 (interface foundation). This convention governs the discipline; the tools and implementation boundaries are chosen per project. A design tool that runs in the project (a design skill, a plugin, a canvas, a design workspace) works from the artifact and the recorded styling source, never around them.

## Reusable System

One design artifact per project, in the format the project chose (a visual design file, a design system kept as code, an interactive prototype, a design workspace's output). It is:
- living: updated with the code, not a one-off handoff;
- referenced: every interface decision traces back to it;
- discoverable: References.md § Design Artifact records where it is, the direction of truth, the sync, and whether the brand is decided, so every new session and every design tool finds it and reads it first.

## Rules

- The design artifact exists before feature implementation begins. Research the current design tools at bootstrap and record the chosen tool and the artifact's location in References.md.
- Design every state a screen can be in. Each state tells the person what happened, what they can do next, and what was kept. The states to consider: empty (nothing yet), no results (filtered to nothing), loading, partial, error, success, disabled, offline, stale, conflict, first run, permission denied, overflow (long text, long lists, many of a thing). This is the one list; other files cite it. Disabled and overflow usually belong to components rather than screen composition.
- When the artifact is silent, the session designs the missing piece from the artifact's own patterns and #31, records it in the artifact as a session-decided entry in the same change (templates/design-artifact-entry.md), and ships it with the record. It neither waits nor improvises outside the system. The owner is asked only when the gap is theirs: a new visual identity, a change to what a primary screen lets a person accomplish, or a pattern the product would be recognized by (#29). A session-decided entry stays marked until the owner's later word supersedes it; silence adopts nothing.
- When code and artifact diverge, update one or the other. Silent drift is a violation.
- The recorded styling contract (#6) and interface boundary (#22) derive from the artifact. When an accepted design decision changes, the dependent code and evidence follow.
- Who picks the look, and how a design tool's output is adopted, is stated once, under "Design tools" below.

## Violations

- A screen shipped with no artifact entry.
- A state left undesigned in production: an error "to be decided", a one-off spinner, a hand-rolled empty placeholder.
- The artifact not updated when the screen changes in code.
- A session waiting on the owner for a composition question the direction already settles.
- A screen reviewed only on its happy path, or reviewed by the session that built it.
- A design tool's own aesthetic defaults applied over the brief: a typeface, palette or direction the artifact already fixed.
- The AI choosing the product's visual identity without the owner's pick or the owner's delegation in words (#29).
- Two design sources with no recorded direction of truth, or a mockup's literal value or control copied into code without the recorded styling and interface adoption.
- Design working files scattered outside the recorded folder, inside the engine folder, or uncommitted; a generated bundle committed.

## Wrong vs Right

- WRONG: the artifact has no error state for a list, so the session sends the owner three placements and waits, or codes one with no record. RIGHT: the session applies the error pattern the artifact already uses elsewhere, records the entry as session-decided, and the owner sees it in the session summary.
- WRONG: the artifact gains a new button variant and the code keeps the old one; months later they cannot be reconciled. RIGHT: an artifact change triggers the code follow-up, and a code change triggers the artifact update; they are two views of one source of truth.
- WRONG: a design tool run in a product with a settled artifact chooses new typefaces and a fresh palette because its own guidance says to be distinctive. RIGHT: the artifact and the styling source are the brief; the tool's distinctiveness goes into composition, hierarchy and states.
- WRONG: under `ai-decides` the AI picks the brand palette and moves on. RIGHT: sketched directions, one recommended, the owner picks, the pick is recorded with the artifact revision, and the AI executes without asking again.

## Where in the project lifecycle interface decisions happen

| Lifecycle moment | Who decides the look | What they decide |
|---|---|---|
| Template project bootstrap (project type: template) | Nobody decides brand | The template records a replaceable styling and interface boundary with neutral placeholder values. No colors, type or iconography are invented. The design artifact is deferred. |
| Template project scaffolding | Nobody decides brand | The technical boundary is exercised only as far as the template's real consumers and checks require. |
| **Product project bootstrap (project type: product)** | **This is where the look is decided** | The AI researches the tool and records the direction of truth. The artifact is authored. Brand decisions are committed, or the directions are prepared and the pick stays open: the scaffold builds neutral placeholder values and no screen feature ships until the owner picks or delegates. |
| Product project feature work | The artifact decides | The session consults the artifact first; a gap is designed within the picked direction and recorded as session-decided; the owner is asked only when the gap is theirs. |

So a request to change a button's color or add an icon belongs to a product. In a template it is deflected: "this template is brand-neutral; the look is decided when a product is made from it."

## Design tools

A design skill, plugin, canvas or design workspace that runs in the project works from the same brief the code does.

- The brief. The artifact, the brand decisions, the vocabulary, the recorded styling source, the interface discovery surface when there is one, PROFILE.md and the project type, all found through References.md § Design Artifact, are the standing brief for any design tool. Where a tool's own defaults conflict with the brief, the brief wins. Where the brief is silent, the tool researches current evidence and proposes directions for the owner's choice.
- Design content versus code. A mockup, artboard, canvas file, preview or prototype is design content. For a screen or flow it shows the applicable states; a piece that is not a screen (a poster, a one-page document, a report) shows what its purpose needs and follows the brand layer and #31 "Words". It respects the accessibility floor (#14) and the project's accessibility target. It carries made-up content only, never real customer or personal data (#30); in a template project it carries no brand values. It is exempt from code-construction rules, tests (#12) and lint gates (#25): a canvas that needs literal inline values and draws its own controls is not a violation. Code adopts the accepted design through the recorded styling source and interface boundary; it does not copy mockup values or controls without provenance.
- A tool's output is a proposal until adopted. A direction is adopted by the owner's pick; a change within the settled direction is adopted by updating the artifact.
- Direction of truth, recorded once. References.md § Design Artifact declares `repository-first` (the styling source, specifications and any interface previews in the repository are the artifact; a workspace or canvas is a published view or a proposal) or `workspace-first` (the workspace or canvas is the artifact; the repository follows it). Never both. The sync between the two is recorded with it: the step, who runs it, and when. A state in which the two disagree is drift. The choice is a consequential decision, recorded at the decision location (#29).
- Who picks. Visual identity (palette, type, tone, brand marks) and what each primary screen must let a person accomplish are the owner's, part of what the product is (#29). The AI proposes two to four genuinely different directions at decision fidelity (sketches, not finished screens), each with its motivation and its trade-off, one recommended; the owner picks; the pick is recorded at the decision location with the artifact revision. After the pick the artifact governs and the session executes without asking again; the no-owner case and the fidelity rule are in #29. Composition within the direction is the session's (#31 and the silence rule above). The design interview (bootstrap/DESIGN-INTERVIEW.md) supplies what the directions are built from and offers the owner both ways: the pick from shown directions, or the delegation in words (#29). A skipped form delegates nothing. Under delegation the AI shows one direction with the alternatives it set aside named beside it, and records it as owner-delegated. Directions are shown, never only described: in the design tool the session has, or as static pages in the design working-files folder.
- Templates. A design tool run in a template project produces wireframes, layouts and states with neutral placeholder values; a request for brand values is deflected to the product made from the template.
- Where the files live. Working files a design tool produces are the artifact's source under `workspace-first` and supporting material under `repository-first`. Either way they live in the folder recorded on the `Design working files` line (a folder a tool fixes for itself counts and is recorded as it is), never scattered and never inside the engine folder, and they are committed. Generated bundles are build output: not committed, with the ignore rule recorded and the published link in References.md.

`scripts/validate-design.sh` reads a project's § Design Artifact for what it can check without judging the design: one live section when the project is known to have a screen, no line left as its template placeholder, and `Brand decided: yes` refused while `First task` or `Return tasks` is unknown, because a direction composes the screen for the first return task. The bootstrap and the scaffold gate run it.

What the framework cannot check: whether a mockup was consulted, whether the owner's pick was real, whether a workspace view is current, whether a mockup's states are complete, whether a session-decided entry should have been an owner question, whether a capture matches the shipped screen, or whether a recorded value is true. The sessions and the independent review read that.

## Design review

A screen is reviewed by someone who did not build it (#29), against the artifact, with evidence for the states that changed. The review covers:
- purpose: a person can do what the screen is for, without help;
- hierarchy: the order of attention leads to the right actions (#31);
- states: each applicable state is present and tells what it must;
- words: the vocabulary, and errors that say what happened and what to do (#31);
- system fidelity: the recorded styling and interface contracts are followed, and accepted values stay traceable (#6, #22);
- the accessibility floor: focus, keyboard, contrast in each scheme, targets, reflow, reduced motion (#14);
- each committed scheme and context the change affects;
- aesthetics, last (#31 "The default is not a decision").

Evidence is the current captures of the changed states in the schemes and contexts they affect, from the recorded `capture:` command, plus observed interaction for what a still image cannot show: keyboard, focus, reduced motion, completing the task. A capture nobody opened is not evidence; the review says what each one shows, and a blank frame or the wrong state is a finding. The feature record links the captures, and templates/design-review.md is the review's form. A changed direction, context or scheme reopens dependent work through development/STEPS.md before old evidence counts again.

## The session

Before any screen work a session reads References.md § Design Artifact, the brand book, the vocabulary, the recorded styling source, the interface discovery surface when there is one, and then the artifact entries for this feature. A screen the artifact covers is built from its entry. A pattern the artifact lacks is sketched first at decision fidelity (a wireframe, or a written composition: purpose, action hierarchy, order, components, states), recorded as session-decided, then built. The session decides composition, component choice, spacing, words, states and placement within the accepted direction and the recorded implementation contracts. It asks the owner only when the gap is theirs.

## Research Notes

Survey the design tools on equal terms: visual design tools, design systems kept as code, a design canvas in the working session, design workspaces. Weigh where the owner can see and change the design, cost (recurring spend is an escalation under #29), whether the tool can hold every state, and whether the sync can run from the repository. Record the direction of truth, the sync and where the files live at the decision location, and fill References.md § Design Artifact.
