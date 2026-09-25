# Scaffold — Frontend

Routed from `scaffolding/SCAFFOLD.md` when the project is a frontend (web app, SPA, SSR app). Steps ordered so each system can be built and verified before the next depends on it.

Step ledger: scaffold-frontend
Step files: scaffolding/SCAFFOLD-FRONTEND-01-SETUP.md; scaffolding/SCAFFOLD-FRONTEND-01B-SITE-CONFIG.md; scaffolding/SCAFFOLD-FRONTEND-02-THEME.md; scaffolding/SCAFFOLD-FRONTEND-03-ERRORS.md; scaffolding/SCAFFOLD-FRONTEND-04-COMPONENTS.md; scaffolding/SCAFFOLD-FRONTEND-05-STATE.md; scaffolding/SCAFFOLD-FRONTEND-06-API.md; scaffolding/SCAFFOLD-FRONTEND-07-AUTH.md; scaffolding/SCAFFOLD-FRONTEND-08-ROUTING.md; scaffolding/SCAFFOLD-FRONTEND-09-FORMS.md; scaffolding/SCAFFOLD-FRONTEND-10-TESTING.md; scaffolding/SCAFFOLD-FRONTEND-10B-DATA-RESOLUTION.md; scaffolding/SCAFFOLD-FRONTEND-10C-OPERATION-STREAMS.md; scaffolding/SCAFFOLD-FRONTEND-10D-SUBPROCESS-BOUNDARY.md; scaffolding/SCAFFOLD-FRONTEND-11-PERFORMANCE-CI.md; scaffolding/SCAFFOLD-FRONTEND-11A-DEPLOYMENT.md; scaffolding/SCAFFOLD-FRONTEND-11B-PULSE-MONITOR.md; scaffolding/SCAFFOLD-FRONTEND-12-SMOKE-TEST.md; scaffolding/SCAFFOLD-FRONTEND-13-EXIT-GATE.md

When this frontend route fits the project, add `scaffold-frontend` after `bootstrap` on the Playbooks line of PROGRESS.md. Run `scripts/next-step.sh` from the project root for the current step and its reading. Reuse current session context; inspect newly relevant guidance when the task changes. Transition and recovery details live in development/STEPS.md.

## Step 0: Handoff check
Read: scaffolding/_preamble.md; scaffolding/RED-FLAGS.md § 1. Skipped-by-interpretation (project-shape tag); scaffolding/RED-FLAGS.md § 12. Implicit "skip if not regulated" treated as "skip because I don't want to build it"; scaffolding/RED-FLAGS.md § Handling a fired red flag; project: References.md; project: PROFILE.md; project: VERSION-LOG.md
Produces: the inventory of the systems this project builds, and every open pre-production gate either resolved or the scaffold halted on it
Check: evidence: the systems inventoried, and each open gate in VERSION-LOG.md with how it was resolved, or none open
Depends on: bootstrap.6

Read `References.md` in full:
- **Compliance section** — regulated data changes auth, logging, and storage choices; PROFILE.md holds the regulated-data fact.
- **Foundational Systems list** — inventory every system; missed systems = silently skipped.
- **Mobile mode** (§ Project) — what the product commits to on a phone; when it commits to an installable web app, Step 8 below adds what that needs (service worker, manifest).
- **Open pre-production gates** in `VERSION-LOG.md` — halt until resolved.

## The steps

| Step | System | File |
|---|---|---|
| 0 | Handoff check | this file |
| 1 | Project setup and types | scaffolding/SCAFFOLD-FRONTEND-01-SETUP.md |
| 1b | Global site config (content, not code) | scaffolding/SCAFFOLD-FRONTEND-01B-SITE-CONFIG.md |
| 2 | Theme system | scaffolding/SCAFFOLD-FRONTEND-02-THEME.md |
| 3 | Error handling | scaffolding/SCAFFOLD-FRONTEND-03-ERRORS.md |
| 4 | Design-system and component foundation | scaffolding/SCAFFOLD-FRONTEND-04-COMPONENTS.md |
| 5 | State management | scaffolding/SCAFFOLD-FRONTEND-05-STATE.md |
| 6 | API layer (client side) | scaffolding/SCAFFOLD-FRONTEND-06-API.md |
| 7 | Auth | scaffolding/SCAFFOLD-FRONTEND-07-AUTH.md |
| 8 | Routing, layouts, and the service worker for an installable web app | scaffolding/SCAFFOLD-FRONTEND-08-ROUTING.md |
| 9 | Forms | scaffolding/SCAFFOLD-FRONTEND-09-FORMS.md |
| 10 | Testing | scaffolding/SCAFFOLD-FRONTEND-10-TESTING.md |
| 10b | Data resolution layer | scaffolding/SCAFFOLD-FRONTEND-10B-DATA-RESOLUTION.md |
| 10c | Long-running operation streams | scaffolding/SCAFFOLD-FRONTEND-10C-OPERATION-STREAMS.md |
| 10d | Subprocess input boundary | scaffolding/SCAFFOLD-FRONTEND-10D-SUBPROCESS-BOUNDARY.md |
| 11 | Performance, build, and CI | scaffolding/SCAFFOLD-FRONTEND-11-PERFORMANCE-CI.md |
| 11a | Deployment discipline | scaffolding/SCAFFOLD-FRONTEND-11A-DEPLOYMENT.md |
| 11b | Pulse Monitor (dev-only project visibility) | scaffolding/SCAFFOLD-FRONTEND-11B-PULSE-MONITOR.md |
| 12 | Smoke-test feature (the integration proof) | scaffolding/SCAFFOLD-FRONTEND-12-SMOKE-TEST.md |
| 13 | Exit gate and the scaffold record | scaffolding/SCAFFOLD-FRONTEND-13-EXIT-GATE.md |

## feature-tree status discipline

As each system lands during scaffold, update the feature-tree.md row in-place:

- `not started` → `in progress` when the directory exists and first file lands.
- `in progress` → `implemented` when tests green + system doc in `docs/systems/<name>.md` explains "what's here / what's NOT here yet / verification".
- Location column fills in real path (was `[scaffold fills]`).
- Audit Log gets one entry per scaffold sub-phase (e.g. "B1 monorepo skeleton", "B2 non-UI foundation", "B3 tokens + UI + docs").

Never leave a row at `not started` after its code ships: the status is what the pulse snapshot shows and what the next session reads.

## Monorepo template projects — extra lens

Template-shape projects (a codebase distributed as packages for other projects to consume) add a second distribution axis beyond "deploy the app":

- Each package has a manifest with real scoped `name`, SemVer `version`, explicit `files` shipping list, and peer-dependencies for consumer-owned runtime (the view framework, the language runtime, etc.) so consumers aren't forced into the template's versions.
- **SemVer discipline via a version-management tool** (research current best): one change-file per change, a command rolls versions + generates per-package CHANGELOG, a command publishes to the registry (or packs for local testing).
- Progressive extraction: build a feature in the reference app first, extract to a package when the pattern stabilizes. The template keeps its own project-owned consumer walkthrough and maintainer playbook docs.
- If the bundler needs help consuming packages that ship raw source: use the bundler's transpile-dependency option (research current).

## Next Step

The scaffold is complete when Step 13's exit gate passes. Proceed to development/DEVELOP.md for the first feature; its work is carried in the implementer plan (development/TASKS.md). Server systems this unit owns that the ledger has no steps for are complete only when the implementer plan closes them (scaffolding/SCAFFOLD.md).
