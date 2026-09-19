# Bootstrap: how discovery is asked

Read with every discovery step (2.1 to 2.6 of the bootstrap playbook, bootstrap/ONBOARD.md). It is not a step itself: it says how the questions are put, and what compression under an impatient owner may and may not change.

Do NOT jump straight to building. The AI needs to understand what you're building first. The owner starts it with the message below; the session then walks the discovery steps, one question group each.

## What the owner says to start

Give this to your AI assistant:

---

Read bootstrap/ONBOARD.md and bootstrap this project, one step at a time. Interview me before generating anything.

I want to build: [describe your idea in plain English, even one sentence is fine]

---

## Discovery Process

Before choosing any technology or generating any files, interview the user with these questions. Ask them one group at a time. These are designed for people who may not know technical terms. Skip any question an earlier answer already settled, and say what you inferred instead of asking it. When the owner pushes back on the number of questions, say how many rounds remain, state what you will assume, and compress the rest into one round. Compression changes how many messages the questions take, never which groups close: each group below is its own step, and it closes only on the owner's words for it, quoted, with each question marked answered, inferred (and from what), or declined (and what was assumed instead). A group cannot be skipped. The answers that feed a gate land on lines a script reads later: PROFILE.md's facts (`scripts/validate-profile.sh`) and, for a project with a screen, the `First task`, `Return tasks`, and `Session length` lines of References.md § Design Artifact (`scripts/validate-design.sh`).
