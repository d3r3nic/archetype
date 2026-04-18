# Phase 2: Scaffold — Router

Build the foundational systems described in `References.md`. Run after bootstrap. Each system is built following convention #0 (Reusability) — built once, configured for context, used by every feature.

**This file is a router.** Most content lives in the shape-specific playbooks below. Read this preamble in full, then jump to the playbook matching your project shape.

## Prerequisites

- Phase 1 (Bootstrap) complete.
- `References.md` exists with tech stack, foundational-systems list, compliance section, convention overrides.
- `feature-tree.md` initialized with systems marked `not started`.
- `VERSION-LOG.md` has a Bootstrap entry. Any open pre-production gates documented there are resolved OR the scaffold halts per `bootstrap/RED-FLAGS.md`.

## Route by project shape

Determine the shape from `References.md`:

- **Backend** (API, worker, service, GraphQL server, data pipeline, etc.) → `scaffolding/SCAFFOLD-BACKEND.md`
- **Frontend** (web app, SPA, SSR app, PWA) → `scaffolding/SCAFFOLD-FRONTEND.md`
- **Mobile** (native iOS/Android, cross-platform mobile) → `scaffolding/SCAFFOLD-MOBILE.md`
- **Platform** (user picked Shopify / WordPress / SimplePractice / etc. in Step 3) → `scaffolding/SCAFFOLD-PLATFORM.md`
- **Fullstack with separate frontend + backend folders** → run SCAFFOLD-FRONTEND in the frontend folder AND SCAFFOLD-BACKEND in the backend folder. Each has its own `References.md` and `feature-tree.md`.

Do NOT attempt to build from this router directly. The shape-specific playbooks have the ordered steps and the convention mappings.

## Shared rules (apply across all shapes)

All shared scaffold rules live in `scaffolding/_preamble.md`. Read that file before following any shape-specific playbook — it covers:
- Zero-stale rule (no expirable specifics)
- Convention-mapping rule (each step names its conventions)
- Handoff-check rule (read References.md compliance + foundational-systems inventory before building)
- Smoke-test rule (scaffold not complete until end-to-end smoke test passes)
- Verification discipline (operational exit criteria, not "looks like it works")
- Commit discipline (one commit per system)
- Red-flags rule (consult `scaffolding/RED-FLAGS.md`, 13 silent-failure patterns)
- Machine-verifiable exit gate (`scripts/validate-scaffold.sh` must pass)

Single source of truth — do not restate these rules inside the shape-specific playbooks. Update `_preamble.md` to change them.

## System Documentation Template

Every scaffolded system gets a doc at `docs/systems/{system-name}.md`:

```
# {System Name}

Convention: #{number} ({convention name}) [+ #{other} if cross-cutting]

## What It Is
[One paragraph explaining the system and its responsibility]

## Where It Lives
[Exact file paths — every file the system owns]

## How Features Use It
[Exact import statement using the project's path alias, e.g.:]
import { NotFoundError } from '@/shared/errors'

[Usage example showing the most common pattern]

## How to Verify
[Specific command. Specific expected output.]

## Configuration
[How to extend or configure for different contexts]
```

The "How to Verify" subsection is non-optional — it's how the next developer (or agent) confirms the system works.

## Post-scaffold required outputs

Every shape-specific playbook ends with:

1. `docs/systems/{name}.md` for every foundational system.
2. `feature-tree.md` with each system marked with its real location.
3. `References.md` updated with actual paths, DB/API summaries where applicable.
4. `.env.example` at project root with every required env var documented (no real values).
5. `VERSION-LOG.md` appended with a Scaffold entry — see template at bottom of this file.
6. Initial "scaffold complete" commit AFTER `scripts/validate-scaffold.sh` passes.
7. Platform projects use `docs/runbook.md` instead of `docs/systems/` — see SCAFFOLD-PLATFORM.

## VERSION-LOG Scaffold entry template

Append to `VERSION-LOG.md` after scaffold completes:

```
## Scaffold

Date: [today's date]
Type: [custom / platform]
Shape: [backend / frontend / mobile / platform / fullstack]
Sessions: [how many discrete AI sessions it took]
Systems built:
- [system name] → [location] (convention #N, verify: `<command>` exit 0)
- [system name] → [location] (convention #N, verify: ...)
- ...
Systems deferred: [which ones and why, with References.md implications]
Smoke-test feature: [path] — integration test status
Red flags fired: [which RED-FLAGS.md item, how it was resolved]
validate-scaffold.sh: [pass / fail, with pass required to mark scaffold complete]
Dependencies installed: [key packages]
Conventions read: [which convention docs were read during scaffolding]
```

## What scaffolding produces

A working, empty project with all foundational systems in place plus ONE smoke-test feature that exercises every system. No business features yet. Any feature can be built immediately by plugging into these systems.

The scaffold is REUSABLE. Projects with the same tech stack can start from this base.

## Scaffolding documentation

Every decision made during scaffolding that deviates from the conventions or makes a stack-specific choice is recorded in `References.md` under "Convention Overrides." Research-at-scaffold decisions (e.g., which linter rules were chosen for the stack's AI-prone categories) are also recorded there.

## Next step

Phase 3 (Develop): build business features on top of the scaffolded systems. See `development/DEVELOP.md`.
