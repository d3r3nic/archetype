# Scaffold — Mobile

Routed from `scaffolding/SCAFFOLD.md` when the project is native mobile (installable from App Store / Play Store, native device APIs). For responsive-web-on-phone use `SCAFFOLD-FRONTEND.md`. For PWA use `SCAFFOLD-FRONTEND.md` Step 8 (service worker + manifest).

**Read `scaffolding/_preamble.md` first** — it covers the shared scaffold rules. Mobile tooling churns especially fast (SDK versions, native-module APIs, submission policies), so the zero-stale rule is particularly important here.

Most Step 0-11 of `SCAFFOLD-FRONTEND.md` apply identically to mobile (project setup, types, theme, components, state, API layer, auth, forms, testing, CI). Mobile-specific additions below.

## Mobile-specific additions

### Step M1 — Project shape decision

Before building:
- **Framework**: React Native, Flutter, native iOS/Android, or cross-platform alternative. Decision recorded in References.md per bootstrap.
- **Workflow (React Native only)**: managed (Expo) vs bare. See `templates/references-mobile.md` "Expo managed vs bare" section. Decision changes native-module access.
- **Backend approach**: custom (separate folder) vs BaaS (platform backend) vs offline-only. See `templates/references-mobile.md` "Backend" section.

### Step M2 — Native-module wrappers

Conventions: #22 (design system) extended for mobile per `templates/references-mobile.md` "Native-Module Wrapping" section.

Every native capability (camera, HealthKit/Google Fit, haptics, biometrics, secure storage, geolocation, push notifications, BLE) gets a project-local wrapper. Features import from the wrapper, not the native library directly.

Build wrappers for every capability listed in References.md:
- Configure the native library with project defaults.
- Handle permission request UX consistently.
- Fall back gracefully when permission denied (simulator, test environments, user-denied, OS feature-unavailable all need graceful handling).
- Provide a stable API the rest of the project uses.

**Wrapper shape signals (apply uniformly across all wrappers in the project):**
- **Error model:** throw a typed AppError subclass (e.g., `PermissionDeniedError`). Never bubble raw native errors to features.
- **Type shape:** uniform across all wrappers. Pick once (module-level objects, classes, hooks, or singletons) and apply everywhere. Inconsistency is the anti-pattern.
- **Permission timing:** lazy (on first capability use) unless References.md declares regulated data — then eager at first launch with disclosure.
- **Test-environment fallback:** each wrapper exposes an availability check that returns false where the native module is absent (simulator, CI, web preview). Features guard calls with it.

ESLint rule (or equivalent): direct native-library imports outside `src/shared/native/` fail the build.

**Verify:** features use only wrapper imports. A permission-denied test shows graceful fallback UI.

### Step M3 — Permissions configuration

Build:
- **iOS:** every `Info.plist` usage-description string required by the native-library wrappers. Missing strings = App Store rejection.
- **Android:** every manifest `<uses-permission>` required. Dangerous permissions (location, camera, mic) have runtime permission requests wired through Step M2 wrappers.
- Documentation in `docs/systems/permissions.md` listing every permission, why it's needed, which feature uses it.
- Managed workflows declare permissions in the framework's config file; bare workflows edit native manifest files directly. Research the current pattern for the chosen mobile framework.

**Every native capability requires platform-specific permission strings — three dimensions per capability:**
- iOS usage-description string (Info.plist — customer-facing rationale text)
- Android manifest permission + runtime request for dangerous permissions
- API-level variations (permission names and requirements change between OS versions — e.g., notifications, location-in-background, biometric)

Research current requirements per capability at scaffold time on Apple Developer Documentation and Android Developers Permission guides. Permission models drift as OS versions release — a stale matrix is worse than no matrix. Have a human review the list against current store submission policies before first build.

**Verify:** build succeeds on both platforms (iOS Xcode build + Android Gradle build). Permission request UX tested on a real device or emulator.

### Step M4 — Offline sync

