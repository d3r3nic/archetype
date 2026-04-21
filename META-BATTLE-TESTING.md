# META — How this framework evolves

This doc explains the mechanism by which Archetype improves. It sits alongside `README.md` and `CLAUDE.md`; neither requires reading it, but anyone maintaining Archetype or building a template on it benefits.

## The four-layer stack

```
Factory (archetype-lab) → Framework (archetype) → Template → Product (customer site)
```

| Layer | Role | Repo / location |
|---|---|---|
| Factory | Where framework changes are authored; all history is narrative Steps in `planning/CHANGELOG.md` | `github.com/d3r3nic/archetype-lab` |
| Framework | What consumers use: 28 conventions, 4 phase playbooks (bootstrap/scaffold/develop/maintain), scripts, file templates | `github.com/d3r3nic/archetype` (published dist) |
| Template | A reusable project shape (e.g. `headless-wp-next`) — monorepo with `@scope/*` packages, reference app, governed by the framework | per-template repo |
| Product | A customer site spawned from a template | per-site repo |

## Updates flow downstream; findings flow upstream

Downstream (each consumer pulls):

- Framework → everyone via `archetype/update.sh` (read-only discipline: framework folder never receives project artifacts)
- Template packages → consumers via the chosen package manager's upgrade command for `@scope/<pkg>` (SemVer contract; patch/minor safe, major ships a codemod)

Upstream — **every discovery by a downstream layer lands in the factory as a numbered Step**. Battle-test findings never stay at the discovering layer. Examples (factory Steps 44–49 and beyond):

| Step | Triggered by | Finding | Landed where |
|---|---|---|---|
| 44 | Template bootstrap | `dist/templates/feature-tree.md` columns didn't match `pulse-inspect.sh` parse | Templates + script + validator group 7 |
| 45 | Template restructure | `inject.sh` / `update.sh` wrote project artifacts inside the framework folder | `dist/inject.sh`, `dist/update.sh`, validator group 8 |
| 46 | Template needed a design-discipline convention | No convention governed the "design artifact as source of truth" rule | New convention #27 Design Foundation |
| 47 | Step 46 left a pipeline leak | `references-*.md` templates didn't have the Design Artifact section | Templates + validator |
| 48 | Template is a monorepo | `pulse-inspect.sh` scanned only `src/*`, not `apps/*/src/*` | Script extended with monorepo scan |
| 49 | Template wasn't a product | Framework conflated template-shape with product-shape in bootstrap | `bootstrap/ONBOARD.md` Group 1 gained the distinction |

Everything in the framework's current state was either originally authored here OR promoted up from a real use.

## What belongs upstream vs what stays local

Belongs in the framework:

- Conventions (character, principles, signals)
- Phase playbooks (the how-to per shape)
- Scripts (pulse-inspect, validators, inject, update)
- File templates (References.md, feature-tree.md, references-*.md)
- Red flags + steering guidance

Stays local at the product layer:

- Specific brand tokens (colors, typography values)
- Specific vendor choices (Sentry DSN, Stripe keys, WP URL)
- UI/UX decisions tied to the product's brand — these live in the product's Design Artifact per convention #27, never in the framework

Stays local at the template layer:

- The specific stack the template bundles — other templates pick other stacks
- The package structure it settles on (scope name, package split) — other templates split differently
- Features built for its audience — other templates ship other features

The test: if rolling back a specific choice would leave the framework's DIRECTION unchanged, the choice was local. If the framework would no longer know what to do, the rule was a framework concern and should be promoted.

## End-of-session checklist for framework maintainers

After any working session that involves a downstream project:

- [ ] Audit: what patterns / rules / lint recipes / tooling gotchas were applied locally?
- [ ] Classify each: framework-level (convention, playbook, script, template) vs local (brand, vendor, feature).
- [ ] Framework-level findings → file a numbered Step in factory CHANGELOG.md with (trigger, finding, fix) tuple.
- [ ] Fix in `dist/` at the right layer (convention vs script vs template vs playbook).
- [ ] Push factory, push framework, pull into active projects.
- [ ] Confirm the finding is no longer local: fresh AI could rebuild from framework alone.

Promotion debt is the worst kind of framework debt — by the time it's discovered, the context that surfaced it is gone.

## For AI agents reading this

If you are developing a template or product project on top of Archetype and you discover something that would benefit future projects — **stop, promote it to the factory first**, then return to your local work. The factory-first rule (see outer CLAUDE.md in archetype-lab) is not a preference; it is how the framework stays coherent across many consumers.
