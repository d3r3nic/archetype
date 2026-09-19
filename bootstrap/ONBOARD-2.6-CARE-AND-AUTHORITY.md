# Bootstrap: discovery, group 6

Part of the bootstrap playbook (bootstrap/ONBOARD.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step: read it when the script names it, with the reading it lists, and close it before opening the next.

## Step 2.6: Group 6 - How careful, and who decides
Read: bootstrap/ONBOARD-DISCOVERY.md; bootstrap/RED-FLAGS.md § Discovery Turn Budget; #30; #29
Produces: the facts PROFILE.md holds, the operating stage derived from them with its reason, the owner channel, and who decides technical questions
Check: evidence: the owner's answers to this group in their own words, quoted; a question an earlier answer settled is recorded as inferred, with the inference; a question the owner declined is recorded as declined, with what was assumed

This group fills PROFILE.md per #30 and the decision-authority setting per #29; ask only what Groups 1-5 did not already answer.

- What should this first version prove, or let someone accomplish?
- Will it work with made-up information, or real information? If real, is any of it about people (names, contact details, health, money)?
- Would anything be lost for good if its records disappeared?
- Could it move money, send messages, change important records, or affect someone's health, safety, work, or access to a service?
- If it stopped working or gave a wrong answer, what would happen? Could people use another way meanwhile?
- Are we testing an idea we might throw away, or preparing something people will depend on? Is there a promised date?
- What have you promised the people involved about privacy, reliability, or the handling of their information?
- What monthly running cost is comfortable, and how much extra AI spending? (Reuse the budget answer if already given.)
- Who else will work on the code with me, now or soon? (Just you and me, or other people too?)
- When a question needs you, where should I send it, and how quickly can you usually answer? (Fills `Owner channel` in References.md.)
- Do you want to make the technical choices yourself, or should I make them and show you what I decided and why?

The AI derives the operating stage from the answers (#30): `isolated` when only the owner uses it, with made-up data, no real effects, nobody depending on it or on its records; `trial` when identified people try it and have a workable fallback; `operational` otherwise. A vague answer stays `unknown` in PROFILE.md and is never read as "no". For audience, effects, reliance, and records, `unknown` blocks real exposure, not the contained experiment; the regulated-data question keeps its own stricter gate (`bootstrap/RED-FLAGS.md` "Deploy Gate"), which halts scaffolding and deployment until it is answered. When the regulated-data answer is vague, PROFILE.md records `Regulated data: unknown`; the default-assumed-yes lives in VERSION-LOG.md as the open pre-production gate, not in the profile. A vague answer to the last question records `Decision authority: ai-decides` with `Authority source: defaulted` (#29); see `bootstrap/RED-FLAGS.md` "Vague answer about who decides".
