# Bootstrap: the project context files

Part of the bootstrap playbook (bootstrap/ONBOARD.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step: read it when the script names it, with the reading it lists, and close it before opening the next.

## Step 4.2: References.md and feature-tree.md
Read: Conventions.md; #16; templates/decisions.md; templates/references-platform.md (when the approach is a platform); templates/feature-tree-platform.md (when the approach is a platform); templates/references-frontend.md (when a custom build has a web front end); templates/references-backend.md (when a custom build has a back end); templates/references-mobile.md (when a custom build is a mobile app); templates/feature-tree.md (when the approach is a custom build)
Produces: References.md from the template that fits, with each foundational system kept, or removed with the discovery answer behind the removal written beside it; feature-tree.md; for a custom build docs/systems/, docs/features/, .gitignore, and the first commit
Check: run scripts/validate-bootstrap.py context; evidence: discovery facts recorded in Project, with unresolved facts named and scaffold-only fields left for scaffold
Depends on: bootstrap.3
Skip when: the project is an existing one and Step 4.1 generated these files

Once the build approach is settled per Step 3 (confirmed under `owner-decides`; recommended and not objected to under `ai-decides`), the AI generates the project files. The generation path depends on whether the approach is a platform (Option A/B from Step 3) or a custom build (Option C).

The template is read as it is filled in, the one that fits and no other. Conventions.md is read here as the index that says which systems exist. A convention's full text is not bootstrap reading: the scaffold step that builds a system reads its convention then, researches current practice, and writes how the system is implemented (scaffolding/_preamble.md).

### If the user picked a PLATFORM (Option A or B from Step 3):

The framework's scaffolding phase does NOT apply. There is no tech stack to document, no foundational systems to build, no folder structure to scaffold. The user's project is configuration and content within a third-party platform.

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

Conventions that do NOT apply: everything else (architecture, components, state, styling, types, errors, API, testing, build/CI, etc.). Those are owned by the platform.

Stop after generating References.md, PROFILE.md, feature-tree.md, and VERSION-LOG.md. Help the user sign up for the platform (the sign-up and any payment wait for the owner's explicit yes, #29) and walk through initial configuration.

### If the user picked a CUSTOM BUILD (Option C from Step 3):

Proceed below. This is the path the framework was originally built around.

### For a fullstack project (web frontend + backend API):

The AI runs the generation process TWICE - once for the frontend folder using templates/references-frontend.md, and once for the backend folder using templates/references-backend.md. PROFILE.md is generated once, at the repository root, never per endpoint: stage and decision authority are project-wide (#30). Each endpoint gets its own References.md and feature-tree.md.

### For a single endpoint:

The AI runs once in the project folder, using the matching template (frontend, backend, or mobile).

### Generation Process (for the AI assistant):

Based on the discovery answers, you now know: what platforms, what features, what scale, and what tech stack.

Generate these files:
- References.md using the appropriate template from templates/ (references-frontend.md, references-backend.md, or references-mobile.md).
  - If the project is a **TEMPLATE** (per Group 1), apply the diverging generation rules from the "Template vs product" table: Stage = `template` plus its own version number, add a `## Downstream Projects` section, keep every labelled line of `## Design Artifact` with `Brand decided: deferred to downstream projects` and a recorded working-files folder, note that any `@scope/*` packages ship with neutral placeholder tokens. Do NOT research design tooling — that decision belongs to downstream projects at their own bootstrap.
  - If the project is a **PRODUCT**, research the design-artifact tool at bootstrap on equal terms (a visual design tool, a design-system-as-code repository, an AI design canvas available in the working session, an AI design workspace) on the criteria that matter: where the owner can see and change the design, cost (recurring spend is an escalation under #29), whether it can hold every state, whether the sync can be run from the repository. Record the tool, the direction of truth (`repository-first` or `workspace-first`), the sync, and the working-files folder on their lines of References.md § Design Artifact, and the tool decision at the decision location (#29). The interview and the rest of that section are Steps 4.4 and 4.5. Per convention #27.
- feature-tree.md using templates/feature-tree.md. For TEMPLATE projects, mark design-derived rows (Components, Design System, Styling values, per-feature visual states) as "structural at template level; downstream projects apply brand"; do NOT leave them undefined.
- PROFILE.md is Step 4.3's product, not this step's.
- In References.md § Project, the owner channel, the single decision location, and the reporting pace, per #29. Preserve an existing record; otherwise create DECISIONS.md from templates/decisions.md and record the settled build/scope choices from Step 3.
- docs/systems/ directory (empty)
- docs/features/ directory (empty)
- .gitignore appropriate for the tech stack
- Initialize git with an initial commit

For each foundational system section in References.md:
1. Decide from the discovery answers whether the project needs it. If it does not, remove it from References.md and feature-tree.md and record why.
2. Record what Step 3's research already settled for it (the stack's choice for that slot), and nothing invented beyond that.
3. Leave how it is implemented, and its Location, to the scaffold step that builds it. That step reads the convention and its Research Notes, researches current practice in the chosen stack, writes the how, and reports it so the owner can verify (scaffolding/_preamble.md). Reading every system's convention here, before any of them is built, is reading that is gone by the time it is needed.
