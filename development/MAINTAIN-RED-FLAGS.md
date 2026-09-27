# Maintain Red Flags — Phase 4 Silent-Failure Patterns

Routed from `development/MAINTAIN.md`. Parallels `bootstrap/RED-FLAGS.md`, `scaffolding/RED-FLAGS.md` and `development/RED-FLAGS.md`. These are the ways a project's records drift while everything still seems to work.

Silent failure in maintenance has no failing test or broken build to surface it. The project keeps working; the drift compounds; later features built on a false map inherit it.

## 1. Looked at once, then forgotten

A session checks the map and the debt once and moves on. Months later nobody has looked again: the debt log is stale, the map has drifted, and the records describe code that no longer exists.

**Defense:** MAINTAIN.md ties each look to a change: a framework update, a changed feature or system, a changed fact in PROFILE.md, an incident, a repeated review finding. `scripts/validate-maintain.sh` checks the map against the project whenever it runs; the judgment the script cannot make is the session's.

## 2. The debt log grows forever

Entries accumulate and none is ever fixed, raised or closed. The log becomes a list of someday-maybes that nobody reads.

**Defense:** MAINTAIN.md's debt rule: an entry that sits unchanged through several looks gets a decision (fix, raise, or close as won't-fix with the reason), and deferrals follow their triggers (#30), which `scripts/validate-profile.sh` enforces.

## 3. A lesson captured in a session review but never promoted

A session review records a finding ("we keep hitting this; the guidance should cover it", or "this guidance got in the way"). Nobody reads the review again, and the next project hits the same thing.

**Defense:** MAINTAIN.md's convention evolution:
- After each session review, read its "Suggested Convention Improvements" and "Where did the framework get in the way?".
- Report what other projects would meet upstream (development/FEEDBACK.md), written out in the report itself; the framework's repository is public, and a link to a project file shows nothing.
- The framework's maintainers gather reports across projects: the ones that ask to remove or soften guidance as much as the ones that ask to add it.
- The loop closes when an update brings the change and a later session review confirms it.

The feedback loop is the point. A session review with no way upstream is only a journal.

## 4. Records drift from the code

A feature's code changes and its record does not. Both "work"; a later session reads the record, builds against the shape it describes, and meets a different one at run time. No shipped hook checks record content.

**Defense:**
- `validate-develop.sh` catches the coarse case: a feature row whose record or tests are missing.
- `validate-maintain.sh` compares the map with the project, and warns when a record names a type its feature no longer defines.
- Whether a record's narrative is still true is the session's to check when the feature changes (MAINTAIN.md, Keeping documents current).

## 5. Two checks disagreeing on the same project

Two checks that cover the same concern with different logic give different answers, and neither can be trusted while the other contradicts it.

**Defense:** each concern has one check (#0). MAINTAIN.md carries no check of its own; it routes to the scripts, and shared logic lives in one of them.

---

## Handling a fired red flag

1. Log the finding in TECHNICAL-DEBT.md if it is not fixed now.
2. Fix it at its source. Change a check only when the check itself is wrong, and say so.
3. Re-run the relevant check.
4. When other projects would meet it too, report it upstream (development/FEEDBACK.md).
