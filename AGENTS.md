<!-- archetype-managed-entrypoint -->
# Working with Archetype

In project installations this file is centrally managed and is replaced by each framework update. Local AI must not edit, delete, or replace it to change a project's rules. Put project facts in References.md, local guidance in CLAUDE.md.additions, justified convention choices in conventions/overrides/, and task bindings in protocols/task-context.md. Propose shared changes upstream. Resolve engine paths from the installed framework folder; project artifacts live at the project root. The installed revision is recorded in VERSION-LOG.md. Explicitly read referenced files; do not assume the client expands imports. These repository instructions remain subject to the active instruction hierarchy and granted permissions.

## Judgment before implementation

Understand the owner's intended outcome and constraints. Identify what is uncertain, inspect existing work, and research current relevant evidence before a consequential choice. Compare alternatives on fit, risks, maintenance and cost. Research may overturn your initial answer; popularity, novelty and examples in this framework do not settle the decision. Reuse evidence that is still current rather than repeating research without a reason.

Conventions describe concerns and approaches to evaluate. Architectural and visual patterns are not universal solutions. Select what serves this project and explain consequential departures at its existing decision location (#0, #16, #29). Preserve accepted project commitments until they are deliberately changed; record affected dependencies, reopen declared ledger records through development/STEPS.md, and revisit unconverted work through development/TASKS.md. A different approach never permits fabricated evidence, ignored owner requirements or silently bypassed checks.

Respect the active instruction hierarchy, permissions and the decision authority in PROFILE.md. The owner decides product intent and commitments; the AI investigates and recommends technical choices, acting within that authority. Use conventions/29-decision-authority.md when an action affects spending, external commitments, live systems, irreversible effects or product scope. Use conventions/30-operating-profile.md for exposure, obligations and justified deferrals. Protect secrets and trust boundaries. Say what is unverified; completion requires evidence appropriate to the claimed outcome.

## Find the relevant work

- Read project-root CLAUDE.md.additions first when it exists: it holds this project's own standing rules. Read other applicable local guidance and the current project purpose, constraints and decision-authority facts. Reuse facts already current in this session; inspect relevant source when a record may be stale.
- If References.md is absent, begin at bootstrap/ONBOARD.md. Do not invent the project's context.
- For work covered by a declared route in PROGRESS.md, run scripts/next-step.sh from the project root and close its current step on the required check and evidence. A completed bootstrap ledger does not cover later work automatically. The script checks recorded steps, not what you read or how well you reasoned. Read development/STEPS.md for transitions when needed.
- Select scaffolding/SCAFFOLD.md, development/DEVELOP.md or development/MAINTAIN.md for the work at hand. Outside declared automated routes, carry the sequence, dependencies, checks and next action in the existing implementer plan under development/TASKS.md. Use Conventions.md to find relevant concerns, including cross-cutting risks; read newly relevant guidance when scope changes.
- Read the relevant sections of References.md, feature-tree.md, local overrides, protocols and catalogs. Check the code for existing behavior before extending or replacing it. For backend work, backend/Conventions.md supplies additional routes.
- Pulling a newer framework into the project follows development/UPDATE.md.
- Tracked work also follows development/TASKS.md, development/FRESHNESS.md and the project-root protocols/task-context.md binding when present. These govern ownership and freshness, including non-code work.

## Before claiming completion

Use the project's verification commands and the applicable framework gate. A failure needs investigation; a justified alternative needs a truthful check of its own contract, not a false pass or a weakened assertion. A source heuristic is not proof of correctness. Follow conventions/18-verification.md and obtain independent review under conventions/29-decision-authority.md.

For screen work, use References.md's Design Artifact and conventions/27-design-foundation.md. Preserve supplied requirements through delegation. Record the chosen direction and session decisions, inspect current captures and exercise interactions; screenshots alone do not prove behavior. Design tools and other AI outputs are proposals to evaluate against the same brief.

Keep current facts at their authoritative location, record non-obvious decisions and evidence, and link dependent records instead of copying reasons. Use conventions/16-documentation.md. Make verified, recoverable changes under conventions/02-git.md within the authorization granted for this project.

When authorized to work on Archetype itself, follow the factory's development instructions and record the change there before publishing the framework. Do not bootstrap the framework source as a downstream project.
