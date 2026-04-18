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

**Platform build, not custom.** The Archetype framework's scaffolding phase does NOT apply. The following conventions still apply to this project: #2 (Git) for version-controlled config, #16 (Documentation) — this file is the primary documentation artifact, #23 (App Security) for admin accounts and PII handling within the platform, #24 (Authorization) for role management within the platform. All other conventions are owned by the platform itself.

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

Platform-agnostic categories. Fill in items that apply; skip or delete items that don't.

### Account & Domain
- [ ] Account created with owner email
- [ ] 2FA enabled on owner account
- [ ] Custom domain connected and verified
- [ ] SSL / HTTPS enforced
- [ ] Backup admin user configured (if platform supports, in case owner loses access)

### Catalog / Content
- [ ] Initial products / posts / listings created
- [ ] Images uploaded and optimized
- [ ] Categories / tags / collections structured
- [ ] SEO fields filled (meta title, description, alt text)

### Commerce (if applicable)
- [ ] Payment provider connected
- [ ] Tax settings configured for jurisdictions
- [ ] Shipping rates / zones defined
- [ ] Refund / return policy published
- [ ] Test transaction processed end-to-end

### Integrations
- [ ] Analytics connected (Google Analytics, Plausible, platform-native)
- [ ] Email / newsletter connected
- [ ] Customer support connected (if applicable)
- [ ] Webhooks / API tokens stored securely (if used)

### Legal
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] Cookie consent (if applicable, especially EU/CA)
- [ ] Refund / return policy published
- [ ] Compliance-specific docs (BAA, DPA, SOC2 attestation) obtained and filed

### Theme / Branding
- [ ] Theme selected and customized
- [ ] Logo uploaded
- [ ] Brand colors / fonts applied
- [ ] Mobile preview checked

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
