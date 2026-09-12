# Creating forkable templates

When you build a template (a starting-point project that spawns customer sites), the spawn output must run end-to-end **without any post-fork patching**. This doc captures the discipline. It is stack-agnostic: whatever web framework, language, or build tool the template bundles, the rules are the same.

## The forkability bar

A template is forkable if and only if a fresh spawn passes its full verify chain (typecheck, lint, test, build, deploy) with **zero monkey-patches** between the copy and the verify step. The test:

```bash
1. Pack/build the template's distributable artifacts (packed archives, build output).
2. Copy the forkable directory verbatim to a new repo:
     cp -R templates/<id>/<forkable_path>/. /path/to/customer-repo
3. Refresh any vendored binaries from the pack output.
4. Rewrite per-customer slugs (package name, repo name) — only legitimate
   fork-time mutation.
5. Run the verify chain — must be green.
```

If step 5 needs ANY post-fork patching to pass, the template fails the bar. Fix at the source, not at fork time.

## The trap: workspace testbed ≠ forkable artifact

The most common failure mode: a template's "reference site" lives inside the template's monorepo as a workspace member, AND it gets used as the fork target. Workspace assumptions sneak into customer forks:

- Workspace-protocol dependencies that resolve to nothing outside the workspace
- Compiler or type config that extends a monorepo base absent from the fork
- No per-package lockfile (the workspace lockfile lives at the repo root)
- Pre-commit tooling and formatter config at the monorepo ROOT, not in the workspace member's own manifest
- CI scripts that run recursively across workspace packages when the customer fork is single-package
- Build scripts that reach into monorepo siblings through relative parent paths

Each of these surfaces as a patch the spawning tool (or fork operator) must apply at fork time. As the patch list grows past 2-3, the template has crossed into "broken by design" territory.

**Solution: split the two roles.**

| Role | Lives at | Workspace? | Lockfile? |
| --- | --- | --- | --- |
| **Testbed** — validates that the template's distributable packages compose | `apps/reference-<thing>/` (or equivalent) | Yes | Inherits monorepo root |
| **Forkable artifact** — what customer sites actually spawn from | `apps/<id>-customer-site/` (or equivalent) | **No** (negated in workspace globs) | **Own**, committed |

Both render the same UI; chrome differs. They stay in sync via a unidirectional sync script run during pack/build.

## What ships in the forkable artifact

Bake into the source — never synthesize at fork time:

- Own package manifest with **non-workspace** deps (local vendored archives, registry packages, or git refs)
- Own lockfile, committed
- Inlined config with no `extends` reaching a parent monorepo base (compiler, linter, formatter)
- Pre-commit tooling declared and wired in the fork's own manifest
- Formatter config + ignore rules already accounting for vendored binaries, generated files, and per-customer overrides
- CI workflow that's single-package and doesn't reference monorepo-only paths
- CD workflow with auth that survives a fork (federated identity, not copied long-lived keys)
- Container and deploy artifacts (build file, ignore files, deploy manifest) self-contained
- README explaining the spawn flow + acceptance criterion + the testbed/forkable split

## The sync mechanism

Edit UI in the testbed (where it composes against the workspace packages, gets full type-checking from the monorepo's deps, and runs in the dev server you already have). Sync to the forkable artifact:

```bash
# project-owned sync script, e.g. scripts/sync-customer-site.sh (or equivalent)
rsync -a --delete \
  --exclude='<dev-only-segments>' \
  apps/reference-<thing>/src/ apps/<id>-customer-site/src/
```

Wire the sync into the template's own pack/build script as its last step, so it runs every time you publish. Direction matters: testbed → forkable. Never the reverse. Never edit the forkable artifact's `src/` directly — it gets overwritten on the next sync.

## Manifest

Declare the forkable path in the template's manifest so the spawning tool knows what to copy:

```yaml
template:
  id: <id>
  source:
    type: local
    forkable_path: apps/<id>-customer-site
```

## Framework-specific guidance

The discipline above is stack-agnostic; only the file names change. Whatever framework the template bundles, check its forkable artifact for these:

- The framework config file stands alone — no shared parent config, no integrations declared outside it.
- The hosting target's build mode (self-contained output, adapter, or equivalent) is selected in that config, not inherited.
- Source and content directories the framework expects are mirrored into the fork, never symlinked out of it.
- Pre-commit, CI, lockfile, and compiler config do NOT reach upward into a monorepo.

- Dated example: a Next.js fork needs `output: 'standalone'` for container hosting such as Cloud Run, its security headers in `next.config.ts`, and no `extends` in its tsconfig; a SvelteKit fork needs a standalone `svelte.config.js` and a per-deploy-target adapter; an Astro fork needs its integrations declared per app.

## Common pitfalls (the patch list)

If you're maintaining an existing template and you find yourself patching forks at spawn time, each patch is a signal that something belongs in the source. The patch list one real spawn script accumulated before the discipline was applied:

1. Strip the recursive-workspace flag from the copied CI workflow
2. Strip framework-validation / snapshot CI steps that reference monorepo paths
3. Strip the frozen-lockfile flag from CI install (because no per-package lockfile shipped)
4. Add pre-commit tooling and formatter to the fork's dev dependencies + install hook
5. Strip dev-only scripts that reach into monorepo siblings
6. Skip copying the dependency-bot config (immediate noise on a fresh fork)
7. Skip framework symlinks (they don't survive a verbatim copy)
8. Synthesize a lockfile (the CI cache key requires one)
9. Append generated files to the formatter ignore list (lockfile, type defs, vendored archives, site config)
10. Inline the compiler config (the parent base doesn't exist in the fork)

Each is a "ship at source" signal. Use them as a checklist when designing your forkable artifact.

## Acceptance test you should run

Before declaring a template forkable, run this verbatim from a clean shell:

```bash
TEMPLATE_REPO=<your template repo>
TEMP=$(mktemp -d)

# 1. Clone (or symlink) the template
git clone --depth 1 "$TEMPLATE_REPO" "$TEMP/template"
cd "$TEMP/template"

# 2. Pack distributables — the template's own release step (project-owned)
bash <pack script>

# 3. Spawn a customer
cp -R apps/<forkable_path>/. "$TEMP/customer"
cd "$TEMP/customer"

# 4. Refresh vendored binaries (if your template uses vendoring)
mkdir -p vendor
cp "$TEMP/template/<pack output>/"* vendor/

# 5. Rewrite the per-customer slug only: the manifest's name field, nothing else
<set the manifest name field to the customer slug>

# 6. Plain workflow — no patches, no flags
<package-manager> install
<package-manager> typecheck
<package-manager> lint
<package-manager> test
<package-manager> build
```

If any of those fail, the template hasn't met the bar. Fix at the source. Re-run.

## When a template is mature, factor

Once several templates exist with shared shapes (welcome view, config getter, error boundaries, observability stub), stop copying and factor into a shared package (`@<scope>/<shared>`) consumed by all templates' forkable artifacts. Until then, copy is the discipline — the sync mechanism keeps it lockstep.

## References

- The template's own spawn contract, forkable path, vendoring layout, and patch history live in that template repo's docs — never in this playbook.
- The spawning tool's fork script belongs to the tool's repo. Every patch it carries is a bug report against the template: fix it at the source and delete the patch.
