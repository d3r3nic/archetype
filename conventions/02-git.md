# Convention #2: Git & Version Control

## Applies when

Every project. What varies: one contributor or several, whether a push to some branch deploys or releases, how work reaches the main line, and whether two assistants take turns (development/PEER-CODING.md).

## Principle

History is the project's recovery point and its record. Every change is committed with what changed and why. Work in progress is committed and pushed at checkpoints, so nothing finished lives only on one machine. The main line receives only work that passes the project's checks. Shared history is never rewritten.

## Reusable System

References.md records the commit message convention, the branch model, where the project's checks run before work reaches the main line (a hook, a pipeline, both, or none with the reason), and what a push to each branch triggers, naming any push that deploys or releases.

## Rules

- Commit each coherent change with a message that says what changed and why. Keep unrelated changes in separate commits.
- Commit work in progress at checkpoints and push it to its own branch. A checkpoint commit on a working branch may still fail a check; the main line never receives one that does.
- Merge into the main line only what passes the project's recorded checks.
- Never commit secrets, credentials or environment files.
- Never rewrite history that others have: no force push to a shared branch, no amending or rebasing commits others build on.
- Never bypass a failing check to get a commit or merge through. Fix the cause, or set the check aside openly through the route in AGENTS.md; a skipped hook or a disabled check is neither.
- Fix code in place. Keep no second copy of a file or function beside the first, except a recorded, temporary migration of a shared interface (#19) that ends by removing the old one.
- Know what a push triggers. A push that deploys, releases or reaches people follows the owner's authority (#29).

## Violations

- One commit mixing unrelated changes under a message like "update code".
- Finished work left uncommitted or only on a local machine.
- A failing change merged into the main line.
- Secrets, credentials or environment files in history.
- A force push over commits someone else has.
- A hook skipped or a check disabled to get a commit through.
- A second version of a file kept beside the first with no migration that removes it.

## Wrong vs Right

- WRONG: one commit of 800 changed lines titled "changes". RIGHT: small commits, each saying what and why, each a point to return to.
- WRONG: a hook fails, so the commit skips it. RIGHT: fix what the hook found, or record why it is set aside, then commit.
- WRONG: a function is broken, so a fixed copy is added beside it and both stay. RIGHT: fix the function where it lives; one source of truth.
- WRONG: a long task ends for the day with its work only in the working folder. RIGHT: commit and push the work in progress to its branch.

## Research Notes

Research the commit and branch conventions the team or ecosystem already uses, and the tooling that runs the project's checks before a commit or a merge in the chosen stack. Record the choices in References.md, including which pushes deploy.
