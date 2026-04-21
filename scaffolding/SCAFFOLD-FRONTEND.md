# Scaffold — Frontend

Routed from `scaffolding/SCAFFOLD.md` when the project is a frontend (web app, SPA, SSR app). Steps ordered so each system can be built and verified before the next depends on it.

**Read `scaffolding/_preamble.md` first** — it covers the shared scaffold rules that apply to all playbooks.

## Step 0 — Handoff check (read before building)

Read `References.md` in full:
- **Compliance section** — regulated data changes auth, logging, and storage choices.
- **Foundational Systems list** — inventory every system; missed systems = silently skipped.
- **Mobile mode** — if discovery picked PWA (not pure responsive), Step 8 below adds service worker + manifest.
- **Open pre-production gates** in `VERSION-LOG.md` — halt until resolved.

## Step 1 — Project setup + types

Conventions: #1 (project setup), #7 (types), #2 (git).

Build:
- Language/runtime version pinned, package manager chosen + lockfile committed.
- Type checker in strict mode, including the language's strictest available flags (e.g. unchecked indexed access, implicit override, unused locals).
- Linter + formatter configs. **Real rules, not stubs** — one linter config per language scope, extending the framework's recommended set. See "Wrapper-boundary enforcement" below.
- `.gitignore`, **pre-commit hooks that install automatically on fresh clone** so downstream forks inherit them without manual setup. Research current idiomatic tools for the chosen runtime.
- Environment validation AT STARTUP (`loadEnv()` equivalent on app entry). See `bootstrap/RED-FLAGS.md` "Env validation at runtime."
- Shared types directory, branded IDs, validation library wired in (one schema = type + validator).
- **Build script pattern:** typecheck and bundle run as separate steps. Never combine emit-to-disk with typecheck-only flags.
- **Monorepo template projects:** root package manifest uses the chosen tool's workspace protocol for cross-package deps. Publishing via the tool's publish command (or tarball packing for local testing). For local consumer-site testing of transitive deps, use the tool's resolution-override mechanism to redirect scoped-package resolutions to local tarballs — otherwise transitive deps try to resolve from a public registry that doesn't know your scope yet.

**Wrapper-boundary enforcement** — Convention #22 says feature code never imports UI-library internals directly. Enforce mechanically via the linter's import-restriction rule: every raw library the `@scope/ui` package wraps belongs on the restricted list for feature + app code. The list grows as you wrap more primitives. Research the linter's current restricted-imports rule syntax.

**Verify:** install succeeds, typechecker + linter run clean, pre-commit fires on commit (runs at least linter + formatter on staged source), deleting a required env var throws on start.

## Step 2 — Theme system

Conventions: #6 (styling), #22 (design system).

Build:
- Design tokens (colors, spacing, typography, shadows, breakpoints) as single source of truth.
- **Dark mode from day 1.** Theme has both light and dark variants wired.
- UI library selected and CONFIGURED with the theme, OR thin wrappers over HTML primitives if the project chose no UI library. Either way, features never import raw UI-library components directly — they import from `src/shared/ui/`. Document the choice in References.md § Convention Overrides.
- Theme provider mounted at the app root. Signals: detects system preference, persists user override, toggles via class/attribute (never media-query-only — blocks user override). Research current APIs for the chosen framework + styling system.

**Verify:** a test page renders with light tokens by default, switches to dark on toggle, and no component hardcodes a color.

## Step 3 — Error handling

Conventions: #8 (errors).

Build:
- Error classes (NetworkError, ValidationError, NotFoundError, AuthError, etc.).
- Error service: catch, classify, log, report (to a crash/error reporting platform).
- Error boundary components (per-route and app-level).
- Error UI components: fallback, empty state, offline, loading.
- Unified loading components (full screen, inline, skeleton).

**Verify:** throwing an error inside a component is caught by the boundary and shows the fallback. Network errors display the offline UI, not a white screen.

## Step 4 — Design-system / component foundation

Conventions: #4 (components), #22 (design system), #14 (accessibility).

Build:
- Base wrapper components around the UI library (Button, Input, Modal, Dialog, Dropdown, etc.).
- Wrappers enforce accessibility (ARIA, focus management, keyboard nav) the UI library's defaults might miss.
- Layout primitives: Stack, Grid, Page container.
- Component catalog (Storybook or equivalent) if the project is team-sized.
- Consistent component API across wrappers (consistent prop names, variant system).
- **Lint-enforce the wrapper boundary.** Direct UI-library imports outside `src/shared/ui/` must fail the build. Use your linter's import-restriction mechanism — feature/app code cannot bypass the wrapper layer. Exempt `src/shared/ui/` itself. Research current linter rule for the chosen language.

