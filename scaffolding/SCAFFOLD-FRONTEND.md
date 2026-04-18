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
- Type checker in strict mode.
- Linter + formatter configs.
- `.gitignore`, pre-commit hooks, barrel exports.
- Environment validation AT STARTUP (`loadEnv()` equivalent on app entry). See `bootstrap/RED-FLAGS.md` "Env validation at runtime."
- Shared types directory, branded IDs, validation library wired in (one schema = type + validator).
- **If Vite:** create `src/vite-env.d.ts` with `/// <reference types="vite/client" />`. Without it, `import.meta.env` typechecks fail.
- **Build script:** for Vite projects, use `"build": "tsc --noEmit && vite build"` — separate typecheck from bundle. Never `tsc -b` alone (emits stray JS into src/ which fails lint).

**Verify:** install succeeds, typechecker + linter run clean, pre-commit fires, deleting a required env var throws on start.

## Step 2 — Theme system

Conventions: #6 (styling), #22 (design system).

Build:
- Design tokens (colors, spacing, typography, shadows, breakpoints) as single source of truth.
- **Dark mode from day 1.** Theme has both light and dark variants wired.
- UI library selected and CONFIGURED with the theme, OR thin wrappers over HTML primitives if the project chose Tailwind-only (no UI library). Either way, features never import raw UI-library components directly — they import from `src/shared/ui/`. Document the choice in References.md § Convention Overrides.
- Theme provider mounted at the app root. Concrete shape:
  - System-preference detection via `matchMedia('(prefers-color-scheme: dark)')`.
  - User override persisted to `localStorage` under a project-specific key (document it in docs/systems/theme.md).
  - Tailwind projects: use `darkMode: 'class'` + `<html class="dark">` toggle (not media-query-only — blocks user override). CSS-variable projects: semantic tokens swap via `:root` / `[data-theme="dark"]` selectors.

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
- ESLint rule: direct UI-library imports outside `src/shared/ui/` fail the build. Pattern via `no-restricted-imports` — example:

```js
// .eslintrc.cjs — ban direct UI-lib imports in feature/app code; allow in shared/ui/
rules: {
  'no-restricted-imports': ['error', {
    patterns: [{
      group: ['@mui/*', '@chakra-ui/*', '@radix-ui/*', /* the chosen UI library */],
      message: 'Import from @/shared/ui/ instead of the UI library directly.',
    }],
  }],
},
overrides: [{
  files: ['src/shared/ui/**/*.{ts,tsx}'],
  rules: { 'no-restricted-imports': 'off' },
}],
```

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

**Provider composition order at the app root — explicit.** Wrong order silently breaks behavior (see `scaffolding/RED-FLAGS.md` #14). Mount in this order (outermost to innermost):

```
<ErrorBoundary>                  (catches everything below)
  <QueryClientProvider>          (Step 6 — must wrap any component using useQuery)
    <ThemeProvider>              (Step 2 — wraps all styled components)
      <AuthProvider>             (Step 7 — must be ABOVE Router so guards see auth)
        <Router>                 (this Step 8)
          <AppLayout />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
</ErrorBoundary>
```

The test render wrapper (Step 10) must mirror this order exactly. Drift between production App.tsx and the test wrapper = tests pass with the wrong context, silent-failure.

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

Build:
- Test runner configured.
- Custom render wrapper providing Theme + Store + Router + QueryClient + AuthProvider + ErrorBoundary — mirror the production order from Step 8 exactly.
- Network-level API mocking (current equivalent of MSW).
- Test data factories.
- Accessibility testing wired in (axe-core or equivalent) to catch a11y regressions. At least one test on a wrapped component runs axe.
- **Test QueryClient has retries disabled.** `new QueryClient({ defaultOptions: { queries: { retry: false }}})` — otherwise failing test fetches retry silently and slow down the suite; real errors get masked.
- **Do NOT pass `signal` from `queryFn: ({signal}) => fetch(..., {signal})` in test setups.** Under jsdom + MSW, the abort signal can stall success-path handlers. Keep `signal` in production client, drop it in test client. See `scaffolding/RED-FLAGS.md` #16 — related env-inlining trap can also break tests.

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
