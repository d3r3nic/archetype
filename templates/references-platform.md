# References — Platform Project

Use this template when the user's project is built on a third-party platform (Shopify, WordPress, SimplePractice, Blueprint, Squarespace, Notion, Airtable, etc.) instead of custom code. If the user is building custom, use `references-frontend.md`, `references-backend.md`, or `references-mobile.md` instead.

---

## Project

- Name:
- Purpose (one sentence):
- Stage: [idea / building / live / maintaining]
- Public URL (if any):
- Owner (who holds the account):

## Build Approach

**Platform build, not custom.** The Archetype framework's scaffolding phase does NOT apply. See the "Applicable Conventions" and "Out-of-Scope Systems" sections below for details on which framework rules still matter here.

**Git note:** Platform projects often don't need a full repo for code. You may still want to version-control this `References.md` file and any exported config or theme files (e.g., `shopify theme pull`, WordPress child-theme files). Use your judgment — git is optional for platform projects, but useful if config drift is a concern.

## Platform

- Name:
- Plan / tier:
- Admin URL:
- Storefront / customer-facing URL (if different):
- Billing account:
- Billing cadence:
- Apps / extensions enabled: [list]

## Why This Platform

Rationale tied to discovery answers (scale, compliance, budget, team, existing systems). Answer these:
- What does the platform solve out of the box that a custom build would need to recreate?
- What does the platform NOT do that the user needs? (If this list is long, re-evaluate the platform choice.)
- Scale fit: platform covers the user's current and ~2-year projected scale?
- Cost fit: monthly cost acceptable at current and projected usage?
- Compliance fit: if regulated data, does the platform sign a BAA / have the right certifications?

**Pricing note:** Verify current pricing on the vendor's official site before the user signs up. Pricing quoted in this file or in the framework is a reference point only — tiers, trial periods, and add-on costs change. Include the date of your pricing check here.

## Decisions & Configuration Log

Dated entries, append-only. Example format:

```
2026-04-17 — Chose Shopify Basic plan over Squarespace Commerce.
Reason: Etsy migration, catalog >50 items, needed lower transaction fees. Reevaluate at 500 orders/month.
```

```
2026-04-20 — Enabled Shopify Email app, disabled Shop Pay Installments.
Reason: newsletter was the Turn-2 requirement. Installments don't fit a $15 product.
```

## Configuration Checklist

Structure: five baseline sections apply to every platform. Sector-specific sections are labeled `[CONTENT/BLOG]`, `[COMMERCE]`, `[BOOKING]`, `[HEALTHCARE]`, `[WORKFLOW]` — use only the one(s) that match the project. Delete unused sector blocks from the generated References.md so future readers aren't confused.

### Baseline: Account
- [ ] Account created with owner email
- [ ] 2FA enabled on owner account
- [ ] Backup admin user configured (skip if single-owner at launch; revisit at growth)
- [ ] Password manager entry created for shared credentials

### Baseline: Domain & SSL
- [ ] Custom domain purchased / connected
- [ ] DNS records verified
- [ ] SSL / HTTPS enforced (platform usually auto-provisions)
- [ ] Email/subdomain routing configured if needed

### Baseline: Legal
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] Cookie consent (if applicable — EU/CA users, analytics, tracking)

### Baseline: Security
- [ ] 2FA on all admin accounts
- [ ] Session timeout and device-trust settings reviewed
- [ ] Audit log enabled if platform supports
- [ ] Export/backup policy documented (who exports customer data, how often)
- [ ] Incident response plan: who to contact if the platform is breached

### Baseline: Documentation
- [ ] This `References.md` kept current (update the Decisions log per change)
- [ ] Runbook for common admin tasks (refunds, password resets, user provisioning)
- [ ] Handoff doc for successor admin (if solo owner)

---

### [CONTENT/BLOG] — use for blogs, documentation sites, content hubs
- [ ] Initial posts / pages created
- [ ] Images uploaded and optimized
- [ ] Categories / tags structured
- [ ] SEO fields filled (meta title, description, social preview, canonical URLs)
- [ ] RSS / sitemap generated and verified
- [ ] Comment moderation policy set (if comments enabled)

