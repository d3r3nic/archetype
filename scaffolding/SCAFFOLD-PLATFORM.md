# Scaffold — Platform Projects

Routed from `scaffolding/SCAFFOLD.md` when the project chose a platform (Option A from `bootstrap/ONBOARD.md` Step 3) rather than a custom build.

**Read `scaffolding/_preamble.md` first** — the shared scaffold rules still apply even when there's no code to scaffold, especially the handoff-check and red-flags rules.

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

Apply the Security and Roles sections of the References.md Configuration Checklist. Items tagged by priority:

- **[required]** 2FA on every admin account.
- **[required]** Role definitions (owner / admin / staff / customer) with least privilege.
- **[required]** PII export workflow documented (who can export, under what conditions).
- **[required]** Incident response plan (who to contact if the platform is breached).
- **[recommended]** Session timeout and device-trust settings reviewed.
- **[recommended]** Backup admin user configured (or explicitly deferred with revisit trigger if solo owner).
- **[if available]** Audit log enabled at the platform tier (if the chosen tier supports it; see tier-gap handling below).

**Tier-gap handling:** if the chosen plan/tier does NOT support a `[required]` or `[recommended]` item, do NOT silently skip. Log as explicitly deferred in `References.md § Decisions & Configuration Log`:
- What the gap is (e.g., "Shopify Basic does not include admin audit log — Plus tier only").
- Why the current tier was chosen anyway (cost, scale, etc.).
- Revisit trigger (e.g., "at first staff hire OR at 200+ orders/month, re-evaluate tier upgrade").
- Compensating control if any (e.g., "manual monthly export of order history as audit-trail substitute").

A gap logged with trigger + rationale is acceptable. A gap silently skipped is red flag #12 from scaffolding/RED-FLAGS.md.

## Step 6 — Runbook

Conventions: #16 (documentation).

Write `docs/runbook.md` covering the common admin tasks a non-developer will need to perform. **Use the sector-specific runbook template** where one exists:

- **[COMMERCE]**: `templates/runbook-commerce.md` — scaffolded template covering custom domain, products, orders + fulfillment, refunds, customers + CCPA/GDPR, newsletter, password reset, data exports, launch-day checklist, incident response, escalate-to-developer.
- **[BOOKING]**: no template yet — structure per Commerce pattern: service catalog, availability, appointment lifecycle, cancellations, reminder workflows, customer data.
- **[HEALTHCARE]**: no template yet — structure per Commerce pattern: patient onboarding, intake + consent, session notes, document sharing, BAA + compliance, record retention.
- **[CONTENT/BLOG]**: no template yet — structure per Commerce pattern: post lifecycle, SEO, comment moderation, theme customization, analytics.

**Required sections in every runbook (regardless of sector):**
- Each admin task: problem → numbered steps → verification → common gotchas.
- **"What I can't do from this runbook — escalate to developer"** section. Prevents the owner thrashing on problems they physically cannot solve without dev help (e.g., "platform is down site-wide" is NOT a runbook item — it's a Shopify Support ticket; "custom liquid theme changes" require a dev). Explicit escalation list.
- Launch-day checklist (matches Step 7 smoke-test script).
- Incident response (compromised login, fraudulent order, data breach notification).

## Step 7 — Smoke-test (agent produces script, owner executes)

**Subject-of-action clarification (Step 41):** the AI agent running this scaffold almost never has the ability to execute a smoke-test on the actual platform (requires live account, platform credentials, often a credit card). The agent's responsibility is to PRODUCE the script; the owner EXECUTES it live and logs results.

**Agent output:**
- A step-by-step smoke-test script inside `docs/runbook.md` (Launch-day checklist section) — sector-specific.
- **[COMMERCE]**: test order flow — add a cheap test product, place an order via test-mode payment (e.g., Shopify bogus gateway), verify confirmation email + order record, fulfill with test shipping, verify refund.
- **[BOOKING]**: test appointment — book a test service, verify confirmation email + reminder schedule, test cancellation flow.
- **[HEALTHCARE]**: test patient flow — invite a test patient (use a staff email), complete intake form, share a test document, record a session note, verify BAA is signed + audit log records the access.
- **[CONTENT/BLOG]**: test post — publish a draft, verify appearance on custom domain (DNS + SSL working), verify SEO metadata + social preview.

**Owner executes live.** Owner logs the smoke-test date, pass/fail per step, and any issues in `References.md § Decisions & Configuration Log`. Scaffold is NOT complete until the owner confirms at least Launch-milestone smoke-test items passed.

## Post-scaffold output

- `References.md` with Configuration Log updated.
- `feature-tree.md` with Launch milestone items marked `configured` or `verified`.
- `docs/runbook.md` covering admin operations.
- `VERSION-LOG.md` with `Type: platform / {name}` scaffold entry.

## No validator

`scripts/validate-scaffold.sh` is code-oriented and does not apply. The scaffold "pass" criterion for platform projects is: every item in the sector-specific Configuration Checklist is marked `configured` or `verified` or explicitly `deferred` with reason.
