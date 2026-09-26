# META — How this framework evolves

This doc explains the mechanism by which Archetype improves. It sits alongside `README.md` and `CLAUDE.md`; neither requires reading it, but anyone maintaining Archetype or building a template on it benefits.

## The four-layer stack

```
Factory (archetype-lab) → Framework (archetype) → Template → Product (customer site)
```

| Layer | Role | Repo / location |
|---|---|---|
| Factory | Where framework changes are authored; all history is narrative numbered steps in `planning/CHANGELOG.md` | the maintainers' private repository |
| Framework | What consumers use: the convention catalogue, the phase playbooks (bootstrap/scaffold/develop/maintain), scripts, file templates | `d3r3nic/archetype` (published dist) |
| Template | A reusable project shape — monorepo with `@scope/*` packages, a reference app, governed by the framework | per-template repo |
| Product | A customer site spawned from a template | per-site repo |

## Updates flow downstream; findings flow upstream

Downstream (each consumer pulls):

- Framework → everyone via `archetype/update.sh` (read-only discipline: framework folder never receives project artifacts)
- Template packages → consumers via the chosen package manager's upgrade command for `@scope/<pkg>` (SemVer contract; patch/minor safe, major ships a codemod)

Upstream — **every discovery by a downstream layer lands in the factory as a numbered step carrying its (trigger, finding, fix) tuple**. Battle-test findings never stay at the discovering layer. The recurring shapes, each taken from a real battle-test:

| Triggered by | Finding | Landed where |
|---|---|---|
| Template bootstrap | A shipped file template's columns didn't match what `pulse-inspect.sh` parses | Templates + script + a validator group |
| Template restructure | `inject.sh` / `update.sh` wrote project artifacts inside the framework folder | `inject.sh`, `update.sh`, a validator group |
| Template needed a design-discipline convention | No convention governed the "design artifact as source of truth" rule | New convention #27 Design Foundation |
| An earlier convention left a pipeline leak | The `references-*.md` templates had no Design Artifact section | Templates + validator |
| Template is a monorepo | `pulse-inspect.sh` scanned one source root, not a monorepo's app roots | Script extended with a monorepo scan |
| Template wasn't a product | Framework conflated template-shape with product-shape at bootstrap | `bootstrap/ONBOARD.md` Group 1 gained the distinction |

The shape repeats: a downstream layer hits a gap, the gap is classified, the fix lands at the layer that owns it (convention, playbook, script, or template), and the factory step records the tuple so the next consumer inherits the fix instead of rediscovering it. Everything in the framework's current state was either originally authored here OR promoted up from a real use.

Findings flow both ways. A finding can add guidance, and it can equally remove, soften, merge or scope guidance that got in the way: a step that did not fit how an application works, a check that failed on how something was written, a rule that gave one answer for every project. Those reports matter as much as gaps, because guidance that is noise costs every project that reads it.

## What belongs upstream vs what stays local

Belongs in the framework:

- Conventions (character, principles, signals)
- Phase playbooks (the how-to per shape)
- Scripts (pulse-inspect, validators, inject, update)
- File templates (References.md, feature-tree.md, references-*.md)
- Red flags + steering guidance

Stays local at the product layer:

- Specific brand tokens (colors, typography values)
- Specific vendor choices (error-tracking DSN, payment keys, CMS endpoint)
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

If you are developing a template or product project on top of Archetype and you find something that would benefit future projects, or guidance that got in the way, report it upstream (development/FEEDBACK.md) with the owner's approval, then return to your local work. Findings that reach the framework are how it stays coherent across many projects.
