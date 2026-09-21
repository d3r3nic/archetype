# Scaffold Shared Rules (Preamble)

Included by every shape-specific playbook (`SCAFFOLD-BACKEND.md`, `SCAFFOLD-FRONTEND.md`, `SCAFFOLD-MOBILE.md`, `SCAFFOLD-PLATFORM.md`). Single source of truth — do not duplicate these rules inside individual playbooks.

## Framework vs project artifacts

The framework encodes the developer's CHARACTER (instincts, patterns, judgment) — durable. Project artifacts (References.md, feature-tree.md, conventions/overrides/, docs/features/, docs/systems/, CLAUDE.md.additions) hold SPECIFICS for THIS project — expirable and that's fine.

- **Framework must NOT contain:** specific tool names as THE answer, specific API calls, version numbers, current pricing, vendor product names as prescriptions.
- **Project artifacts SHOULD contain:** the specific tools THIS project uses, current versions, current pricing, current vendor choices. That's their job.

When you scaffold, record the actual researched choice and its reason in project artifacts. Generic descriptions do not make an architecture universal: evaluate the approach as well as the tool. An existing project commitment remains in force until deliberately revised (#0, #16, #29).

## Zero-stale rule (framework only)

Every tool, SDK, version, linter rule, or vendor named in the framework is a reference. Verify changing facts that matter to the current choice; reuse evidence that is still current. Research Notes in each convention list the CATEGORY of tooling ("a structured logger for the language", "a SAML-capable enterprise auth broker"). Resolve to a specific current choice at scaffold time, not from training-data memory. The specifics land in project artifacts, not in framework edits. Where a framework file keeps one concrete illustration, it sits on a line beginning `Dated example:`; read those as expired until re-verified, never as a prescription.

## Convention-mapping rule

Every step in the shape-specific playbooks names the conventions it implements (e.g., "build per convention #8 + B3"). Read those convention docs before building the step — they carry the principles, rules, and research triggers. Do not scaffold by enforcement-rule memory alone.

Read the relevant concern when making the decision it informs. Research uncertain or changing practice for the selected runtime and consider evidence against the initial choice. If research access is unavailable, say which facts remain unverified. Put the selected implementation and entry point in References.md; keep its consequential reason at the existing decision location. Reuse unchanged material already read in this session.

## Handoff-check rule (Step 0 of every playbook)

At scaffold handoff, read the current project purpose, constraints and accepted decisions in `References.md`, including:
- **Compliance section** determines which systems are mandatory (audit log, encryption, rate limiting, etc.).
- **Foundational Systems list** is your inventory — every entry must map to a playbook step OR be built as a project-specific extension alongside its nearest sibling.
- **Convention Overrides** document project-specific deviations.
- **Open pre-production gates** in `VERSION-LOG.md` block further scaffolding until resolved (per `bootstrap/RED-FLAGS.md`).

## Stage rule (operating profile)

Read `PROFILE.md` with References.md. The stage (#30) decides what this scaffold may defer:
- `isolated`: may defer remote deployment, capacity engineering, operational dashboards, integrations for capabilities the experiment does not exercise, and detailed research for unused systems. May not defer the recorded purpose and success criteria (References.md), protected configuration, the trust boundary of anything reachable, reproducible verification, containment of the experiment from live systems, or the smoke test.
- `trial`: adds boundary, integration, permission, and recovery checks for everything the participants can reach.
- `operational`: nothing is deferred without a recorded reason and a trigger.

Every deferral is a `TECHNICAL-DEBT.md` entry with `Kind: deferral`, a `Control`, and a `Due-before` trigger or date (templates/technical-debt.md). A floor item (secrets, trust boundaries, irreversible effects, personal data, authorized reuse, honest completion) is never deferred. "Later" without an entry is a loose end, and `scripts/validate-profile.sh` treats a deferral without a trigger as malformed. A deferred foundational system keeps its row in feature-tree.md with Status `deferred (TD-N)` and a docs/systems/ page that says what is deferred and until which trigger, so `scripts/validate-scaffold.sh` reads the page like any other and the deferral stays visible; the smoke test still covers everything that was built.

## Smoke-test rule

Every shape-specific playbook ends with a minimal feature exercising the full scaffold end-to-end. Scaffold is NOT complete until the smoke-test feature's integration test passes. A scaffold with every system individually built but not wired together is silently broken.

## Verification discipline

Convention #18 requires evidence at coherent change boundaries and all applicable required gates before acceptance. Each declared scaffold step supplies its own command and exit criterion. Do not proceed to the next step if verification fails. Do not stub-satisfy verification ("looks like it would work").

## Commit discipline

Keep coherent verified recovery points under convention #2 and the repository authorization. Grouping follows change boundaries and reviewability, not the number of systems in a checklist.

## Red-flags rule

For a stepped playbook, read the sections of `scaffolding/RED-FLAGS.md` named by the current step. An unconverted playbook reads the catalogue before scaffolding. If a red flag fires, STOP and resolve before continuing.

## Machine-verifiable exit gate

Run `scripts/validate-scaffold.sh` at the end and investigate its diagnostics. It includes layout and source-pattern heuristics; a mismatch can require a correction to a check or a supported project mapping, not a forced architecture. A real failure remains blocking. Never suppress evidence, misstate applicability or report an unsupported approach as verified. Record the limitation if no truthful supported check is available.
