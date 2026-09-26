# Frontend scaffold: the exit gate

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 13: Exit gate and the scaffold record
Read: scaffolding/SCAFFOLD.md § Post-scaffold required outputs; scaffolding/SCAFFOLD.md § VERSION-LOG Scaffold entry template; scaffolding/RED-FLAGS.md § 2. Checklist-only verification (no execution)
Produces: every system marked in feature-tree.md with its real location or its deferral, a docs/systems/ page per system, References.md updated, and the scaffold entry in VERSION-LOG.md
Check: run scripts/validate-scaffold.sh --required known-screen
Depends on: scaffold-frontend.12; scaffold-frontend.11
Basis: decisions and inputs required
Skip by: owner

Run `scripts/validate-scaffold.sh --required known-screen`. Fix any failures before committing. The required mode refuses a missing or repeated Design Artifact section because this route is known to produce screens.

### What the scaffold leaves written

Same as SCAFFOLD-BACKEND: every applicable system marked implemented with path, `deferred (TD-N)` with its trigger per #30, or `blocked (owner: <action>)` per #29, docs/systems/ entry per system (a deferred system's page says what is deferred and until when), References.md updated with its § Boundaries lines, the example configuration file, VERSION-LOG entry, initial commit.

Use the same current decision basis and artifact/review inputs as the smoke-test step. Keep the decision record as the source of reasons and the review as the source of observations; the progress ledger holds references and check results.
