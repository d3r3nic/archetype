# Frontend scaffold: routing, layouts, and the service worker for an installable web app

Part of the frontend scaffold playbook (scaffolding/SCAFFOLD-FRONTEND.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step. Before building, read the conventions it names and write how the system will be built in its References.md section (scaffolding/_preamble.md); when it lands, update its feature-tree.md row and its docs/systems/ page.

## Step 8: Routing, layouts, and the service worker for an installable web app
Read: #21; #11; #14; bootstrap/RED-FLAGS.md § Mobile Disambiguation (when the app is installable or the mobile mode is still open); scaffolding/_preamble.md § Convention-mapping rule; scaffolding/RED-FLAGS.md § 14. Provider composition order (frontend/mobile); scaffolding/RED-FLAGS.md § 15. Route guards forgotten on protected routes
Produces: the routes, the layouts, the guards, and for an installable web app the service worker and the manifest
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: a protected route opened without a session, a navigation showing the loading state of Step 3, and the install prompt when the app is installable
Depends on: scaffold-frontend.4; scaffold-frontend.7

Build:
- Route definitions.
- Layout components (persistent shells per route section).
- Route guards integrated with Step 7 (protected routes redirect when unauthenticated). Every route definition EITHER declares `public: true` OR wraps its element in a guard — no implicit-unprotected. See `scaffolding/RED-FLAGS.md` #15.
- Loading and error states per route (integrated with Step 3).
- **If PWA:** service worker + manifest. Test install flow on a real mobile browser. See `bootstrap/RED-FLAGS.md` "Mobile Disambiguation."

**Provider composition order at the app root: explicit.** Wrong order silently breaks behavior (see `scaffolding/RED-FLAGS.md` #14). Outermost to innermost: **ErrorBoundary → server-state provider → Theme → Auth → Router**. Each wraps everything below. The test render wrapper (Step 10) must mirror this order exactly: drift between production entry and the test wrapper = tests pass with the wrong context, silent-failure.

**Verify:** a protected route redirects unauthenticated users. Navigating between routes shows loading states from Step 3. If PWA, the app is installable on a mobile browser.
