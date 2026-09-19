# Bootstrap: discovery, group 1

Part of the bootstrap playbook (bootstrap/ONBOARD.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step: read it when the script names it, with the reading it lists, and close it before opening the next.

## Step 2.1: Group 1 - What is it?
Read: bootstrap/ONBOARD-DISCOVERY.md; bootstrap/ONBOARD-EXAMPLES.md; bootstrap/RED-FLAGS.md § Discovery Turn Budget
Produces: what the product does and for whom, template or product, ship or learn, and the owner's answer to the one look question
Check: evidence: the owner's answers to this group in their own words, quoted; a question an earlier answer settled is recorded as inferred, with the inference; a question the owner declined is recorded as declined, with what was assumed

- What does your app do? Describe it like you're explaining to a friend.
- Who uses it? Just you? Your team? The public?
- Can you name an existing app that's similar to what you want? (even loosely)
- Is this a product you want to ship, or a project to learn a specific technology? (If learning a technology, that's a legitimate reason to use that stack even when a platform would be simpler — but note it explicitly so Step 3 can handle it correctly.)
- **Is this a TEMPLATE / starter kit / generator, or a PRODUCT / end deliverable?** A template is code that other projects FORK or INSTALL FROM — its audience is developers; it ships structural primitives, neutral defaults, and intentionally has no brand identity. A product is the end thing that real users interact with — it commits to a visual identity, a specific set of features, and a deployed URL. Same framework applies to both, but bootstrap generation diverges: templates defer brand/design-artifact decisions to downstream projects, ship `@scope/*` packages with placeholder tokens, and document the "downstream sites" model. Products complete those decisions at bootstrap, or prepare the directions and leave the pick open: the scaffold then builds neutral placeholder values, and no UI feature ships until the pick lands.
- **For a PRODUCT, one question about the look, asked once:** do you have ideas about how it should look, or should I choose what fits your business? Note anything the owner mentions in passing (a logo, the colors on a van, a site) and ask nothing more about the look during discovery: gathering what exists, the questions, and the direction belong to the design interview (`bootstrap/DESIGN-INTERVIEW.md`), which runs at Step 4, once the build approach and the operating stage are known, and never runs when Step 3 ends in a platform. The AI never invents the look on its own: the owner picks from shown directions or delegates the pick in words (#27, #29). Until then `Brand decided` in References.md § Design Artifact records `not yet, directions pending the owner's pick`, never a default look.

**Proactive learning-intent detection:** If the user's OPENING message declares enterprise or complex infrastructure (container orchestration, distributed caching, distributed message queues, service mesh, multi-region, microservices, self-managed clusters) for a personal-scale or small-scale project (one user, a blog, a single-person tool, a portfolio), ask the ship-vs-learn question in your FIRST reply, not after red flags fire in later turns. Pattern: solo + enterprise-infra is nearly always learning intent. Surface it early so the rest of discovery proceeds with the right frame.

**Template vs product — how generation diverges:** Discovery answer routes Step 4.

| Concern | TEMPLATE | PRODUCT |
|---|---|---|
| References.md § Project `Stage` | `template` plus the template's own version number | `development / staging / production` |
| References.md § Design Artifact | Every labelled line kept: `Brand decided: deferred to downstream projects`, `Direction of truth` and `Design working files` filled so a design tool run in the template has a recorded home, `none` where a line has nothing; the section's prose says downstream projects decide their own artifact at their own bootstrap and that the template ships neutral placeholder tokens, no visual identity invented. | AI researches the tool category, fills every labelled line of the section (direction of truth, sync, working-files folder, `Brand decided` from the design interview) per convention #27. |
| Design tools run in the project | Structure only: wireframes, layouts, states with neutral tokens; a request for brand values is deflected downstream. | Work from the artifact and the token source as the brief; the owner picks the direction from proposed directions (#27, #29). |
| References.md new § | `## Downstream Projects` — how sites FORK or INSTALL from this template, what's shared vs local, upgrade flow. | `## Deployment` (standard). |
| `@scope/*` packages | Built with neutral tokens (system colors, inherited typography). Convention #27 gate is about STRUCTURE, not VALUES. | Values come from design artifact per #27. |
| feature-tree.md Design-related rows (e.g. Components, Design System) | "Structural at template level; downstream projects apply brand." | Full-fidelity, artifact-driven. |
| VERSION-LOG.md bootstrap `Type:` | `Type: template` | `Type: product` |
| Discovery Groups 2–5 | Still asked — stack/scale answers shape the template's structural choices. | Still asked. |

This distinction is not the same as #22 Design System (which is always about component libraries) or #27 Design Foundation (always about the design-artifact discipline). It's orthogonal: a template or a product can still have both. Templates DEFER the artifact; products COMMIT it.