Conventions: #5 (state), #9 (API — server-state offline handling).

If References.md discovery answered "works offline" = yes:
- Local persistent store (SQLite via a wrapper, MMKV, or equivalent).
- Sync queue: mutations performed offline queue and replay on reconnect.
- Conflict resolution strategy (last-write-wins, CRDT, or server-wins — documented decision).
- UI indicator for offline state.

If regulated data + offline: see `bootstrap/RED-FLAGS.md` "Offline + regulated data" — this combination is a compliance risk that should have been flagged at bootstrap. Verify encryption-at-rest on local store, remote wipe capability, secure session handling.

**Verify:** turn off network on a test device, perform mutations, turn network back on, mutations sync.

### Step M5 — Push notifications

Build (if push is in scope per References.md):
- Push provider wired in (current platform-native or cross-platform service).
- Token registration + refresh flow.
- Foreground vs background notification handling.
- Deep-link handling from notification tap.
- Opt-in permission UX.

**Verify:** send a test push to a test device; tapping deep-links correctly.

### Step M6 — Code signing + submission flow

Build:
- **iOS:** certificates, provisioning profiles, signing config documented. TestFlight upload flow scripted if possible.
- **Android:** release keystore securely stored, signing config in `build.gradle` reading from env. Play Console upload flow scripted if possible.
- EAS Build (React Native + Expo) config if that's the chosen approach.
- OTA (over-the-air) update strategy documented (if applicable).

**Build-service config signals:**
- Separate profiles for internal dev, internal-distribution preview, and store-submission production. Same bundle, different distribution.
- Build numbers auto-increment on the production profile.
- Real credentials (Apple IDs, team IDs, service-account keys) are NEVER committed. Use the build service's secret mechanism or the CI platform's secrets.
- Research the current schema for the chosen build service.

**SDK-aware package installation:** use the SDK's package installer (not generic `npm install`) for packages with SDK peers. The SDK knows its compatibility matrix; generic installers don't. See `scaffolding/RED-FLAGS.md` #18.

**Build-time env-inlining trap:** bundlers and Babel presets rewrite public env variables to literal values at transform time. Runtime env mutation in tests has NO effect on these. Research the current opt-out mechanism for the chosen stack. See `scaffolding/RED-FLAGS.md` #16.

Note: developer-program enrollment costs and review-cycle timing are referenced in `templates/references-mobile.md`. Verify current numbers at enrollment time.

**Verify:** a build uploaded to TestFlight / internal track on Play Console installs on a test device.

## Step M6b — Pulse Monitor (dev-only, host-served)

Conventions: #26 (pulse monitor).

Mobile projects don't bundle the pulse UI into the app. Instead, serve it locally on the developer's host machine:
- `npx http-server archetype/templates/pulse-ui/ -p 4500` (or equivalent static server).
- Developer opens `http://localhost:4500` in a browser; the page fetches `.pulse-state.json` from the same host.
- Run `./archetype/scripts/pulse-inspect.sh --out archetype/templates/pulse-ui/.pulse-state.json` to refresh state.
- Optionally scaffold a `scripts/pulse.sh` convenience wrapper that does both.

Create `docs/systems/pulse-monitor.md` from `archetype/templates/pulse-monitor-spec.md`; document this host-served pattern in the project-specific "Where it's served" section.

## Step M7 — Smoke-test feature (scaffold exit gate)

Build a minimal feature exercising the full mobile stack:
- Auth-protected
- Uses at least one native-module wrapper (e.g., secure storage for the auth token)
- Fetches from API
- Renders through theme + components
- Tested on both iOS and Android simulators/emulators at minimum

## Final gate

Run `scripts/validate-scaffold.sh`. Fix failures before committing.

## Post-scaffold output

Same pattern as SCAFFOLD-BACKEND / FRONTEND. Mobile-specific files: `ios/Info.plist`, `android/AndroidManifest.xml`, build scripts, permission documentation.
