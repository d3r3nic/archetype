# What changed

Each framework release, newest first. Its lines say:
- Session: what the session now does differently;
- Project: what an installed project records once;
- Reopen: which steps a project that already did them reopens and does again;
- Audit: which of the project's files to check against a changed rule or template.

So a project catches up without running its setup again. The updater prints the entries a project has not seen, and development/UPDATE.md, section After, says how to act on them.

An entry's `Follows` line names the release before it. The entries a project has not seen run from the top down to the one that follows the revision it had installed, which VERSION-LOG.md records. An install older than the last entry here reads them all; the rules and guides it now has state everything earlier.

## 2026-09-28: Every update says what to redo
Follows: d447f226b09d1c9e3eb71587fcd00bb87a68eeb0

- **Session:** each entry now also says which steps a project that already did them reopens and does again (Reopen), and which of its files to check against a changed rule or template (Audit). Act on them as development/UPDATE.md, section After, says.
- **Project:** once, because this release added Reopen and Audit lines to earlier entries, which a project already past them is never shown. Read development/CHANGES.md from this entry down to the entry whose `Follows` line names the revision on the first `Commit:` line of VERSION-LOG.md, or to the end when none does, and do the Project, Reopen and Audit lines this project has not done.
- **Reopen:** none.
- **Audit:** none.

## 2026-09-27: Peer coding stays on the goal
Follows: 60dee6353653fff781ae4815fe8f91eb21fe87d3

- **Session:** in peer coding, weigh every review finding against the branch's goal. A blocking finding is a real problem in what the branch changed, drift outside the agreed scope or against the owner's recorded words (#19) and a floor item of the operating profile (#30) left unmet among them, or one that stops its goal; only blocking findings are repaired in the branch, and only they hold back acceptance. Everything else is debt: one FINDINGS.md row with Severity `debt`, not worked on in the branch (development/PEER-CODING.md, Stay on the goal).
- **Session:** at every turn, before each change, check that it serves the goal or repairs a blocking finding, and write anything else down as debt instead. The packet's Goal check says how the turn served the goal and what went to debt.
- **Session:** when a branch closes for its merge, carry the debt rows to the project's records: the task source, or TECHNICAL-DEBT.md as `Kind: shortcut` entries. Carried entries are reviewed like any product change, and that review checks only that the range appends them to the log and changes nothing else, and that each records its row. Before an abandoned close, rows about the abandoned change go with it, and the others go to the task source or to the owner.
- **Project:** in a branch folder already open, mark each FINDINGS.md row's Severity `blocking` or `debt` at your next turn.
- **Reopen:** none.
- **Audit:** none.

## 2026-09-27: Hand-over commits stay plain
Follows: 8577abdf3bcb466a4d687a850a57077a9152b153

- **Session:** in peer coding, every hand-over commits the record, plainly, and pushes when the settings say `Push: yes`; product work is committed on the writing turn as it goes.
- **Session:** keep each commit plain: a one-line message and your Peer line, plus only what the project's commit convention requires. Do not reshape the turn's history at a hand-over or write long message bodies, since the packet carries the detail (development/PEER-CODING.md).
- **Project:** nothing to record.
- **Reopen:** none.
- **Audit:** none.

## 2026-09-27: Every update says what changed
Follows: 08bcc1404be21a0f67321fe0f1ff6889ca5e571c

- **Session:** after an update, act on the entries of this file the project has not seen. The updater prints them; after an updater from before this file, development/UPDATE.md, section After, says how to find them. Change how you work as each Session line says, and do what each Project line asks.
- **Project:** nothing to record.
- **Reopen:** none.
- **Audit:** none.

## 2026-09-26: Guidance and checks by how the application works
Follows: f6b13b40b87298e9ebaea9dd8b5d182c130dedf3

- **Session:** each convention says when it applies, by how the application works, and holds its standard firm:
  - build once and reuse, with separation as the recorded exception;
  - one owner per concern, and no duplicated logic or components;
  - safe boundaries, and correct, consistent API contracts;
  - no bloat, and speed and cost sized to real usage.

  Where a rule applies, choose the form, record it in the project's files, and let the checks enforce the record.
- **Session:** the framework names no technology. Choose the stack from the use case and record it in the project's files.
- **Project:** add a `## Boundaries` section to References.md.
  - It holds each shared system's one owner and what only it may use, one line per concern: `` - <concern>: `<pattern>` only in `<path>`, `<path>` ``. Copy the section's explanation from the matching References template in `templates/`.
  - `scripts/validate-develop.sh` requires it. Record `- none: <reason>` when the project has nothing to guard.
  - Record the lines from how the code already works, and treat a place that already goes around an owner as a finding to fix.
- **Project:** add a `Checks run:` line saying where the checks run before work reaches the main line; the scaffold check warns without it.
- **Project:** a migration command recorded as `migrate:` (or `db:migrate:`, as an earlier backend template had it) in § Commands is bounded to its production path in § Boundaries.
- **Project:** a feature record may carry a `Tests:` line naming its tests. Without one, the develop check looks for test files in the feature's location as before.
- **Reopen:** none.
- **Audit:** References.md against the current References template for the project's kind (templates/references-<kind>.md): bring in each section and line it lacks, recorded from how the code already works. For a frontend that includes the state responsibilities (scaffold-frontend step 5) and the checks, budgets, build and rollback path (step 11). A decision the code does not show is made as PROFILE.md's decision authority says, then recorded.
- **Audit:** feature-tree.md: a foundational-system row still `not started` for a system the project's facts do not call for (each convention's Applies when) came from the older template's fixed list; remove it.
- **Audit:** the test setup of a web front end or device app (scaffold-frontend steps 8 and 10, scaffolding/RED-FLAGS.md section 14): tests render through the app's own root composition, reused, not a copy of its order. Where they copy it, make both use the one composition.

