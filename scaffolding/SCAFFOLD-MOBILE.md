# Scaffold — Mobile

Routed from `scaffolding/SCAFFOLD.md` when the project is native mobile (installable from App Store / Play Store, native device APIs). For responsive-web-on-phone use `SCAFFOLD-FRONTEND.md`. For PWA use `SCAFFOLD-FRONTEND.md` Step 8 (service worker + manifest).

**Zero-stale rule:** mobile tooling churns fast. SDK versions, native-module APIs, submission policies all change. Research at scaffold time for the chosen mobile framework (React Native + Expo, Flutter, native iOS/Android). Do not rely on specific SDK versions named here.

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
- Fall back gracefully when permission denied.
- Provide a stable API the rest of the project uses.

ESLint rule (or equivalent): direct native-library imports outside `src/shared/native/` fail the build.

**Verify:** features use only wrapper imports. A permission-denied test shows graceful fallback UI.

### Step M3 — Permissions configuration

Build:
- **iOS:** every `Info.plist` usage-description string required by the native-library wrappers. Missing strings = App Store rejection.
- **Android:** every manifest `<uses-permission>` required. Dangerous permissions (location, camera, mic) have runtime permission requests wired through Step M2 wrappers.
- Documentation in `docs/systems/permissions.md` listing every permission, why it's needed, which feature uses it.

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

Note: developer-program enrollment costs and review-cycle timing are referenced in `templates/references-mobile.md`. Verify current numbers at enrollment time.

**Verify:** a build uploaded to TestFlight / internal track on Play Console installs on a test device.

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
