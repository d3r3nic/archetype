# Convention #16: Documentation & Decisions

## Applies when

Every project. What varies: how many people and sessions read the records, how long the product lives, and whether the team already keeps decisions in a format of its own.

## Principle

Records hold what the code cannot say: intent, constraints, business reasons and the decisions behind the design, each in one place. Every consequential decision can be found with its reason, so "why did we choose this?" has an answer that does not depend on anyone's memory. Documentation that restates the code is noise, and documentation that has drifted from the code is worse.

## Reusable System

One decision location, named in References.md: the team's existing decision records when it has them, otherwise DECISIONS.md from templates/decisions.md. One feature record format, templates/feature-doc-template.md. Current facts live in one place each (References.md, feature-tree.md), and other records link to them.

## Rules

- Comment what a reader cannot recover from the code: a reason, a constraint, a business rule, a workaround and what it works around. Do not narrate what the code plainly does; unclear code is rewritten before it is explained.
- Explain every number that encodes a constraint: why this timeout, this limit, this batch size.
- Name things for what they mean. Use abbreviations only where the domain's readers all know them.
- Record each consequential decision once, at the decision location, with what was decided, why, the alternatives, and who decided it. Never keep a second decision store.
- Keep a record current when the behavior, contract or decision it describes changes. A routine edit that changes none of these needs no new record.
- A reminder left in code says what is missing and where it is tracked, so it can be found and closed.
- Keep explanations proportional to the decision and its risk.

## Decisions the step runner reads

A step that declares a decision basis (development/STEPS.md) fingerprints the decisions it cites. Such a decision sits under a `### DEC-NNN` heading and has a line for each of `Status:` (proposed, accepted, superseded or retired, in any case), `Decision:`, `Reason:` and `Authority:`, plus `Depends on:` and `Supersedes:` when it has them (decision IDs, or none). Only the cited decisions and those they depend on or are superseded by are read. The other fields in templates/decisions.md are the project's to use. A team whose own record format differs keeps it and cites its records to the step runner as `--input` files instead.

## Violations

- Comments that repeat the code line by line.
- A record that describes a previous version of the code.
- A constraint encoded as an unexplained number.
- A consequential decision that cannot be found, or that lives in two places that disagree.
- A reminder in code with nothing that tracks it.

## Wrong vs Right

- WRONG: "loop through each order" above a loop. RIGHT: one comment on the rule the code cannot show: "orders over the threshold get the partner discount under the current agreement", with where the agreement is recorded.
- WRONG: a timeout of three seconds with no explanation, raised to five because "bigger is safer". RIGHT: "the payment provider fails over after three seconds", so the next reader leaves it alone.
- WRONG: a long comment block on a function whose name and types already say everything. RIGHT: no comment.

## Documentation Formatting

Use the structure that helps the actual reader and any declared parser. The feature template is the single home for its format. Link to current facts instead of copying locations, shapes or commands into every document. Historical logs keep revision-specific snapshots and say they are history.

## Research Notes

Research the decision-record formats the team or ecosystem already uses, the stack's documentation tooling, and its naming conventions. Record the decision location, the templates in use and the naming rules in References.md.