**Verify:** a test page built from wrappers only (no raw HTML, no direct UI library imports) renders correctly. Running the lint rule against a direct import fails.

## Step 5 — State management

Conventions: #5 (state), #9 (API — server state).

Build:
- Global store configured (for global-state needs — auth, theme, app-level UI state).
- Server-state library configured (current equivalent of TanStack Query / SWR / Apollo client cache / etc.).
- Slice/module pattern per feature (each feature owns its store slice).
- Pattern for syncing server state with cache invalidation.

**Verify:** a test slice dispatches and reads correctly. Server-state fetch caches and dedupes.

## Step 6 — API layer (client-side)

Conventions: #9 (API integration), #10 (frontend-backend contract).

Build:
- Configured HTTP client with base URL, auth header injection, request/response interceptors.
- Data transformation at the boundary (snake_case↔camelCase, date parsing).
- Integration with server-state library from Step 5.
- Consistent error handling (API errors throw Step 3 error classes).
- Contract typing: if the backend ships typed contracts (OpenAPI, tRPC, GraphQL codegen), wire that in.

**Verify:** a test API call hits a mocked endpoint, returns transformed data, caches via server-state, and displays through Step 5 state.

## Step 7 — Auth

Conventions: #11 (authentication).

Build:
- Auth service wrapping the auth provider (token storage, refresh, logout cleanup, session restore).
- Features NEVER import the auth SDK directly — only the wrapper.
- Auth context/provider mounted at the app root.
- Token storage chosen securely (httpOnly cookie > localStorage for most cases; research current guidance).
- `useAuth()` / `getAuthenticatedUser()` utility.

**Verify:** login/logout flow in a test page works end-to-end; expired token triggers refresh or redirect.

## Step 8 — Routing + layouts + (if PWA) service worker

Conventions: #21 (routing), #11 (route guards), #14 (accessibility).

Build:
- Route definitions.
- Layout components (persistent shells per route section).
- Route guards integrated with Step 7 (protected routes redirect when unauthenticated). Every route definition EITHER declares `public: true` OR wraps its element in a guard — no implicit-unprotected. See `scaffolding/RED-FLAGS.md` #15.
- Loading and error states per route (integrated with Step 3).
- **If PWA:** service worker + manifest. Test install flow on a real mobile browser. See `bootstrap/RED-FLAGS.md` "Mobile Disambiguation."