## 2026-09-26: The session's final word, and the force-push guard
Follows: e72ed261e0358e490c979ef87bda81c9ffb164f6

- **Session:** the framework's guidance, steps and checks are reminders; the session has the final word on fit, within the decision authority in PROFILE.md.
  - When one does not fit how this application works, set it aside and record what, why and what you did instead. For a step, use `scripts/next-step.sh --set-aside` (development/STEPS.md).
  - Report it upstream when it would get in the way of other projects (development/FEEDBACK.md). The owner approves before anything is sent.
  - A set-aside is never a pass. It never covers the owner's decisions, the floor (#30) or honesty, and a step that holds the owner's words is set aside only with them.
- **Session:** the destructive-command guard blocks every force-push form it names and lets `--force-with-lease` through; use that form when a force push is needed.
- **Session:** when the guard blocks a command, never reword it to get past the guard. Use the safer form its message names, or ask the owner (bootstrap/hooks/README.md).
- **Project:** nothing to record.
- **Reopen:** none.
- **Audit:** none.

## 2026-09-25: Text read the same on every system
Follows: 2b9e92f4bf81583cb4a3a94fe5799bac806ac48d

- **Session:** the checks read text as bytes and give the same answer on every system, and a parser that stops early fails instead of passing. Nothing changes in how you work.
- **Project:** nothing to record.
- **Reopen:** none.
- **Audit:** none.

## 2026-09-25: Every peer turn committed as it moves, every commit names its assistant
Follows: 486c95237eb3ec51d1591281483986bbe8dd53f2

- **Session:** in peer coding (development/PEER-CODING.md):
  - commit as the turn moves, and push at each checkpoint when the settings say `Push: yes`;
  - leave nothing uncommitted however a turn ends;
  - every commit on a peer branch names its assistant with a `Peer:` line.
- **Project:** `Push: no` in `peer-coding/SETTINGS.md` needs its reason: a push to a work branch would itself start a deploy or release build, or the project has no remote. `scripts/peer-coding.py` refuses a bare `Push: no`; otherwise set `Push: yes`.
- **Project:** for a peer-coding branch opened under an earlier release whose pushed commits carry no `Peer:` line, the next hand-over's packet names each one: `Commit <id> made by <name>`. `scripts/peer-coding.py check` lists them.
- **Reopen:** none.
- **Audit:** none.

