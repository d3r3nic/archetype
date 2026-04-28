# Creating forkable templates

When you build a template (a starting-point project that spawns customer sites), the spawn output must run end-to-end **without any post-fork patching**. This doc captures the discipline. Framework-agnostic: Next.js / Astro / SvelteKit / Remix / anything else — the rules are the same.

## The forkability bar

A template is forkable if and only if a fresh spawn passes its full verify chain (typecheck, lint, test, build, deploy) with **zero monkey-patches** between the rsync and the verify step. The test:

```bash
1. Pack/build the template's distributable artifacts (e.g. tarballs, dist/).
2. Copy the forkable directory verbatim to a new repo:
     cp -R templates/<id>/<forkable_path>/. /path/to/customer-repo
3. Refresh any vendored binaries (e.g. tarballs from dist/).
4. Rewrite per-customer slugs (package name, repo name) — only legitimate
   fork-time mutation.
5. Run the verify chain — must be green.
```

If step 5 needs ANY post-fork patching to pass, the template fails the bar. Fix at the source, not at fork time.

## The trap: workspace testbed ≠ forkable artifact

The most common failure mode: a template's "reference site" lives inside the template's monorepo as a workspace member, AND it gets used as the fork target. Workspace assumptions sneak into customer forks:

- `workspace:*` deps that don't exist outside the workspace
- `tsconfig.json` extending a monorepo base that's not in the fork
- No per-package lockfile (workspace lockfile lives at root)
- Husky / Prettier / ESLint configured at the monorepo ROOT, not in the workspace member's package.json
- CI scripts using `pnpm -r` (recursive) when the customer fork is single-package
- Build scripts using `cd ../..` to reach monorepo siblings

Each of these surfaces as a patch the dashboard (or fork operator) must apply at fork time. As the patch list grows past 2-3, the template has crossed into "broken by design" territory.

**Solution: split the two roles.**

| Role | Lives at | Workspace? | Lockfile? |
| --- | --- | --- | --- |
| **Testbed** — validates that the template's distributable packages compose | `apps/reference-<thing>/` (or equivalent) | Yes | Inherits monorepo root |
| **Forkable artifact** — what customer sites actually spawn from | `apps/<id>-customer-site/` (or equivalent) | **No** (negated in workspace globs) | **Own**, committed |

Both render the same UI; chrome differs. They stay in sync via a unidirectional sync script run during pack/build.

## What ships in the forkable artifact

Bake into the source — never synthesize at fork time:

- Own `package.json` with **non-workspace** deps (e.g. `file:./vendor/*.tgz`, real npm packages, or git refs)
- Own lockfile, committed (`pnpm-lock.yaml` / `package-lock.json` / `yarn.lock` / etc.)
- Inlined config (no `extends` to a parent monorepo base): tsconfig, eslint, etc.
- Pre-commit tooling (husky / lint-staged / pre-commit / lefthook) wired locally
- Formatter config + ignore rules already accounting for vendored binaries, generated files, and per-customer overrides
- CI workflow that's single-package and doesn't reference monorepo-only paths
- CD workflow with auth that survives a fork (Workload Identity Federation > stored keys)
- Docker / deploy artifacts (Dockerfile, .dockerignore, .gcloudignore, etc.) self-contained
- README explaining the spawn flow + acceptance criterion + the testbed/forkable split

## The sync mechanism

