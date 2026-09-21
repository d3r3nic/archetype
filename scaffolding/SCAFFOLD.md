# Phase 2: Scaffold — Router

Build the foundations the project has justified in References.md. Run after bootstrap. Convention #0 guides whether an existing capability, an adaptation or a focused implementation best serves the requirement.

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
- **Platform** (user picked a hosted platform — storefront, site builder, practice-management suite, workspace tool — in `bootstrap/ONBOARD.md` Step 3) → `scaffolding/SCAFFOLD-PLATFORM.md`
- **Fullstack with separate frontend + backend folders** → run SCAFFOLD-FRONTEND in the frontend folder AND SCAFFOLD-BACKEND in the backend folder. Each has its own `References.md` and `feature-tree.md`.

Use a listed playbook when its assumptions fit the project. If the researched approach does not fit these routes, identify the applicable concerns and missing workflow/check coverage in the project plan. Do not mislabel the project to force a route. A project-specific extension needs explicit verification and cannot be claimed as supported by the step runner unless it uses a declared playbook that the runner actually recognizes. This router alone is not an implementation procedure.

A playbook that declares a step ledger (development/STEPS.md) is walked with `scripts/next-step.sh`: add its ledger id after `bootstrap` on the Playbooks line of PROGRESS.md and the script names each step, the file that holds it, and its reading. The frontend playbook is stepped this way (`scaffold-frontend`). For an unconverted route, use development/TASKS.md to carry its sequence, dependencies, checks and recovery in the existing implementer plan. Preserve its substantive verification requirements; do not declare runner coverage that does not exist.

## Shared rules (apply across all shapes)

All shared scaffold rules live in `scaffolding/_preamble.md`. Read that file before following any shape-specific playbook — it covers:
- Zero-stale rule (no expirable specifics)
- Convention-mapping rule (each step names its conventions)
- Handoff-check rule (read References.md compliance + foundational-systems inventory before building)
- Smoke-test rule (scaffold not complete until end-to-end smoke test passes)
- Verification discipline (operational exit criteria, not "looks like it works")
- Commit discipline (coherent verified recovery points)
- Red-flags rule (consult `scaffolding/RED-FLAGS.md`, the silent-failure catalogue)
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
[Link the authoritative location in feature-tree.md or References.md; name additional paths only when a consumer needs them.]

## How Features Use It
[The actual public entry point and a short usage example where needed. Use the project's selected interface, which need not be a module import.]

## How to Verify
[Link the command in References.md and explain the expected behavior. Add a local command only when it is specific to this system.]

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

A working, empty project with every applicable foundational system in place, or recorded as a deferral with its trigger per the operating stage (#30, `_preamble.md` stage rule), plus ONE smoke-test feature that exercises every system that was built. No business features yet. Any feature can be built immediately by plugging into these systems.

A scaffold can be reused when another project shares its assumptions. Verify that fit before inheriting its architecture or obligations.

## Scaffolding documentation

Record consequential choices and their reasons at the project's existing decision location (#16). References.md identifies selected implementations, commands and justified convention choices; system docs explain contracts and use. Link these records rather than copying reasons into each. Keep revision-specific verification in the log as history.

## Next step

Phase 3 (Develop): build business features on top of the scaffolded systems. See `development/DEVELOP.md`.
