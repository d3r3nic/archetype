# Project Profile

How careful this project must be, and who decides technical questions. Every session reads this with References.md; `scripts/validate-profile.sh` reads it too. The facts block below runs up to the first `##` heading: one line per fact, `- Key: value`, each key exactly once. `unknown` is a real value: not yet learned, never "no". Update a fact when it changes; the operating stage follows the facts, not the other way round (convention #30). Decision authority is convention #29. A budget line records what the owner authorized; it grants no spending authority by itself.

- Schema: 1
- Operating stage: [isolated / trial / operational]
- Stage reason: [one line: which facts put it here]
- Decision authority: [owner-decides / ai-decides]
- Authority source: [owner-stated / defaulted]
- Audience: [owner-only / identified-participants / public / unknown]
- Data: [synthetic-disposable / real-nonpersonal / personal / unknown]
- External effects: [none / unknown / any of: money, messages, records, health-safety-access]
- Operational reliance: [yes / no / unknown]
- Valuable records: [yes / no / unknown]
- Fallback: [yes / no / unknown]
- Contributors: [one / several / unknown]
- Regulated data: [yes / no / unknown]
- Customer commitments: [yes / no / unknown]
- Monthly running-cost ceiling: [amount and currency the owner authorized, or unknown]
- AI spend envelope: [what the owner authorized for AI usage, or unknown]
- Observed-on: [YYYY-MM-DD the facts were last confirmed with the owner]
- Review: [YYYY-MM-DD, or the first trigger expected: first-outside-participant, public-access, real-data, personal-data, real-money-or-external-action, operational-reliance, valuable-records, second-contributor, regulated-data-or-commitment, trial-stage, operational-stage]

## How the operating stage is derived

- `isolated`: only the owner uses it, the data is made up and disposable, nothing has a real external effect, nobody depends on it, no valuable records, no commitments.
- `trial`: identified people try it and have a workable fallback if it fails; not public, not relied upon.
- `operational`: people depend on the result, the records, the availability, or real transactions. Also the reading when this file is missing.

Personal data, money, safety consequences, legal duties, and customer commitments add obligations at any stage. A second contributor adds collaboration obligations without requiring enterprise infrastructure. Regulated data is real data: it cannot sit next to `Data: synthetic-disposable`.

## Who decides

`owner-decides`: technical plans and foundational changes wait for the owner's approval (#19). `ai-decides`: the AI decides, records each decision with its reason, and escalates only the categories in #29. `Authority source` says where the setting came from: `owner-stated` when the owner said so, `defaulted` when a vague answer was resolved by the default. Moving from `owner-decides` to `ai-decides` needs an owner statement, recorded in the change log below.

## The floor (never deferred)

Whenever the protected asset or the hazardous capability exists: secrets and environment protection; validation of untrusted input at every boundary, public endpoints included, and authorization wherever access is restricted; safe irreversible effects (recovery, confirmation, reconciliation, or duplicate prevention as appropriate); responsible personal-data handling before collection, deletion and export procedure included; authorized reuse of code, assets, and data; honest completion and independent review wherever a merge path exists. What the project owes is the union of this floor, the stage's baseline, the requirements its facts add, and its commitments. A capability the project lacks is recorded as justified non-applicability, never as a deferral.

## Deferrals

Live in TECHNICAL-DEBT.md as entries with `Kind: deferral`, a `Control`, a `Due-before` trigger or date, a `Review-by` date, and `Closure-evidence`. A trigger the facts above make true turns its deferrals blocking; renewing a date, relabeling the stage, or won't-fix does not clear it. Before any action that changes exposure (inviting a user, importing real data, enabling payments, publishing), refresh the facts and run `scripts/validate-profile.sh --strict`.

## Change log

Append one line per change to the operating stage or the decision-authority setting: date, old value, new value, reason, and who said so. Downgrading the stage needs a reason here and a review of every surviving deferral.
