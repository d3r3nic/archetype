# Bootstrap: discovery, group 2

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

If the user says "phone app" or "works on my phone," do not silently pick a stack. Use `bootstrap/RED-FLAGS.md` "Mobile Disambiguation" to identify the outcome they need: browser access, installation, offline behavior, notifications, app-store presence or device APIs. Step 3 researches the current approach after those requirements are known.

Record the requested capabilities without converting them into a build label here. Step 3 verifies which current approaches provide them and what each choice costs. If the outcome remains ambiguous, ask about the outcome rather than asking the owner to choose a technology label.