## 2026-09-25: Peer coding, two AI assistants taking turns on a branch
Follows: fb03dacf255c5e7371dc0837b44bd1e6802d0102

- **Session:** two AI assistants can take alternating turns on a branch, each reviewing the other's work (development/PEER-CODING.md). A project's own settings live in `peer-coding/SETTINGS.md`.
- **Project:** when References.md § Project has no `Peer coding` line:
  - ask the owner the two peer-coding questions of bootstrap/ONBOARD-2.6-CARE-AND-AUTHORITY.md;
  - record `none`, or set peer coding up (development/PEER-CODING.md, Setting it up);
  - until the owner answers, record `none (asked, awaiting the owner)`. The bootstrap checks the step runner repeats read this line, and other work continues.
- **Project:** a `peer-coding/` folder that holds `README.md`, `PROTOCOL.md` or `templates/` from an earlier copy of the peer-coding rules: remove them in a change of their own, keeping every branch folder. `scripts/peer-coding.py check` names them.
- **Reopen:** none.
- **Audit:** none.

## 2026-09-24: Honest checks, a working guard, a log that survives updates
Follows: 1538b8c28d9bced68266c3c87fe2d84bbd804739

- **Session:** References.md § Commands holds each command in backticks. The step runner refuses an unmarked value and says how to write it.
- **Project:** write each recorded command in backticks.
- **Project:** a project that installed the framework's hook guard runs `scripts/check-hooks.py`. It names:
  - a guard command that no longer starts (quote its path placeholder as the settings templates do);
  - a registration of the retired turn-end reminder (remove it);
  - a settings file git ignores.

  Change only those entries of the project's settings.
- **Project:** a unit that handles regulated data records where its audit trail lives on the Audit log line of References.md § Compliance; the scaffold check reads it there.
- **Project:** a frontend project records how people use it on a phone on the `Mobile mode` line of References.md § Project (templates/references-frontend.md); the frontend scaffold reads it.
- **Reopen:** none.
- **Audit:** PROGRESS.md: a closed `bootstrap.3` whose evidence is only that no objection came by a stated time. Ask the owner to authorize the build approach (#29), and record their words at the decision location.

## 2026-09-23: Fixes a fresh project meets on day one; rules load by import
Follows: cefbec9d9ebac48bc3edbce3fc70a6e779856b02

- **Session:** root CLAUDE.md imports AGENTS.md, so the rules load under either name.
- **Session:** work blocked on the owner is recorded as blocked, with the owner's action (#29), never as a deferral.
- **Project:** remove any feature-tree.md row that still holds the template's placeholder; the checks fail it.
- **Project:** a pulse monitor built under an earlier release keeps its snapshot and UI outside every folder the production build or deployment copies. Its route is registered only when the environment explicitly says development (#26, templates/pulse-monitor-spec.md). Move them, then list the production build's files, hidden ones included, to confirm neither is there.
- **Reopen:** none.
- **Audit:** TECHNICAL-DEBT.md: a deferral whose work waits only on the owner's authorization is a block (#29). Record it as #29 says, with the reason for the change at the decision location; a deferral the operating stage allows (#30) stays.

## 2026-09-21: Updates carry a project's own rules forward; AGENTS.md holds the rules
Follows: cf15e2117af1733b2360470fe2458bc4af6b4385

- **Session:** root AGENTS.md holds the framework's rules and is replaced by every update. The project's own rules live in CLAUDE.md.additions, which AGENTS.md sends every session to first.
  - Never put a project rule in a root entry file.
  - Never restore a root entry file from version control after an update.
- **Project:** review what the update carried into CLAUDE.md.additions (development/UPDATE.md, section After).
- **Reopen:** none.
- **Audit:** none.
