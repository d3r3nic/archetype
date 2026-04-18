# Scaffold Shared Rules (Preamble)

Included by every shape-specific playbook (`SCAFFOLD-BACKEND.md`, `SCAFFOLD-FRONTEND.md`, `SCAFFOLD-MOBILE.md`, `SCAFFOLD-PLATFORM.md`). Single source of truth — do not duplicate these rules inside individual playbooks.

## Zero-stale rule

Every tool, SDK, version, linter rule, or vendor named in the framework is a reference — verify current options at scaffold time. Research Notes in each convention list the CATEGORY of tooling ("a structured logger for the language", "a SAML-capable enterprise auth broker"). Resolve to a specific current choice at scaffold time, not from training-data memory.

## Convention-mapping rule

Every step in the shape-specific playbooks names the conventions it implements (e.g., "build per convention #8 + B3"). Read those convention docs before building the step — they carry the principles, rules, and research triggers. Do not scaffold by enforcement-rule memory alone.

## Handoff-check rule (Step 0 of every playbook)

Read `References.md` in full before building anything:
- **Compliance section** determines which systems are mandatory (audit log, encryption, rate limiting, etc.).
- **Foundational Systems list** is your inventory — every entry must map to a playbook step OR be built as a project-specific extension alongside its nearest sibling.
- **Convention Overrides** document project-specific deviations.
- **Open pre-production gates** in `VERSION-LOG.md` block further scaffolding until resolved (per `bootstrap/RED-FLAGS.md`).

## Smoke-test rule

Every shape-specific playbook ends with a minimal feature exercising the full scaffold end-to-end. Scaffold is NOT complete until the smoke-test feature's integration test passes. A scaffold with every system individually built but not wired together is silently broken.

## Verification discipline

Convention #18 says verify after every change. The playbooks translate this into operational gates: each step has a specific command and specific exit criterion. Do not proceed to the next step if verification fails. Do not stub-satisfy verification ("looks like it would work").

## Commit discipline

One commit per foundational system per convention #2. The commit history IS the rollback ladder.

## Red-flags rule

Before scaffolding, read `scaffolding/RED-FLAGS.md` — 13 known silent-failure patterns. Consult it during each step. If a red flag fires, STOP and resolve before continuing.

## Machine-verifiable exit gate

Run `scripts/validate-scaffold.sh` at the end. Do not commit a scaffold that fails the validator. Do not paper over failures. Re-build the broken system; re-run.
