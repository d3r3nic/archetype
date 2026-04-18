# Feature Tree — Platform Project

Use this template when the project is built on a third-party platform (Shopify, WordPress, SimplePractice, Blueprint, Squarespace, Notion, Airtable, etc.). For custom builds, use `feature-tree.md` instead.

A platform feature-tree is a **configuration and rollout checklist**, not a systems map. There are no foundational systems to build — the platform owns them. The tree tracks what configuration has been set up and what milestones are still ahead.

---

## Platform

- Name:
- Plan / tier:
- Deployed at:
- Owner:

## Launch milestone

Everything required before the project is live and usable by its intended audience.

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Platform account created | not started | | |
| 2FA enabled on owner account | not started | | |
| Custom domain connected | not started | | |
| SSL / HTTPS enforced | not started | | |
| Initial catalog / content loaded | not started | | |
| Payment or checkout flow tested end-to-end (if applicable) | not started | | |
| Legal pages published (privacy, terms, refund, compliance) | not started | | |
| Analytics connected | not started | | |
| Test user or test purchase verified | not started | | |

## Growth milestone

Items that make the project sustainable as usage ramps up. Not required for launch.

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Newsletter / email integration | not started | | |
| Customer / user support channel | not started | | |
| Abandoned-cart or retention workflow (if commerce) | not started | | |
| SEO and metadata polish | not started | | |
| Automated backup or export workflow | not started | | |
| Secondary admin user (backup access) | not started | | |

## Mature milestone

Items that only become relevant at scale or after the first growth phase. May never apply.

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Advanced analytics / funnel tracking | not started | | |
| A/B testing or experimentation | not started | | |
| Multi-region or internationalization | not started | | |
| Custom integrations via platform APIs | not started | | |
| Migration to next tier (higher plan, or platform switch) | not started | | |

## Deferred / Open Questions

Items the user chose to defer or hasn't decided on. Revisit during maintenance phases.

-

## Status legend

- `not started` — no action yet
- `in progress` — actively configuring
- `planned` — documented by the scaffold agent, awaiting owner's live execution (platform projects need this — agent can document but not execute)
- `configured` — set up and working
- `verified` — tested end-to-end
- `deferred` — explicit decision to skip with reason in References.md Decisions log
- `N/A` — does not apply to this project

---

## Notes for AI agents reading this file

- This project is a platform build, NOT a custom build. Do NOT scaffold foundational systems.
- Applicable conventions (see `References.md` Applicable Conventions section): #2 Git, #16 Documentation, #23 App Security, #24 Authorization. All others are owned by the platform.
- If a user asks for features that require custom code beyond platform extension APIs, consider whether they've outgrown the platform — see `References.md` "How to Leave the Platform Later" for the migration trigger criteria.