**Provider composition order at the app root — explicit.** Wrong order silently breaks behavior (see `scaffolding/RED-FLAGS.md` #14). Outermost to innermost: **ErrorBoundary → QueryClient (server state) → Theme → Auth → Router**. Each wraps everything below. The test render wrapper (Step 10) must mirror this order exactly — drift between production entry and the test wrapper = tests pass with the wrong context, silent-failure.

**Verify:** a protected route redirects unauthenticated users. Navigating between routes shows loading states from Step 3. If PWA, the app is installable on a mobile browser.

## Step 9 — Forms (if applicable)

Conventions: #20 (forms), #14 (accessibility).

Build only if References.md lists forms beyond trivial inputs.
- Form library configured.
- Validation schema pattern (one schema = types + validation) using Step 1's validation library.
- Field components with accessible error display (aria-invalid, aria-describedby, labels).
- Multi-step wizard pattern if needed.

**Verify:** a sample form validates, shows field-level errors, preserves state across step navigation.

## Step 10 — Testing

Conventions: #12 (testing), #18 (verification).

**Wiring shape** (tools per stack — research current best):
- A test runner that handles the project's module system + JSX/TSX transform.
- A DOM environment (headless) so component tests run without a real browser.
- A testing library whose assertions describe what the user sees, not implementation details.
- A global setup file that registers DOM matchers (auto-importable so each test file doesn't repeat setup).
- A network-level mocker (not module-level mocks) for tests that cross the API boundary.
- In monorepos, each package gets its own test config; packages with no DOM concerns use a node environment; packages with React concerns use a DOM environment.


Build:
- Test runner configured.
- Custom render wrapper providing Theme + Store + Router + QueryClient + AuthProvider + ErrorBoundary — mirror the production order from Step 8 exactly.
- Network-level API mocking (current equivalent of MSW).
- Test data factories.
- Accessibility testing wired in (axe-core or equivalent) to catch a11y regressions. At least one test on a wrapped component runs axe.
- **Test network-layer client has retries disabled.** Retries on failing test fetches mask real errors. Research current test-config pattern for the chosen data-fetching library.
- **Test and production client configs can differ.** Some library features (abort signals, exponential backoff, streaming) interact unpredictably with mocked networks or test DOMs. Keep production semantics in the prod client; diverge for tests as needed. See `scaffolding/RED-FLAGS.md` #16 (env-inlining trap).

**Verify:** render a sample component through the wrapper. A failing a11y test blocks the PR.

## Step 11 — Performance + build + CI

Conventions: #13 (performance), #15 (build/CI).

Build:
- Code splitting: route-based + component-based for heavy dependencies.
- Bundle size budget enforced in CI.
- Web Vitals monitoring wired in for production.
- CI pipeline: lint → typecheck → test → a11y → build → bundle-size-check → deploy.
- Preview deployments per PR.
- Rollback path documented.

**Verify:** a PR that pushes bundle over budget fails CI. Web Vitals collection works on a staging build.

## Step 11b — Pulse Monitor (dev-only project visibility)

Conventions: #26 (pulse monitor).

Copy the framework's base UI into the project's dev-static path. Serve via a dev-only route. Production builds MUST exclude the pulse UI (tree-shaken out or route-guarded).

Build:
- Dev-only route (e.g., `/dev/pulse`) that serves `templates/pulse-ui/index.html` via the framework's static or dev-middleware path.
- `.pulse-state.json` served as a sibling static file in the same dev route.
- Script (npm run or equivalent) that runs `./archetype/scripts/pulse-inspect.sh --out <path>/.pulse-state.json`.
- Create `docs/systems/pulse-monitor.md` from `archetype/templates/pulse-monitor-spec.md`; fill in the project-specific "Where it's served" section.

**Verify:** `npm run dev`, open `/dev/pulse`, confirm 5 sections render with real data. Verify production build excludes the pulse UI.

## Step 12 — Smoke-test feature (scaffold exit gate)

Build a minimal feature that exercises EVERY shared system. Typical choice: a `/profile` or `/settings` page that:
- Auth-protected (Step 7)
- Fetches from API (Step 6)
- Uses state management (Step 5)
- Renders through the component foundation (Step 4)
- Has a form (Step 9 if present)
- Has an integration test (Step 10)
- Passes a11y checks

This is end-to-end integration proof. Without it, scaffold can be "complete" with misconfigured wiring. See `scaffolding/RED-FLAGS.md` "Scaffold-complete without integration proof."

## Final gate — automated validator

Run `scripts/validate-scaffold.sh`. Fix any failures before committing.

## Post-scaffold output

Same as SCAFFOLD-BACKEND: every system marked implemented with path, docs/systems/ entry per system, References.md updated, `.env.example`, VERSION-LOG entry, initial commit.

## feature-tree status discipline

As each system lands during scaffold, update the feature-tree.md row in-place:

- `not started` → `in progress` when the directory exists and first file lands.
- `in progress` → `implemented` when tests green + system doc in `docs/systems/<name>.md` explains "what's here / what's NOT here yet / verification".
- Location column fills in real path (was `[scaffold fills]`).
- Audit Log gets one entry per scaffold sub-phase (e.g. "B1 monorepo skeleton", "B2 non-UI foundation", "B3 tokens + UI + docs").

Never leave a row at `not started` after its code ships. Pulse-inspect drift detection reads these statuses.

## Monorepo template projects — extra lens

Template-shape projects (framework Step 49) add a second distribution axis beyond "deploy the app":

- Each package has a manifest with real scoped `name`, SemVer `version`, explicit `files` shipping list, and peer-dependencies for consumer-owned runtime (the view framework, the language runtime, etc.) so consumers aren't forced into the template's versions.
- **SemVer discipline via a version-management tool** (research current best): one change-file per change, a command rolls versions + generates per-package CHANGELOG, a command publishes to the registry (or packs for local testing).
- Progressive extraction: build a feature in the reference app first, extract to a package when the pattern stabilizes. Reference: the template's own `docs/CUSTOMER-SITE.md` for consumer-facing walkthrough; `docs/MAINTENANCE.md` for template-maintainer playbook.
- If the bundler needs help consuming packages that ship raw source: use the bundler's transpile-dependency option (research current).
