# Bootstrap: the project context files

## Step 4.2: References.md and feature-tree.md
Read: Conventions.md; #16; templates/decisions.md; templates/references-platform.md (when the approach is a platform); templates/feature-tree-platform.md (when the approach is a platform); templates/references-frontend.md (when a custom build has a web front end); templates/references-backend.md (when a custom build has a back end); templates/references-mobile.md (when a custom build is a mobile app); templates/feature-tree.md (when the approach is a custom build)
Produces: References.md from the template that fits, with each foundational system kept, or removed with the discovery answer behind the removal written beside it; feature-tree.md; for a custom build docs/systems/, docs/features/, .gitignore, and the first commit
Check: run scripts/validate-bootstrap.py context; evidence: discovery facts recorded in Project, with unresolved facts named and scaffold-only fields left for scaffold
Depends on: bootstrap.3
Skip when: the project is an existing one and Step 4.1 generated these files

Once the build approach is settled per Step 3, generate the project context for that approach. The path depends on whether the project uses a platform or maintains custom code, not on an option label from the research presentation.

Read the template sections that fit the actual responsibilities as they are filled in. A hybrid can need platform facts and custom-code context without duplicating shared facts. Conventions.md is read here as the index that says which systems exist. A convention's full text is not bootstrap reading: the scaffold step that builds a system reads its convention then, researches current practice, and writes how the system is implemented (scaffolding/_preamble.md).

### Platform configuration without project-owned code

The custom-code scaffold does not apply to provider-owned internals. Record the project's configuration and content responsibilities, then use scaffolding/SCAFFOLD-PLATFORM.md for the applicable configuration work. If the project owns code, follow the custom-code branch below for that code as well.

Generate:
- `References.md` using `templates/references-platform.md` (NOT the frontend/backend/mobile templates — those are for custom builds)
- `PROFILE.md` (Step 4.3) using `templates/profile.md`: the operating stage derived from Group 6, the facts with unknown kept unknown, the decision-authority setting with its source. A platform project still has an audience, data, effects, and an owner who decides (#30, #29).
- `feature-tree.md` from `templates/feature-tree-platform.md`, reshaped as a configuration checklist for the chosen platform (not a systems map)
- `VERSION-LOG.md` with `Type: platform / {platform-name}` in the bootstrap entry
- No `.gitignore`, no `git init`, no `docs/systems/`, no `docs/features/` — the framework doesn't manage the platform's internals

Conventions that still apply:
- #2 (Git) — if the user will version-control platform config files (theme customizations, export files)
- #16 (Documentation) — the References.md IS their documentation
- #23 (App Security) — admin account, 2FA, PII handling within the platform
- #24 (Authorization) — role settings within the platform
- #29 (Decision Authority) and #30 (Operating Profile) — who decides, what is escalated, how careful the configuration must be, and what was deferred

Do not recreate the provider's internal architecture or build systems. Select additional guidance for responsibilities the project actually owns, such as custom styling, data imports or integration behavior. Verify the configured workflows and access controls; provider ownership does not establish that the project's configuration is correct.

Continue the applicable bootstrap records and platform configuration work. Sign-up and any payment wait for the owner's explicit authorization (#29).

### Project-owned code, including a hybrid

Proceed below for the owned code. For a hybrid, include the relevant platform facts in the same project context and link provider-owned capabilities to the integration boundaries. Keep one decision location and one project profile. Apply custom verification, security and maintenance obligations to the code and cross-boundary behavior; do not treat the platform label as an exemption.

### For a fullstack project (web frontend + backend API):

The AI runs the generation process TWICE - once for the frontend folder using templates/references-frontend.md, and once for the backend folder using templates/references-backend.md. PROFILE.md is generated once, at the repository root, never per endpoint: stage and decision authority are project-wide (#30). Each endpoint gets its own References.md and feature-tree.md.

### For a single endpoint:

The AI runs once in the project folder, using the matching template (frontend, backend, or mobile).

A single unit that renders its interface and also owns server responsibilities (its own data store, scheduled work, outgoing messages, server sessions) is still one unit: one References.md and one feature-tree.md, from the frontend template plus the backend template's sections for the server systems it owns. Merge a concern both templates cover (authentication, errors, validation, testing, deployment) into one section, not two. A responsibility neither template names gets a section of its own that points to the guidance and verification that apply.

### Generation Process (for the AI assistant):

Use the settled brief and research. Do not add systems or stack choices merely because the template offers a field for them.

Generate these files:
- References.md using the appropriate template from templates/ (references-frontend.md, references-backend.md, or references-mobile.md).
  - If the project is a **TEMPLATE** (per Group 1), record Stage as `template` with its version, add `## Downstream Projects` for the consumption and upgrade contract, and keep every labelled line of `## Design Artifact`. Record `Brand decided: deferred to downstream projects`, a working-files location for structural design work, and `none` where a field does not apply. Record that downstream products choose their own artifact and identity, and that reusable packages ship neutral tokens. Do not choose a downstream product's design tool or brand here.
  - If the project is a **PRODUCT**, research the current artifact approaches that fit the owner collaboration, state coverage, cost, source-of-truth and synchronization needs. Record the chosen tool or file-based approach, direction of truth, sync and working-files folder, with the decision and its reason at the decision location (#29). The interview and Step 4.5 fill the remaining design fields.
  - Fill § Compliance from discovery (Step 2.5's data answers, Step 2.6's promises already made to users) and Step 3's research; PROFILE.md keeps the regulated-data fact, and an unanswered fact stays unknown. Where a regime requires an audit log, the Audit log line says kept by <unit or service> when another one keeps it, and not required with the reason where no regime asks for one; for a unit that keeps its own, leave the placeholder until scaffold builds the log and records its path. For a web front end, fill § Project's Mobile mode from Step 2.2.
- feature-tree.md using templates/feature-tree.md. For TEMPLATE projects, mark design-derived rows (Components, Design System, Styling values, per-feature visual states) as "structural at template level; downstream projects apply brand"; do NOT leave them undefined.
- PROFILE.md is Step 4.3's product, not this step's.
- In References.md § Project, the owner channel, the single decision location, and the reporting pace, per #29, and Step 2.6's peer-coding answers: `Peer coding` (none, or both assistants as short name and tool) and `Peer roles` in the owner's words (development/PEER-CODING.md). Preserve an existing record; otherwise create DECISIONS.md from templates/decisions.md and record the settled build/scope choices from Step 3.
- docs/systems/ directory (empty)
- docs/features/ directory (empty)
- .gitignore appropriate for the tech stack
- Initialize git with an initial commit

For each foundational system section in References.md:
1. Decide from the discovery answers whether the project needs it. If it does not, remove it from References.md and feature-tree.md and record why.
2. Record what Step 3's research already settled for it (the stack's choice for that slot), and nothing invented beyond that.
3. Leave how it is implemented, and its Location, to the scaffold step that builds it. That step reads the convention and its Research Notes, researches current practice in the chosen stack, writes the how, and reports it so the owner can verify (scaffolding/_preamble.md). Reading every system's convention here, before any of them is built, is reading that is gone by the time it is needed.
