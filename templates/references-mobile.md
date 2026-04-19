# References

## Project

Each line must start with `- ` (dash space). `scripts/pulse-inspect.sh` parses these bullets; lines without a leading dash are ignored.

- Name: [project name]
- Purpose: [one-line description]
- Stage: [development / staging / production]
- Platforms: [iOS / Android / both]

## Tech Stack

Each line must start with `- ` (dash space); content is `- Key: Value`. Inspector parses every bullet.

- Framework: [React Native / Flutter / SwiftUI / Kotlin / etc.]
- Language: [TypeScript / Dart / Swift / Kotlin / etc.]
- UI Library: [NativeBase / React Native Paper / Material for Flutter / etc.]
- State: [Redux / Riverpod / Provider / Zustand / etc.]
- Data Fetching: [React Query / Dio / Alamofire / etc.]
- Validation: [Zod / freezed / etc.]
- Navigation: [React Navigation / Go Router / etc.]
- Testing: [Jest / Flutter test / XCTest / etc.]
- Package Manager: [npm / pnpm / pub / CocoaPods / etc.]

## Commands

```
dev:       [command to run on simulator/emulator]
build:ios: [command to build iOS]
build:android: [command to build Android]
test:      [command to run tests]
typecheck: [command to run type checker]
lint:      [command to lint]
deploy:    [command to deploy - TestFlight, Play Store, etc.]
clean:     [command to clean build artifacts]
```

## Foundational Systems

Each system is built once following convention #0 (Reusability). Features plug into these, never build ad-hoc.

### Git & Project Init (#2)
Commit convention: [e.g., conventional commits]
Branch strategy: [e.g., trunk-based]
Pre-commit hooks: [what runs]

### Project Structure & Types (#1, #7)
Folder structure: [see Folder Structure section below]
Type checking: [strict mode configuration]
Validation library: [which one]
Shared types: [path to shared type definitions]

### Theme System (#6)
Location: [path to theme definition]
Tokens: [where design tokens are defined - colors, spacing, typography]
Platform adaptation: [how theme adapts between iOS and Android if applicable]
Usage: [how features use theme values]

### Error System (#8)
Location: [path to error service]
Error types: [custom error classes]
Error display: [how errors are shown to users - toasts, alerts, error screens]
Loading states: [unified loading and empty state components]
Crash reporting: [which service - Crashlytics, Sentry, etc.]
Usage: [how features use the error system]

### API Layer & Contract (#9, #10)
Location: [path to API client]
Client: [configured HTTP client]
Cache strategy: [how API data is cached]
Offline handling: [how the app behaves when offline]
Response format: [consistent envelope structure]
Usage: [how features define API calls]

### Auth System (#11)
Location: [path to auth service]
Auth utility: [how to get authenticated user]
Token management: [secure storage - keychain, encrypted preferences]
Session handling: [how login/logout/refresh work]
Deep linking: [auth-related deep links if applicable]
Usage: [how features check auth]

### Navigation (#21)
Router: [which navigation library]
Route definitions: [path to route config]
Navigation guards: [auth protection on routes]
Deep linking: [deep link configuration]
Usage: [how features navigate]

### State Management (#5)
Store: [path to store configuration]
Pattern: [e.g., "one slice per feature"]
Server state: [how API data integrates with state]
Offline state: [how offline data is persisted]
Usage: [how features manage state]

### Component Foundation (#4, #22)
Location: [path to shared components]
Base components: [wrapper components]
Import rule: [import convention]
Platform-specific: [components that differ between iOS/Android]
Usage: [how features use shared components]

### Form System (#20) [if applicable]
Location: [path to form utilities]
Validation: [how forms validate]
Usage: [how features build forms]

### Testing Setup (#12, #18)
Test runner: [which one]
Test utilities: [path to shared test helpers]
Device testing: [simulator/emulator/physical device testing setup]
Verification commands: [exact commands]

### CI/CD & Build (#15)
CI platform: [which one]
Pipeline: [sequence]
iOS deployment: [TestFlight, App Store process]
Android deployment: [Play Store process]
Code signing: [how certificates/keys are managed]

## Folder Structure

```
[paste actual folder structure here]
```

## Backend

Mobile apps almost always talk to a backend. Document which stack serves this mobile app:
- Backend approach: [Custom backend (separate folder with its own References.md) / Platform backend (BaaS — uses references-platform.md) / None (offline-only, no backend)]
- Backend location: [path to backend folder if custom, or platform name + admin URL if BaaS]
- API contract: [REST base URL / GraphQL endpoint / SDK name]
- Offline sync: [strategy for reconnecting after offline use]
- Auth flow: [how mobile obtains and refreshes tokens — deep-link OAuth, embedded SDK, etc.]

If backend is a separate custom folder, it has its own `References.md` using `references-backend.md`. If it's a BaaS platform, it has its own folder (e.g., `backend-<platform>/`) using `references-platform.md`. Cross-reference here.

## Native-Module Wrapping

Mobile projects need native-module wrappers for the same reason convention #22 requires UI-library wrappers: features should not import the native-capability library directly. Features that need a native capability (camera, HealthKit/Google Fit, haptics, biometrics, secure storage, geolocation, push notifications, BLE) import from a project-local wrapper that:
- Configures the native library with the project's defaults
- Handles permission request UX consistently
- Falls back gracefully when permission denied
- Provides a stable API the rest of the project uses

This applies to React Native, Flutter, and native iOS/Android. Research the current native-module approach for the chosen mobile framework (managed workflow vs bare workflow for React Native, platform channels for Flutter, etc.) at bootstrap time.

List the wrappers in use:
- [native capability]: [wrapper path] — [what native library it wraps, why]

## Platform-Specific Notes

### iOS
- Minimum iOS version: [e.g., iOS 16+]
- Required Info.plist permission strings: [NSCameraUsageDescription, NSHealthShareUsageDescription, etc. Missing entries cause App Store rejection.]
- Code signing / provisioning: [how certificates and profiles are managed]
- TestFlight / App Store: [submission timeline and costs — Apple Developer $99/yr, typical review 24-48h]

### Android
- Minimum API level: [e.g., API 26+]
- Required manifest permissions: [CAMERA, ACCESS_FINE_LOCATION, etc.]
- Signing config: [how release keystore is managed]
- Play Console: [submission timeline and costs — Google Play $25 one-time, typical review 24-72h]

### Expo managed vs bare (React Native only)
- **Managed workflow:** Expo handles native config, build, OTA updates. Faster to start. Limited to SDK-supported native modules unless you eject.
- **Bare workflow:** full native project; can use any native module. Requires Xcode and Android Studio toolchain.
- Choice depends on which native capabilities you need and whether the user owns the toolchain. Decide at bootstrap time.

## Existing Patterns to Study

- [feature name]: [path] - [what it demonstrates]

## Critical Lessons

- [lesson]: [what happened and the rule that prevents it]

## Convention Overrides

- [convention #]: [what's different and why]
