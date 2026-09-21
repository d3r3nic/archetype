# Bootstrap: reading the answers together

Part of the bootstrap playbook (bootstrap/ONBOARD.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step: read it when the script names it, with the reading it lists, and close it before opening the next.

## Step 2.7: Read the answers together
Read: bootstrap/RED-FLAGS.md § Red Flag Combinations; bootstrap/RED-FLAGS.md § Scope-Change Handler
Produces: the owner's knowledge level as read from the answers, the technical needs the answers translate into, and every red-flag combination found, said to the owner before any research
Check: evidence: the needs the answers translate into, and each red-flag combination found with what the owner said about it, or none found
Depends on: bootstrap.2.1; bootstrap.2.2; bootstrap.2.3; bootstrap.2.4; bootstrap.2.5; bootstrap.2.6

### How the AI decides (read the user's knowledge level):

The AI should gauge the user's technical experience from how they talk. Adjust choices accordingly:

**Non-technical user** (says things like "I don't know how apps work", "I heard AI can help"):
- Choose managed / BaaS services that require zero DevOps knowledge
- Database: a managed relational database with auth and file storage built in, or an embedded single-file database for simple single-user apps
- Hosting: a managed frontend platform + a managed backend/app platform
- Auth: a fully-managed drop-in auth provider
- Category shape is what matters; research current market leaders at bootstrap time. These ARE production-level tiers — they just don't require server management knowledge.

**Developer with some experience** (knows frameworks, doesn't know DevOps):
- Choose cloud platforms with simple deployment and managed databases
- Auth: a managed identity provider (consumer or B2B category depending on use case)
- Migratable to self-managed cloud later as needs grow
- Research current options at bootstrap time.

**Experienced developer / team with DevOps knowledge** (mentions a cloud provider, containers, infrastructure):
- Choose a major cloud provider with full control
- Database: managed database service on that cloud
- Auth: cloud-native managed auth or a compliance-certified managed auth broker
- Infrastructure as code (reproducible, auditable)
- CI/CD: automated pipeline to the cloud provider
- Full monitoring, logging, alerting

**Regulated data** (HIPAA, SOC2, PCI, GDPR, CCPA, financial regulations, sector-specific privacy laws):

FIRST: identify the regime. Different regimes require different controls, vendor agreements, and evidence. Research current requirements and vendor options for the specific regime at bootstrap time — do NOT rely on training-data-era recommendations.

SECOND: run Step 3 platform research. For most regulated domains, a compliance-ready vertical SaaS exists and clears the Step 3 coverage threshold without custom engineering. Platforms with signed BAA (HIPAA), subprocessor+attestation (SOC 2), or equivalent compliance artifacts for the regime are the first choice. Custom is the last resort for regulated data.

THIRD — only if custom is genuinely required (product logic no platform offers, scale exceeds platform tier, multi-system integration):
- Cloud provider with the right compliance certifications AND signed vendor agreement for the regime
- Database: managed, encrypted at rest and in transit
- Auth: compliance-certified managed auth (research current providers — enterprise auth categories include HIPAA-eligible managed auth, SAML-capable B2B auth brokers, enterprise identity providers)
- Infrastructure as code (reproducible, auditable)
- Audit trails, access controls, incident response — mandatory for every regime
- Budget reality: compliance-grade infrastructure has a meaningful monthly floor (varies by regime — HIPAA minimum differs from SOC 2 Type 2 minimum differs from PCI). Research current vendor pricing. If the user cannot absorb it, platform is the only correct answer — surface this explicitly, do not scaffold custom.

**Compliance regime details routed from bootstrap/RED-FLAGS.md when a specific regime is confirmed.**

### How to translate answers into technical decisions:

| Answer | Technical Decision |
|--------|-------------------|
| Web browser app | Frontend: a component-based web UI framework |
| Phone app (confirmed native) | Mobile: one cross-platform native framework, or each platform's own native toolchain |
| Phone app (PWA, installable from browser) | Web stack + PWA manifest + service worker |
| Works on phone (responsive web) | Web stack, responsive design, no mobile-specific tooling |
| Desktop app | Desktop: a web-stack desktop shell, or the OS's native UI toolkit |
| Users log in | Auth system needed |
| Users submit forms | Form system needed |
| Users upload files | File storage system needed |
| Real-time updates | WebSocket/SSE needed |
| Works offline | Offline support needed |
| Just me / personal | Simple stack, an embedded single-file database is fine, managed hosting |
| Startup MVP | Modern stack, managed relational database, cloud hosting |
| Enterprise / compliance | A major cloud provider, infrastructure as code, full monitoring |
| Millions of users | Performance, CDN, caching, horizontal scaling |
| No tech preferences | AI picks based on experience level (see above) |
| Has preferences | AI respects preferences AND still runs Step 3 research. If a platform covers the use case, or scale/compliance/cost is mismatched to the preference, surface the alternatives before agreeing. User can still choose their preference — but must see the tradeoff. |
| Sensitive data (health, finance) | Compliance-grade infrastructure, encryption, audit trails |
| No DevOps knowledge | Managed / BaaS services category (research current market leaders) |
| Knows cloud infrastructure | A major cloud provider with proper architecture (preferred for production) |

### Proven stack shapes (for each slot, research the current mainstream, actively maintained choice in the project's language — never pick from memory):

Web frontend: component UI framework + statically typed language + fast bundler + a styling system
Content sites / blogs / docs: a static-first site generator that ships little or no client JS
Backend API: typed server framework + a schema/ORM layer + a managed relational database
Mobile: one cross-platform native framework, or each platform's own native toolchain
Desktop: a web-stack desktop shell, or the OS's native UI toolkit

### Handling scope changes mid-discovery

If the user introduces a new requirement during discovery (multi-user after "just for me", SSO after "personal", mobile after "web", compliance after "nothing sensitive"), STOP the linear flow: acknowledge the change, re-ask affected groups, re-run Step 3 research. Full playbook + resistant-user handling in `bootstrap/RED-FLAGS.md` "Scope-Change Handler" section.

Do not proceed to Step 4 (file generation) until discovery is coherent with the current scope.

### Red flag combinations — surface before Step 3

Some requirement combinations are incompatible, anti-pattern, or signal hidden complexity. If the user's answers hit any, surface the conflict BEFORE moving to Step 3.

**Full 10-row table and per-row playbook in `bootstrap/RED-FLAGS.md`.** Categories covered:
- Free + regulated data (compliance floor makes this impossible)
- Offline + regulated data (device-loss compliance risk)
- Solo user + enterprise infra (scale mismatch — unless learning, see LEARNING-PROJECTS.md)
- Real-time + static hosting (infrastructure mismatch)
- Multi-user team + solo stack (feature/stack mismatch)
- "All equally important" + deadline (priority conflict)
- Enterprise SSO + consumer auth stack (provider mismatch)
- Compliance claim + no vendor-agreement discussion (user error)
- Enterprise SSO + user is not admin on the IdP tenant (provisioning dependency)
- Priority ranking refused (applies default order)

Multiple red flags = strong signal that platform Option A is correct. Do not proceed to Step 4 custom build when scale, compliance, or budget fundamentally don't fit a custom path.
