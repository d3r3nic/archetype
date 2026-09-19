# Bootstrap: discovery, group 2

Part of the bootstrap playbook (bootstrap/ONBOARD.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step: read it when the script names it, with the reading it lists, and close it before opening the next.

## Step 2.2: Group 2 - Where does it run?
Read: bootstrap/ONBOARD-DISCOVERY.md; bootstrap/RED-FLAGS.md § Discovery Turn Budget; bootstrap/RED-FLAGS.md § Mobile Disambiguation
Produces: the platforms, the mobile mode when a phone is involved, and the primary context
Check: evidence: the owner's answers to this group in their own words, quoted; a question an earlier answer settled is recorded as inferred, with the inference; a question the owner declined is recorded as declined, with what was assumed

- Should this work in a web browser?
- Should this be a phone app, installed from an app store?
- Should this be a desktop application, installed on a laptop or desktop?
- Or some combination?
- Name a well-known app in each category so the question lands with a non-technical user. Pick apps that are popular now, not ones you remember.
- Where will people mostly use it: sitting at a computer, on a phone while doing something else, on a shared screen in a room, or outdoors? Which of those is most of the time? (Fills `Primary context` in References.md § Design Artifact.)

If the user says "phone app" or "works on my phone," do NOT silently pick a stack. Run the mobile disambiguation and decision tree — full detail in `bootstrap/RED-FLAGS.md` "Mobile Disambiguation" section. Three distinct choices: responsive web (cheapest), PWA (installable web + offline), native (App Store + native device APIs). Default for "I don't know" = responsive.

**Mobile decision tree — pattern:**
- If user names a native-only capability (the OS health-data store, haptics, biometrics, Bluetooth peripherals, deep OS integration) → native.
- If user wants installability + offline but no native-device APIs → PWA.
- If user just wants the site to work on phones → responsive.
- If ambiguous → ask explicitly. Do not guess.
