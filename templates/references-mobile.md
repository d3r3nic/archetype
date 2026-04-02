# References

## Project

Name: [project name]
Purpose: [one-line description]
Stage: [development / staging / production]
Platforms: [iOS / Android / both]

## Tech Stack

Framework: [React Native / Flutter / SwiftUI / Kotlin / etc.]
Language: [TypeScript / Dart / Swift / Kotlin / etc.]
UI Library: [NativeBase / React Native Paper / Material for Flutter / etc.]
State: [Redux / Riverpod / Provider / Zustand / etc.]
Data Fetching: [React Query / Dio / Alamofire / etc.]
Validation: [Zod / freezed / etc.]
Navigation: [React Navigation / Go Router / etc.]
Testing: [Jest / Flutter test / XCTest / etc.]
Package Manager: [npm / pnpm / pub / CocoaPods / etc.]

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

## Platform-Specific Notes

### iOS
- [minimum iOS version]
- [specific iOS permissions needed]
- [any iOS-specific considerations]

### Android
- [minimum Android API level]
- [specific Android permissions needed]
- [any Android-specific considerations]

## Existing Patterns to Study

- [feature name]: [path] - [what it demonstrates]

## Critical Lessons

- [lesson]: [what happened and the rule that prevents it]

## Convention Overrides

- [convention #]: [what's different and why]
