# Scaffold — Mobile

Routed from `scaffolding/SCAFFOLD.md` when the project is native mobile (installable from App Store / Play Store, native device APIs). For responsive-web-on-phone use `SCAFFOLD-FRONTEND.md`. For PWA use `SCAFFOLD-FRONTEND.md` Step 8 (service worker + manifest).

**Read `scaffolding/_preamble.md` first** — it covers the shared scaffold rules. Mobile tooling churns especially fast (SDK versions, native-module APIs, submission policies), so the zero-stale rule is particularly important here.

Most Step 0-11 of `SCAFFOLD-FRONTEND.md` apply identically to mobile (project setup, types, theme, components, state, API layer, auth, forms, testing, CI). The theme step's rule holds here too: the selected styling source follows the artifact in the recorded direction of truth (`References.md § Design Artifact`), and the mobile References template's `Platform parity` line says how both platforms' states stay aligned (#27). The component foundation uses the project's selected native, library, adapter, wrapper, or project-owned boundary. Its applicable-state evidence, focus behavior, discovery surface, and capture command apply here as well. Mobile-specific additions follow.

## Mobile-specific additions

### Step M1 — Project shape decision

Before building:
- **Framework**: a cross-platform mobile framework, or each platform's native toolchain. Decision recorded in References.md per bootstrap.
- **Workflow (cross-platform frameworks only)**: managed SDK vs bare native project. See `templates/references-mobile.md` "Managed vs bare native toolchain" section. Decision changes native-module access.
- **Backend approach**: custom (separate folder) vs hosted backend service vs offline-only. See `templates/references-mobile.md` "Backend" section.

### Step M2: Native capability boundary

Conventions: #22 (design system) extended for mobile per `templates/references-mobile.md` "Native-Module Wrapping" section.

For each native capability in scope (camera, health data, haptics, biometrics, secure storage, geolocation, push notifications, BLE), research the current platform and framework guidance. Record whether features use the platform or library directly, a selective adapter, or a project-owned wrapper, and why that boundary fits the permission flow, testability, expected change, and access needs.

Where the selected boundary owns these concerns:
- Configure project defaults that should be shared.
- Keep permission requests and denial behavior consistent with the accepted interaction.
- Handle simulator, test-environment, user-denied, and unavailable-platform cases that apply.
- Translate unstable or unsafe native details into a project contract when consumers should not own them.

**Boundary signals:**
- **Error model:** expose errors the feature can handle safely and meaningfully; do not leak sensitive native details.
- **Type shape:** use consistent shapes for the same concepts. Different capability responsibilities may justify different interfaces.
- **Permission timing:** choose timing from platform guidance, the feature's moment of need, disclosure requirements, and accepted user flow.
- **Test-environment behavior:** provide availability checks, fixtures, or platform test support where the capability can be absent.

If the project selects a restricted adapter or wrapper boundary, configure the current toolchain to catch direct imports that bypass it. Direct imports remain valid when they are the recorded choice.

**Verify:** each feature follows its recorded capability boundary. Permission denial and unavailable-platform cases show the behavior promised by the artifact and pass the applicable access checks.

### Step M3 — Permissions configuration

Build:
- **iOS:** every `Info.plist` usage-description string required by the selected capability integrations. Missing required strings can cause rejection.
- **Android:** every required manifest `<uses-permission>`. Dangerous permissions (location, camera, mic) have runtime requests wired through the Step M2 boundary.
- Documentation in `docs/systems/permissions.md` listing every permission, why it's needed, which feature uses it.
- Managed workflows declare permissions in the framework's config file; bare workflows edit native manifest files directly. Research the current pattern for the chosen mobile framework.

**For each native capability that requires permission, verify three dimensions:**
- iOS usage-description string (Info.plist — customer-facing rationale text)
- Android manifest permission + runtime request for dangerous permissions
- API-level variations (permission names and requirements change between OS versions — e.g., notifications, location-in-background, biometric)

Research current requirements per capability at scaffold time on Apple Developer Documentation and Android Developers Permission guides. Permission models drift as OS versions release — a stale matrix is worse than no matrix. Have a human review the list against current store submission policies before first build.

**Verify:** build succeeds on both platforms, each through its own native build toolchain. Permission request UX tested on a real device or emulator.

### Step M4 — Offline sync

Conventions: #5 (state), #9 (API — server-state offline handling).

If References.md discovery answered "works offline" = yes:
- Local persistent store (an embedded database or key-value store, reached through the Step M2 boundary selected for it).
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
- **iOS:** certificates, provisioning profiles, signing config documented. Upload flow to the platform's beta-distribution channel scripted if possible.
- **Android:** release keystore securely stored, signing config in the native build file reading from env. Upload flow to the store's internal track scripted if possible.
- Hosted build-service config if the project uses one.
- OTA (over-the-air) update strategy documented (if applicable).

**Build-service config signals:**
- Separate profiles for internal dev, internal-distribution preview, and store-submission production. Same bundle, different distribution.
- Build numbers auto-increment on the production profile.
- Real credentials (Apple IDs, team IDs, service-account keys) are NEVER committed. Use the build service's secret mechanism or the CI platform's secrets.
- Research the current schema for the chosen build service.

**SDK-aware package installation:** use the SDK's own package installer (not the package manager's generic install) for packages with SDK peers. The SDK knows its compatibility matrix; generic installers don't. See `scaffolding/RED-FLAGS.md` #18.

**Build-time env-inlining trap:** bundlers and transpiler presets rewrite public env variables to literal values at transform time. Runtime env mutation in tests has NO effect on these. Research the current opt-out mechanism for the chosen stack. See `scaffolding/RED-FLAGS.md` #16.

Note: developer-program enrollment costs and review-cycle timing are referenced in `templates/references-mobile.md`. Verify current numbers at enrollment time.

**Verify:** a build uploaded to each platform's beta or internal distribution channel installs on a test device.

## Step M6b — Pulse Monitor (dev-only, host-served)

Conventions: #26 (pulse monitor).

Mobile projects don't bundle the pulse UI into the app. Instead, serve it locally on the developer's host machine:
- Copy `archetype/templates/pulse-ui/` into a project-owned directory the app bundle never includes (for example `dev/pulse/`), with the snapshot git-ignored, and serve that directory with any static file server on a local port. No project artifact is written inside the framework folder.
- Developer opens that local address in a browser; the page fetches `.pulse-state.json` from the same directory.
- Run `archetype/scripts/pulse-inspect.sh --out <that project-owned directory>/.pulse-state.json` to refresh state.
- Optionally scaffold a project-owned `scripts/pulse.sh` convenience wrapper that does both.

Create `docs/systems/pulse-monitor.md` from `archetype/templates/pulse-monitor-spec.md`; document this host-served pattern in the project-specific "Where it's served" section, and read that spec's implementation notes before choosing the snapshot path.

## Step M7 — Smoke-test feature (scaffold exit gate)

Build a minimal feature exercising the full mobile stack:
- Auth-protected
- Uses at least one native-module wrapper (e.g., secure storage for the auth token)
- Fetches from API
- Renders through theme + components
- Tested on both iOS and Android simulators/emulators at minimum

## Final gate

Run `scripts/validate-scaffold.sh --required known-screen`. Fix failures before committing. A native mobile project is a known-screen route, so a missing or example-only Design Artifact section cannot close the scaffold.

## Post-scaffold output

Same pattern as SCAFFOLD-BACKEND / FRONTEND. Mobile-specific files: `ios/Info.plist`, `android/AndroidManifest.xml`, build scripts, permission documentation.