### [COMMERCE] — use for online stores (Shopify, WooCommerce, Square, etc.)
- [ ] Product catalog entered
- [ ] Payment provider connected and test transaction processed
- [ ] Tax settings configured for jurisdictions
- [ ] Shipping rates / zones defined
- [ ] Refund / return policy published
- [ ] Abandoned-cart email flow configured (defer if low volume)
- [ ] Analytics and attribution (GA4, platform-native, Meta pixel if applicable)

### [BOOKING] — use for appointment / scheduling platforms (Calendly, Acuity, Square Appointments, etc.)
- [ ] Services / session types defined with duration and price
- [ ] Availability calendar set up with buffer times
- [ ] Confirmation and reminder email templates customized
- [ ] Cancellation / rescheduling policy configured
- [ ] Payment capture timing (at booking vs at session) decided
- [ ] Intake form / pre-appointment questions configured

### [HEALTHCARE] — use for HIPAA-regulated practice management (SimplePractice, Jane, TherapyNotes, Healthie, etc.)
- [ ] BAA signed with platform vendor (file a copy)
- [ ] Intake and consent forms configured (HIPAA notice of privacy practices, informed consent)
- [ ] Clinical documentation templates set up (session notes, treatment plans)
- [ ] Patient portal access tested with a fake patient account
- [ ] Telehealth integration tested (if in scope)
- [ ] Record retention policy documented (state-specific — e.g., California CMIA requires 7 years for adults, 7 years past age of majority for minors)
- [ ] Workflow for migrating paper records (if applicable)
- [ ] Device-hygiene checklist for staff (encrypted laptops, no PHI on personal devices, remote wipe enabled)
- [ ] Incident response plan (breach notification timelines: HIPAA 60 days, state laws may be shorter)

### [WORKFLOW] — use for internal-tool platforms (Notion, Airtable, Retool, Monday, etc.)
- [ ] Database / base / workspace structure designed
- [ ] User roles and permissions configured
- [ ] Input forms for non-admin users
- [ ] Automation rules (notifications, status transitions)
- [ ] Reporting / dashboard views for stakeholders
- [ ] Export / integration with upstream or downstream systems

## Applicable Conventions (and how they apply)

- **#2 Git** — If you version-control platform theme customizations, export files, or config-as-code (e.g., Shopify theme folder, WordPress child theme), commit them here. Otherwise this convention is minimal for platform projects.
- **#16 Documentation** — This file (References.md) is your primary documentation. Keep the Decisions & Configuration Log current. One commit per meaningful config change, referencing the log entry.
- **#23 App Security** — Admin account hygiene (strong password, 2FA, limited admin users), PII handling (what customer data the platform collects and who can access it), audit logs (enable if the platform supports), export policies (who can export customer data), incident response (who to contact if the platform is breached).
- **#24 Authorization** — Role definitions within the platform (owner / admin / staff / customer). Least privilege. Audit trail on role changes.

## Out-of-Scope Systems

These framework conventions do NOT apply to this project because the platform owns them:

- #3 Architecture — platform's concern
- #4 Components — platform's concern
- #5 State management — platform's concern
- #6 Styling (beyond theme customization) — platform's concern
- #7 Types, #8 Errors, #9 API, #10 Contract — platform's concern
- #11 Authentication — platform's concern
- #12 Testing, #13 Performance, #14 Accessibility, #15 Build/CI — platform's concern
- #17-#22, #25 — platform's concern

If a future AI agent opens this project and suggests scaffolding any of the above, they should stop and re-read this file first. This is a platform project.

## Convention Overrides

Project-specific deviations or additions. Start empty; add entries as they emerge. Example:

```
#23 — This platform stores customer addresses by default. We will NOT store
credit card numbers in platform fields; all card data stays with Stripe.
```

## Open Questions / Deferred Decisions

List of things the user has not yet decided. Revisit during maintenance.

- Q: Should we add abandoned-cart emails? (revisit at 50 orders/month)
- Q: Custom checkout vs default? (revisit if conversion < 2%)

## How to Leave the Platform Later

If the user outgrows this platform and wants to migrate to custom:
- Re-run bootstrap from `bootstrap/ONBOARD.md` with current scope
- Use the appropriate custom-build template (references-frontend/backend/mobile)
- This file becomes the specification of what the custom build must replicate
- Export all platform data before decommissioning
