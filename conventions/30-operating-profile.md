# Convention #30: Operating Profile & Deferral

## Applies when

Every project. The facts it records (who uses the product, what data it holds, what it can do in the world, who depends on it) decide how the other conventions apply: the same rule can be deferred in a private experiment and owed at once in a product people rely on.

## Principle

How careful a project must be follows from facts, not from a label and not from its age. Who uses it, whether the data is real and about people, whether it can move money or affect someone's health or access, whether anyone depends on it or on its records, what was promised: these set the obligations. A disposable experiment may postpone much of what an operational product owes, but it records every postponement with the trigger that ends it, and a short list of obligations is never postponed at all. The profile is a record the AI derives and keeps current, never a permission slip, and a project label cannot remove an obligation that arises from actual use.

## Reusable System

- `PROFILE.md` at the repository root: the operating stage, the facts that set it, the decision-authority setting with its source (#29), cost ceilings, the date the facts were last confirmed, and a review condition. The facts block is one `- Key: value` line per fact, each key exactly once, up to the first `##` heading; the parse contract is the one References.md uses. `unknown` is a real value and is never read as "no". The template is templates/profile.md. A fullstack repository has one profile; a product spread over several repositories carries the same facts in each, and the owner channel keeps them aligned.
- Deferrals in `TECHNICAL-DEBT.md` (templates/technical-debt.md): entries with `Kind: deferral`, the `Control` they postpone and the `Due-before` trigger or date that ends the postponement, and where useful a `Review-by` date and the `Closure-evidence` that will close it. One log for shortcuts and deferrals, so nothing is tracked twice.
- `scripts/validate-profile.sh`: reads both files and reports, per check, OK, FAIL, WARN, DEFERRED, or UNVERIFIED, and says whether the profile was declared or missing. `--strict` turns every UNVERIFIED result into an error; run it that way before any action that changes exposure and in maintenance of operational projects.

## Stages

- `isolated`: a private experiment. Only the owner uses it, the data is made up and disposable, nothing it does has a real external effect, nobody depends on it or on its records, nothing was promised.
- `trial`: a controlled evaluation. Identified people use it and have a workable fallback if it fails; it is not public and not relied upon.
- `operational`: people depend on the result, the records, the availability, or real transactions. An internal tool can be operational. This is also how a missing profile is read.

The AI derives the stage from the facts at bootstrap and whenever a fact changes. Personal data, money, safety consequences, legal duties, and customer commitments add obligations at any stage. A second contributor adds collaboration obligations without requiring enterprise infrastructure. Regulated data is real data: it cannot sit next to synthetic-only data.

## The facts

Audience (owner-only, identified-participants, public); data (synthetic-disposable, real-nonpersonal, personal); external effects (none, or any of money, messages, records, health-safety-access); operational reliance; valuable records; fallback; contributors (one, several); regulated data; customer commitments; the monthly running-cost ceiling and the AI spend envelope the owner authorized; the decision authority and its source; the date the facts were last confirmed; and a review condition, a date or the first trigger expected. Every yes-or-no fact may be `unknown`. A budget line records an authorization the owner gave; it grants no spending authority by itself (#29).

## The floor

Never deferred, at any stage, whenever the protected asset or the hazardous capability exists:

- Secrets and environment protection: credentials out of source, logs, and public artifacts; least privilege; experiments separated from live systems.
- Trust-boundary protection: untrusted input validated at every boundary, public endpoints included; identity and resource authorization enforced wherever access is restricted. A public information page needs no invented login.
- Safe irreversible effects: valuable records and external actions protected by recovery, confirmation, reconciliation, or duplicate prevention, whichever fits. Disposable synthetic data may be reset; irreplaceable user data may not be silently lost.
- Responsible personal-data handling before collection: purpose, access, retention, and the applicable deletion and export procedure established first, retention exceptions respected. A verified manual procedure can suffice where obligations and volume permit.
- Authorized reuse: rights to the code, assets, and data in use verified, notices preserved. Public availability is not a license.
- Honest completion and review: shipped behavior verified, required checks kept passing, independent audit before merge wherever a merge path exists. A stage cannot relabel a failing test, a known unsafe behavior, or a placeholder as acceptable completion (#29).

What a project owes is the union of this floor, its stage's baseline, the requirements its facts add, and its existing commitments. The floor is not an exhaustive checklist. A capability the project does not have (no merge path, no deployment) is recorded as justified non-applicability where it applies, never as a deferral.

## Rules

- Every fact in PROFILE.md is `yes`, `no`, a listed value, or `unknown`. A vague answer is recorded as `unknown`. For audience, effects, reliance, and records, `unknown` blocks real exposure and leaves the contained experiment open; the regulated-data question keeps its stricter gate from bootstrap, which halts scaffolding and deployment until it is answered.
- The stage agrees with the facts. An `isolated` project has no outside users, no real data, no real external effects, no operational reliance, no valuable records, and no customer commitments. A `trial` is not public, is not relied upon, and has a fallback not recorded as `no`. Regulated data with synthetic-only data is a contradiction. Each is a validator failure, not a judgment call.
- Every deferral names the control it postpones and the trigger or date that ends it. "Later" without an entry is a loose end.
- Triggers are named and evaluated from the recorded facts: `first-outside-participant`, `public-access`, `real-data`, `personal-data`, `real-money-or-external-action`, `operational-reliance`, `valuable-records`, `second-contributor`, `regulated-data-or-commitment`, `trial-stage`, `operational-stage`. A date deadline is inclusive. A trigger the facts make true turns every deferral due before it blocking until fixed. Renewing the review date, relabeling the stage, or marking won't-fix does not clear it.
- A trigger that rests on an `unknown` fact is unverified: the validator says so, strict mode fails on it, and learning the fact is the next task, not a footnote.
- A deferral with no profile to evaluate it is a failure, so a project cannot sidestep its deferrals by never writing PROFILE.md.
- Downgrading a stage requires a recorded reason in the profile's change log and a review of every deferral that survives it. Exposure that still exists forbids the downgrade.
- Insufficient budget changes scope or sequencing, never the floor.
- Re-read PROFILE.md at the start of each session and before any action that changes exposure (inviting a user, importing real data, enabling payments, publishing). Refresh the facts first, run the validator in strict mode, and let the action follow the refreshed profile.

## What the validator cannot see

It reads declarations and checks their consistency. It does not observe users, data, or money; it cannot tell whether a stated fact is true; it has no memory of earlier profiles, so a downgrade that also rewrites the facts is caught by review, not by the script; it knows a deferral is a floor item only when the entry labels the control as one, so whether a postponed piece of a security convention was rate limiting (deferrable) or input validation (floor) is a judgment the independent audit makes; and it stands at no action boundary. It reads each field in the common written forms (a list item or a plain line, the label bold or not, the value after the colon); an entry it cannot read, such as a deferral whose trigger it cannot find, is reported as unverified, which strict mode fails, never as a pass. The review reads what it cannot. The playbooks name where to run it. Nothing here claims automatic prevention.

## Violations

- A stage chosen by the owner or by the AI's taste instead of derived from the facts
- `unknown` treated as `no`
- A floor item logged as a deferral, or a floor item hidden inside a deferral labeled with a convention number
- A deferral whose trigger has fired, kept open by a renewed date, a won't-fix, or a quieter stage label
- Real users, real data, or real money reaching an `isolated` project
- A validator result read as "production-ready" when it means "this action is permitted under the recorded facts"
- A missing PROFILE.md read as "no obligations" instead of as the strictest stage
- A budget line read as permission to spend

## Wrong vs Right

- WRONG: "It's just a POC, skip auth." RIGHT: "Isolated stage: only you, made-up data. Authorization where access is restricted stays, because the floor applies whenever the asset exists; rate limiting and the operational dashboard are deferred until the first outside participant, recorded as TD entries with that trigger."
- WRONG: the first customer is invited and the session starts on their feature request. RIGHT: the session refreshes PROFILE.md first, the audience becomes identified participants, the deferrals due before that trigger become blocking, and they are done before the invitation goes out.
- WRONG: "Operating stage: isolated" while the profile also says the data is personal. RIGHT: the validator fails the contradiction; the facts win, the stage moves to trial or operational, and the personal-data obligations apply now.
- WRONG: the project never creates PROFILE.md and its deferrals sit unevaluated. RIGHT: the validator warns about the missing profile, fails every deferral it cannot evaluate, and reads the strictest stage until the file exists.
- WRONG: a deferral labeled "#23" that postpones input validation. RIGHT: input validation is a floor item and is built now; the entry's control names what is really postponed, so the audit can see it.

## Research Notes

At bootstrap, derive the stage from the discovery answers and write PROFILE.md before generating anything else that depends on it. Research the regulatory regime only when a fact calls for it (regulated data, customer commitments), and record the finding in References.md with its date. Standards bodies publish control baselines and secure-development practices graded by risk; read the current ones when the project's facts put it above `isolated`, and record which one the project follows. The stage names and triggers here are the framework's own vocabulary; they map to no external certification and claim none.