Edit UI in the testbed (where it composes against the workspace packages, gets full type-checking from monorepo's deps, and runs in the dev server you already have). Sync to the forkable artifact:

```bash
# scripts/sync-customer-site.sh (or equivalent)
rsync -a --delete \
  --exclude='<dev-only-segments>' \
  apps/reference-<thing>/src/ apps/<id>-customer-site/src/
```

Wire this into the pack/build script so it runs every time you publish:

```bash
# scripts/pack-local.sh (or equivalent) — last step
bash scripts/sync-customer-site.sh
```

Direction matters: testbed → forkable. Never the reverse. Never edit the forkable artifact's `src/` directly — gets overwritten on the next sync.

## Manifest

Declare the forkable path in the template's manifest so the dashboard / spawning tool knows what to copy:

```yaml
template:
  id: <id>
  source:
    type: local
    forkable_path: apps/<id>-customer-site
```

## Framework-specific guidance

The discipline above is framework-agnostic. Specifics vary:

| Framework | Forkable-path artifact concerns |
| --- | --- |
| **Next.js** | `output: 'standalone'` if deploying to Cloud Run / serverless; `next.config.ts` with security headers; `app/` or `pages/` mirror; no `extends` in tsconfig |
| **Astro** | `astro.config.mjs` standalone; integrations declared per-app; content collections under `src/content/` mirrored |
| **SvelteKit** | `svelte.config.js` standalone (no parent `vite.config.js` shared); adapter chosen per-deploy target; `src/lib/` mirrored |
| **Remix / React Router** | `vite.config.ts` standalone; route conventions same in fork; build output specific to the deploy target |
| **Anything** | Pre-commit + CI + lockfile + tsconfig must NOT reach upward into a monorepo |

## Common pitfalls (the patch list)

If you're maintaining an existing template and you find yourself patching forks at spawn time, each patch is a signal that something belongs in the source. The 10 patches the makemyweb dashboard's `fork-template.sh` accumulated before the discipline was applied:

1. Strip `pnpm -r` (recursive) flag from copied CI workflow
2. Strip framework-validation / pulse-snapshot CI steps that reference monorepo paths
3. Strip `--frozen-lockfile` from CI install (because no per-package lockfile shipped)
4. Add husky / lint-staged / formatter to customer's devDeps + `prepare` script
5. Strip pulse-generate / dev-only scripts that reference `cd ../..`
6. Skip copying `dependabot.yml` (immediate noise on fork)
7. Skip framework symlinks (don't survive `cp -R`)
8. Synthesize lockfile (CI cache key requires one)
9. Append generated files to formatter ignore (lockfile, type defs, vendor, site-config)
10. Inline `tsconfig.json` (parent base doesn't exist in fork)

Each is a "ship at source" signal. Use them as a checklist when designing your forkable artifact.

## Acceptance test you should run

Before declaring a template forkable, run this verbatim from a clean shell:

```bash
TEMPLATE_REPO=<your template repo>
TEMP=$(mktemp -d)

# 1. Clone (or symlink) the template
git clone --depth 1 "$TEMPLATE_REPO" "$TEMP/template"
cd "$TEMP/template"

# 2. Pack distributables (or whatever your template's "release" step is)
bash scripts/pack-local.sh   # or `pnpm build`, `npm run release`, etc.

# 3. Spawn a customer
cp -R apps/<forkable_path>/. "$TEMP/customer"
cd "$TEMP/customer"

# 4. Refresh vendored binaries (if your template uses vendoring)
mkdir -p vendor
cp "$TEMP/template/dist-pack/"*.tgz vendor/   # or equivalent

# 5. Rewrite per-customer slug (single-line; no other mutations allowed)
node -e "let p=require('./package.json');p.name='spawned-customer';require('fs').writeFileSync('package.json',JSON.stringify(p,null,2))"

# 6. Plain workflow — no patches
<package-manager> install                # e.g. pnpm install (no flags!)
<package-manager> typecheck
<package-manager> lint
<package-manager> test
<package-manager> build
```

If any of those fail, the template hasn't met the bar. Fix at the source. Re-run.

## When a template is mature, factor

Once 3+ templates exist with shared shapes (welcome view, getSiteConfig helper, error boundaries, observability stub), stop copying and factor into a `@<scope>/<shared>` package consumed by all templates' forkable artifacts. Until then, copy is the discipline (sync mechanism keeps it lockstep).

## References

- The trigger for this discipline at the makemyweb project: `~/Development4/makemyweb-dashboard/docs/dev-ai-prompt-template-forkability.md`.
- The first template that adopted it (Next.js + WP): `~/Development4/templates/headless-wp-next/apps/customer-site-template/` and the rewrite at `~/Development4/templates/headless-wp-next/docs/CUSTOMER-SITE.md`.
- Factory record: planning/CHANGELOG.md Step 58.
