# Convention #25: Automated Enforcement

## Applies when

Every project with recorded rules that code can break. What varies: the stack's checking tools, where checks run (#15), and how many people and sessions work on the code.

## Principle

A rule that a machine can check reliably is checked by a machine, not left to memory. Automate the checks whose reliability and prevention value justify their cost: the formatter, lint rules, type checks, and the project's § Boundaries lines, which `scripts/validate-develop.sh` enforces. A check that fails blocks; a warning that nobody acts on is noise, so it becomes a failure or it goes. What no script can judge stays with review and evidence.

## Reusable System

The project's enforcement set, configured once for the whole project: which recorded contracts are checked automatically and by what, where each check runs, and which rules remain review-only. References.md records the set and the gap list, the rules that rely on review alone.

## Rules

- Automate checks for real recurring risks and for the project's recorded contracts. A rule that can be written as a heuristic is not thereby accurate or worth keeping.
- Record each one-owner rule as a § Boundaries line, so the check enforces it and nobody has to remember it.
- Make each check fail or remove it. Warnings that pile up teach everyone to ignore checks.
- Keep checks that run before each commit fast enough that nobody is tempted to skip them; slower checks run before merge.
- Never bypass a check to get work through. Fix the cause, or set the check aside openly through the route in AGENTS.md.
- A suppression carries its reason on the same line, and the project watches whether suppressions grow.
- When review finds a defect, choose the prevention that fits: a test, a check, clearer guidance or a design change. Add a custom rule only when it can detect the condition reliably at a justified cost.
- A passing check proves only what it exercised. Verify the intended behavior and review what no check covers.

## Violations

- A rule the project relies on that exists only in prose while a check could enforce it.
- A check that warns forever and blocks nothing.
- Style argued in review that a formatter would settle.
- A check skipped to get a commit through.
- Suppressions with no stated reason.

## Wrong vs Right

- WRONG: "remember to call the service through the API client" is written in the docs, and features keep calling the network directly. RIGHT: a § Boundaries line says the network may be used only in the client's folder, and the check fails the first feature that goes around it.
- WRONG: naming is debated in every review. RIGHT: the linter enforces the naming rules, and review looks at logic and design.
- WRONG: suppressions accumulate with no context. RIGHT: each one says why, and growth is visible.

## Research Notes

Research the chosen stack's linter, formatter, type checker and their custom-rule support, the options for running checks before commit and before merge, and which of the project's recorded rules can be enforced reliably and which stay review-only. Record the enforcement set, where it runs, how to add a rule, and the gap list in References.md.

## Project Overrides

If a file exists at conventions/overrides/25-automated-enforcement.md, read it. It holds this project's own rules for this concern: the detail it adds, and where it departs from this convention and why. Where the two differ, the recorded project choice governs, within the owner's decisions, the floor and the obligations the project's facts add (#30).
