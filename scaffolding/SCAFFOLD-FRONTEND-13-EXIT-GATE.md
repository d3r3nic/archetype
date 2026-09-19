# Frontend scaffold: the exit gate

Part of the frontend scaffold playbook (scaffolding/SCAFFOLD-FRONTEND.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step. Before building, read the conventions it names and write how the system will be built in its References.md section (scaffolding/_preamble.md); when it lands, update its feature-tree.md row and its docs/systems/ page.

## Step 13: Exit gate and the scaffold record
Read: scaffolding/SCAFFOLD.md § Post-scaffold required outputs; scaffolding/SCAFFOLD.md § VERSION-LOG Scaffold entry template; scaffolding/RED-FLAGS.md § 2. Checklist-only verification (no execution)
Produces: every system marked in feature-tree.md with its real location or its deferral, a docs/systems/ page per system, References.md updated, and the scaffold entry in VERSION-LOG.md
Check: run scripts/validate-scaffold.sh

Run `scripts/validate-scaffold.sh`. Fix any failures before committing.

### What the scaffold leaves written

Same as SCAFFOLD-BACKEND: every applicable system marked implemented with path, or `deferred (TD-N)` with its trigger per #30, docs/systems/ entry per system (a deferred system's page says what is deferred and until when), References.md updated, `.env.example`, VERSION-LOG entry, initial commit.
