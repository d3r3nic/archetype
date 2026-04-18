# Red Flags and Decision Gates

Reference tables and gate patterns pulled out of `ONBOARD.md` so discovery stays linear while depth lives here. Routed from `ONBOARD.md` Step 2 and Step 3. Read the relevant sections when a red flag fires; do not read top-to-bottom.

## Red Flag Combinations

Surface before moving to Step 3. If any combination fires, do NOT silently proceed. Each row includes the pattern, why it's a red flag, and what to do.

| Combination | Why it's a red flag | What to do |
|-------------|---------------------|------------|
| Free to run + regulated data (HIPAA, PCI, financial) | Compliance-grade hosting has a meaningful monthly floor. BAAs, compliant storage, encryption, audit logging — none ship on free tiers. | Step 3 Option A is the only correct answer. Recommend the cheapest compliant platform for the regime. Custom for $0 is not possible. |
| Offline + regulated data (PHI, PII, financial) | Offline means data on the device. Device loss, encryption failure, sync integrity, remote wipe — all compliance risks. | Challenge the requirement. Ask: "Do you need truly offline, or fast access while online?" Offline with regulated data is a significant compliance burden. |
| Solo user + enterprise infra (Kubernetes, multi-region, service mesh, Kafka) | Operational burden exceeds feature work. User bounces off the infra before shipping the product — UNLESS this is a learning project (see LEARNING-PROJECTS.md). | First, ask ship-vs-learn (see LEARNING-PROJECTS.md). If shipping, surface the scale mismatch and quantify complexity cost (hours of ops/week). Offer a simpler stack. |
| Real-time + static hosting | Real-time (WebSocket, SSE) needs a long-lived server. Static hosts cannot. | Add a managed real-time service OR a stateful backend. Confirm the cost addition. |
| Multi-user team + "just me" stack (SQLite-only, no auth, local files) | Team features need auth, shared persistence, concurrency. Solo stacks cannot handle this. | Re-run discovery Groups 3 and 4; escalate the stack. |
| "All equally important" priorities + tight deadline | If everything is top priority, nothing is. Deadlines force tradeoffs. | Force a ranking. See "Priority-ranking fallback" below. |
| Enterprise SSO (Okta, Azure AD, Google Workspace) + consumer auth stack | Enterprise SSO usually needs a SAML/SCIM-capable managed auth provider — not consumer auth. | Route to enterprise-auth research. See "SSO tenant ownership check" below. |
| Compliance claim + no BAA / vendor-agreement discussion | Claiming a compliance regime without vendor agreements is a common user error. | Ask about BAA/subprocessor plans. Route to compliance-aware platforms or enterprise cloud paths. |
| Enterprise SSO mentioned + user is not an admin on the IdP tenant | Provisioning (SAML metadata, SCIM, conditional access) requires admin access to the identity provider. | Ask: "Are you an admin on that tenant, or will IT provision?" If not admin, scaffold a fallback (consumer auth with SAML-ready adapter) until IT engages. |
| "All equally important" + user refuses to rank | Proceeding without a ranking means AI guesses and may optimize the wrong axis. | Apply default order: (1) compliance and legal safety, (2) data integrity and authentication, (3) core user flow, (4) scale, (5) polish and nice-to-haves. Document the applied order in References.md under "Convention Overrides" so the user can redirect later. |

Multiple red flags = strong signal for platform Option A.

## Vague-Answer Rules

### Vague sensitive-data answer → assume regulated

If the user answers the sensitive-data question vaguely ("I dunno", "not sure", "I guess not"), DEFAULT TO ASSUMING REGULATED DATA. Ask one disambiguating question:

> "To be safe, I'll assume yes — are any of these involved: health info (doctor notes, therapy, wellness tracking with medical intent)? payments (credit card numbers you store)? identity info (SSN, driver's license, passport)? employment/HR data? minors' data? If none of these apply and the data is not governed by any specific law you're aware of, say 'no regulated data.' Otherwise I'll route you toward a compliance-aware stack."

The safe default is yes-regulated. A wrong "no" here leads to a non-compliant stack the user won't catch until audit. A wrong "yes" leads to overkill but safe.

### Vague budget answer

Parallels vague-regulated:
- If regulated-data is YES (confirmed or default-assumed), surface the minimum monthly compliance floor — research current vendor quotes for the specific regime before committing. If user cannot absorb it, platform Option A is the only correct answer.
- If regulated-data is NO, assume $0 budget. Flag any non-free component (paid hosting tier, paid auth provider, paid monitoring) before committing. Get affirmative consent per component.

### Vague stack preference ("use whatever", "I don't care")

Not a choice — a deflection. Do not invent Option C with a random stack. Apply Step 3 default: if a platform covers 80%+ of the use case, recommend it. If not, offer a minimum-viable custom stack for the scope and name it as the default pending user objection.

## Deploy Gate — unresolved regulated-data question

If the regulated-data question is in "default-assumed yes, not explicitly answered" state at the end of bootstrap:
1. Record it in `VERSION-LOG.md` as an open pre-production gate.
2. Scaffolding and deploy steps (Phase 2 onward) must halt until the user affirmatively answers with either "yes, it is regulated — here's the regime" or "no, it is not regulated."
3. Deflections ("go with defaults", "whatever you recommend") do NOT resolve this gate. The user must pick.

## Mobile Disambiguation

If the user says "phone app" or "works on my phone," do NOT silently pick a stack. Follow up:

> "When you say phone, do you mean: (a) installed from the App Store / Play Store like Instagram (a native app), (b) added to the home screen from a browser like a PWA, or (c) just works well when they open your site on their phone (responsive web)? The three are very different in cost and time to build."

These three are genuinely distinct decisions — do NOT merge them:
- **Responsive web (c)** — site works on phone browsers. No install. Cheapest and fastest. The default for "I don't know."
- **PWA (b)** — responsive web PLUS an installable home-screen icon via manifest + service worker. Adds offline caching and push notifications. More work than (c), meaningfully less than (a).
- **Native (a)** — native modules, App Store presence, native device APIs (HealthKit, haptics, biometrics), different deployment. Most work.

If the user says "I don't know what that means" or deflects, pick responsive (c). Do NOT silently pick native or bundle PWA on top by default.

## Scope-Change Handler

If the user introduces a new requirement during discovery (multi-user after "just for me", SSO after "personal project", mobile after "web only", compliance after "nothing sensitive"), STOP the linear flow and:

1. **Acknowledge the change explicitly.** "That changes things — multi-user means we need auth, permissions, and a shared data model."
2. **Re-ask the affected discovery groups.** Group 3 (users/auth/forms) if user count changed. Group 4 (scale) if scope or audience grew. Group 5 (sensitive data) if the data model changed.
3. **Re-run Step 3 research.** The previous platform/stack recommendation is invalid.
4. **If the user resists re-interviewing** ("I told you already"): explain why — the earlier answer was for a different scope.

Do not proceed to Step 4 (file generation) until discovery is coherent with the current scope.

## Discovery Turn Budget

If you have re-asked the same core question 3 times and the user keeps deflecting, default to the most-likely interpretation, LOG the assumption in VERSION-LOG as an open pre-production gate, and move on. Infinite re-asking loops waste the user's attention. The gate ensures the assumption is surfaced before it causes real damage.
