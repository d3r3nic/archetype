# Frontend scaffold: routing, layouts, and the offline worker for an installable web app

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 8: Routing, layouts, and the offline worker for an installable web app
Read: #21; #11; #14; bootstrap/RED-FLAGS.md § Mobile Disambiguation (when the app is installable or the mobile mode is still open); scaffolding/_preamble.md § Convention-mapping rule; scaffolding/RED-FLAGS.md § 14. Root composition order (frontend/mobile); scaffolding/RED-FLAGS.md § 15. Route guards forgotten on protected routes
Produces: the route definitions, the layouts, the guard, the root composition, and for an installable web app its offline worker and install manifest
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: when the product has accounts, a protected route opened without a session; a navigation showing the loading state of Step 3; and the install prompt when the app is installable
Depends on: scaffold-frontend.4; scaffold-frontend.7
Skip when: the product has a single view and nothing to navigate between

Apply #21 through the recorded decisions:
- Every route defined once; every link built from the definitions.
- When the product has accounts (Step 7), protected by default: every route goes through the one guard unless its definition declares it public.
- Layouts that stay in place while their content changes, where the stack supports it.
- Each route's waiting and error states from Step 3.
- The root composition: when the stack composes shared contexts at the root (error handling, data cache, theme, identity, navigation), their order decides what each can see. Record the order once, as one composition that the app and the test setup (Step 10) both use.
- When References.md § Project, Mobile mode, commits to an installable web app: its offline worker and install manifest, and the install tried on a real phone browser (bootstrap/RED-FLAGS.md, Mobile Disambiguation).

**Verify:** when the product has accounts, a protected route refuses a visitor without a session; navigating shows Step 3's loading state; an installable app installs on a phone browser.
