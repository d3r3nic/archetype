# Scaffold — Mobile

Routed from `scaffolding/SCAFFOLD.md` when the project is an app installed on phones or tablets through their stores, using the device's own capabilities. A web product used in a phone's browser uses `SCAFFOLD-FRONTEND.md`; an installable web app uses its Step 8.

**Read `scaffolding/_preamble.md` first.** Device tooling, platform rules and store policies change quickly, so research current guidance at scaffold time and record it in the project's files.

## The systems a device app builds

Build the systems this app needs, each from its convention, applying the decisions the project recorded and researching the chosen toolkit where the record is silent. The frontend route describes most of them; use its steps where they fit a device app, never its web-only parts (addresses in a browser, a browser's offline worker, site-wide content for a website):
- project setup and configuration, with the configuration owner and where the checks run (#1, #2, #7, #15);
- the theme, from the artifact in the recorded direction of truth, with the mobile References template's `Platform parity` line saying how the platforms' states stay aligned (#6, #27);
- the component foundation, with its applicable-state evidence, focus behavior, discovery surface and capture command (#4, #14, #22);
- errors and waiting states (#8);
- shared state and data caching, where screens share them (#5);
- the API client for each remote service (#9, #10);
- authentication, with credentials in the platform's secure store (#11);
- navigation between screens, protected by default (#21);
- forms (#20);
- testing, with the shared setup (#12).

Each shared system records its § Boundaries line in References.md, as the frontend steps describe.

## Device-specific steps

### Step M1 — Project shape decision

Before building, record in References.md, from the bootstrap research:
- **Toolkit:** a cross-platform toolkit, or each platform's own toolchain.
- **Workflow**, for a cross-platform toolkit: its managed workflow or a native project (templates/references-mobile.md, "Managed vs bare native toolchain"). The choice changes what native capabilities the app can reach.
- **Backend:** its own service (a separate folder), a hosted backend service, or none, for an offline-only app (templates/references-mobile.md, "Backend").

### Step M2: Native capability boundary

Conventions: #22, extended for devices in templates/references-mobile.md, "Native-Module Wrapping".

For each native capability in scope (camera, health data, haptics, biometrics, secure storage, location, push notifications, short-range radio), research the current platform and toolkit guidance. Record whether features use the platform or library directly, a selective adapter, or a project-owned wrapper, and why that boundary fits the permission flow, testability, expected change and access needs.

Where the selected boundary owns these concerns:
- configure the defaults that should be shared;
- keep permission requests and denial behavior consistent with the accepted interaction;
- handle the simulator, test-environment, user-denied and unavailable-platform cases that apply;
- translate unstable or unsafe native details into a project contract when consumers should not own them.

**Boundary signals:**
- **Error model:** expose errors the feature can handle safely and meaningfully; never leak sensitive native details.
- **Type shape:** the same concepts get the same shapes; different capabilities may justify different interfaces.
- **Permission timing:** choose it from platform guidance, the feature's moment of need, disclosure requirements and the accepted flow.
- **Test-environment behavior:** availability checks, fixtures or platform test support where the capability can be absent.

If the project selects a restricted adapter or wrapper boundary, record it in § Boundaries and let the checks catch direct use that bypasses it. Direct use remains valid when it is the recorded choice.

**Verify:** each feature follows its recorded capability boundary; permission denial and unavailable-platform cases behave as the artifact promises and pass the applicable access checks.

### Step M3 — Permissions configuration

Build, for every platform the app ships to:
- each permission the selected capabilities require, declared the way the platform requires, with the rationale text people see; a missing declaration can get the app rejected;
- the runtime request for each permission the platform treats as sensitive, through the Step M2 boundary;
- `docs/systems/permissions.md` listing every permission, why it is needed and which feature uses it.

Permission names and rules change between operating-system versions (notifications, background location and biometrics among them). Research the current requirements for each capability in each platform's own documentation at scaffold time, and have a person check the list against current store policies before the first build.

**Verify:** the app builds for each platform with its own toolchain; the permission requests behave as intended on a real device or an emulator.

### Step M4 — Offline sync

Applies when discovery answered that the app works offline. Conventions: #5, #9.

- A local persistent store, reached through the boundary Step M2 selected for it.
- A queue of changes made offline, replayed on reconnect.
- A conflict strategy, recorded with its reason.
- A visible offline state.

With regulated data offline, see `bootstrap/RED-FLAGS.md`, "Offline + regulated data": encrypt the local store, provide remote wipe, and handle sessions securely.

**Verify:** with the network off, make changes; turn it on; the changes sync.

### Step M5 — Push notifications

Applies when push is in scope in References.md.
- The push service chosen for the platforms.
- Token registration and refresh.
- Foreground and background handling.
- Opening the right screen from a notification.
- The opt-in request at the moment it makes sense.

**Verify:** a test push reaches a test device, and tapping it opens the right screen.

### Step M6 — Code signing and submission

- Signing for each platform: certificates and profiles or keys, stored securely and never committed, with the signing configuration read from the environment. Script the upload to each platform's beta or internal testing channel where possible.
- A hosted build service's configuration, when the project uses one: separate profiles for development, internal preview and store release; build numbers that increase on release builds; credentials kept in the build service's or the pipeline's secret store.
- The strategy for updates delivered without a store release, when the toolkit offers them and the project uses them.
- Companion packages that the toolkit versions itself are installed through the toolkit's own installer, and its health check runs as part of verification (`scaffolding/RED-FLAGS.md`, section 18).
- Values the build inlines cannot be changed by tests at run time; research the chosen toolkit's way around it (`scaffolding/RED-FLAGS.md`, section 16).

Store enrollment costs and review timing change; the template records where to check them at enrollment time.

**Verify:** a build uploaded to each platform's beta or internal channel installs on a test device.

## Step M6b — Pulse Monitor (dev-only, host-served)

Applies when the project builds one (#26).

A device app does not bundle the pulse UI. Serve it on the developer's machine:
- Copy `archetype/templates/pulse-ui/` into a project-owned folder the app bundle never includes (for example `dev/pulse/`), with the snapshot git-ignored, and serve that folder with any static file server on a local port. Nothing is written inside the framework folder.
- The developer opens that local address; the page reads `.pulse-state.json` from the same folder.
- Run `archetype/scripts/pulse-inspect.sh --out <that folder>/.pulse-state.json` to refresh it, optionally through a project-owned script that does both.

Create `docs/systems/pulse-monitor.md` from `archetype/templates/pulse-monitor-spec.md`, describe this host-served pattern in its "Where it's served" section, and read the spec's implementation notes before choosing the snapshot path.

## Step M7 — Smoke-test feature (scaffold exit gate)

Build one minimal feature through the whole app: behind sign-in when the app has accounts, using at least one native capability through its recorded boundary (secure storage for the session is a common choice), reading through the API client, rendering through the theme and components, and tested on every platform the app ships to, on simulators or emulators at least.

## Final gate

Run `scripts/validate-scaffold.sh --required known-screen` and fix what it reports before committing. A device app has screens, so a missing Design Artifact section cannot close the scaffold.

## Post-scaffold output

The same as the other playbooks, plus each platform's permission declarations, the build scripts and the permission documentation.
