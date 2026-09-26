# Bootstrap: discovery, group 6

## Step 2.6: Group 6 - How careful, and who decides
Read: bootstrap/ONBOARD-DISCOVERY.md; bootstrap/RED-FLAGS.md § Discovery Turn Budget; #30; #29
Produces: the facts PROFILE.md holds, the operating stage derived from them with its reason, the owner channel, who decides technical questions, and whether a second AI assistant takes turns on the project and who writes new work
Check: evidence: the owner's answers to this group in their own words, quoted; a question an earlier answer settled is recorded as inferred, with the inference; a question the owner declined is recorded as declined, with what was assumed
Skip by: owner

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
- Will another AI assistant also work on this project, in its own chat, taking turns with me? At each hand-over you would pass one short line from one chat to the other. (A no records `Peer coding: none` in References.md; a yes sets up peer coding.)
- If so, which of us should write new work, and which should review it? Either of us can fix what a review finds and send it back for another review. Or should we take turns, or will you say each time? (Fills Who writes in the peer-coding settings, in the owner's words.)
- When a question needs you, where should I send it, and how quickly can you usually answer? (Fills `Owner channel` in References.md.)
- Do you want to make the technical choices yourself, or should I make them and show you what I decided and why?

The AI derives the operating stage from the answers (#30): `isolated` when only the owner uses it, with made-up data, no real effects, nobody depending on it or on its records; `trial` when identified people try it and have a workable fallback; `operational` otherwise. A vague answer stays `unknown` in PROFILE.md and is never read as "no". For audience, effects, reliance, and records, `unknown` blocks real exposure, not the contained experiment; the regulated-data question keeps its own stricter gate (`bootstrap/RED-FLAGS.md` "Deploy Gate"), which halts scaffolding and deployment until it is answered. When the regulated-data answer is vague, PROFILE.md records `Regulated data: unknown`; the default-assumed-yes lives in VERSION-LOG.md as the open pre-production gate, not in the profile. A second assistant reads the project's code and records, so it is the owner's choice, and PROFILE.md's regulated-data answer applies to it as to any service that sees the data; a vague answer records `Peer coding: none` until the owner asks for it (development/PEER-CODING.md, Setting it up). A vague answer to the last question records `Decision authority: ai-decides` with `Authority source: defaulted` (#29); see `bootstrap/RED-FLAGS.md` "Vague answer about who decides".
