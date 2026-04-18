# Scaffold — Platform Projects

Routed from `scaffolding/SCAFFOLD.md` when the project chose a platform (Option A from `bootstrap/ONBOARD.md` Step 3) rather than a custom build.

**Scaffolding mostly does not apply.** The framework's scaffold phase is for building foundational code systems. Platform projects have no code to scaffold — the platform already owns the systems (auth, database, errors, state, routing, UI, CI, etc.).

What platform projects DO need from scaffold:
- Platform configuration walkthrough per the chosen platform's admin tools.
- Documentation of decisions made during platform setup.
- Version control for any exportable config (theme files, automation definitions, etc.).
- The non-code conventions that still apply (#2 git, #16 docs, #23 app security, #24 authorization).

This is more "platform onboarding" than scaffolding. Follow `templates/references-platform.md` Configuration Checklist for the chosen platform type (sector-tagged).

## Step 0 — Handoff check

Read `References.md`:
- **Platform name + plan/tier** — confirm these are current. Pricing and features change.
- **Configuration Checklist** — the sector-tagged block in References.md is your build target.
- **Out-of-Scope Systems** — confirm the framework conventions that do NOT apply.

## Step 1 — Platform account setup

Follow the baseline sections of the References.md Configuration Checklist:
- Account created with owner email.
- 2FA enabled on owner account.
- Billing setup with the chosen plan.
- Custom domain connected and SSL verified.
- Legal pages published (privacy, terms, cookie consent as applicable).

Document every decision in the Decisions & Configuration Log section of References.md with the date.

## Step 2 — Sector-specific configuration

Follow the sector block in References.md Configuration Checklist:
- `[CONTENT/BLOG]`: initial content, SEO, RSS, comment moderation.
- `[COMMERCE]`: catalog, payments, tax, shipping, abandoned-cart.
- `[BOOKING]`: services, availability, confirmation/reminder emails, cancellation policy.
- `[HEALTHCARE]`: BAA signed + filed, intake forms, clinical documentation, retention policy, device hygiene, incident response.
- `[WORKFLOW]`: database/workspace structure, roles, forms, automations, reporting views.

Work through the checklist items. Mark each in `feature-tree.md` (using `templates/feature-tree-platform.md` Launch/Growth/Mature tiers) as configured as you go.

## Step 3 — Integrations

Each external integration (payment processor, email provider, analytics, CRM, etc.) is configured through the platform's admin:
- Document the integration in the Decisions log.
- Test the integration end-to-end (e.g., test transaction for payments, test email for marketing).
- Store API tokens securely in the platform's secret management, never in exported configs.

## Step 4 — Git + exportable config (optional)

Conventions: #2 (git), #16 (documentation).

If the platform exposes exportable config (theme files, custom code, automation definitions):
- Initialize a git repo for those files.
- Commit baseline config.
- Document the export/import workflow for that platform.

If the platform does not expose exportable config:
- Keep References.md, feature-tree.md, and VERSION-LOG.md under version control (they ARE the project documentation).
- Skip `git init` for anything else.

## Step 5 — Security hygiene

Conventions: #23 (app security), #24 (authorization).

Apply the Security and Roles sections of the References.md Configuration Checklist:
- 2FA on every admin.
- Session timeout and device-trust settings reviewed.
- Audit log enabled in platform if supported.
- Role definitions (owner / admin / staff / customer) configured with least privilege.
- PII export workflow documented (who can export, under what conditions).
- Incident response plan (who to contact if the platform is breached).

## Step 6 — Runbook

Conventions: #16 (documentation).

Write `docs/runbook.md` covering the common admin tasks a non-developer will need to perform. Examples by sector:
- **[COMMERCE]**: how to issue a refund, how to print a shipping label, how to edit a product.
- **[BOOKING]**: how to cancel an appointment, how to modify service availability.
- **[HEALTHCARE]**: how to update intake forms, how to export records for a patient request, how to respond to a BAA audit request.
- **[CONTENT/BLOG]**: how to publish a post, how to schedule, how to moderate comments.

## Step 7 — Smoke-test

Do one full end-to-end flow on the platform:
- **[COMMERCE]**: a test order placed, paid, fulfilled.
- **[BOOKING]**: a test appointment booked and confirmed.
- **[HEALTHCARE]**: a test patient invited, intake form completed, document shared, session note recorded.
- **[CONTENT/BLOG]**: a test post published and viewable on the custom domain.

Log the smoke-test date and outcome in References.md Decisions log.

## Post-scaffold output

- `References.md` with Configuration Log updated.
- `feature-tree.md` with Launch milestone items marked `configured` or `verified`.
- `docs/runbook.md` covering admin operations.
- `VERSION-LOG.md` with `Type: platform / {name}` scaffold entry.

## No validator

`scripts/validate-scaffold.sh` is code-oriented and does not apply. The scaffold "pass" criterion for platform projects is: every item in the sector-specific Configuration Checklist is marked `configured` or `verified` or explicitly `deferred` with reason.
