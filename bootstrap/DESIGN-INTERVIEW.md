# Design interview: a form with gates, and two ways through it

Routed from `bootstrap/ONBOARD.md`. It runs once for a product with a screen, at Step 4 of ONBOARD.md, after Step 3 has settled a custom build and Group 6 has given the operating stage, so nobody answers questions about the look of a product that turns out to need no custom screen. A template project skips it: templates decide no brand, and their downstream products run it at their own bootstrap. An existing product whose `Brand decided` line is not `yes` runs it with what the audit found already filled in.

The owner decides how the product looks (#29). This interview is how the AI learns enough to make that decision easy: either the owner picks from directions, or the owner says in words "choose what fits my business" and the AI picks for them. Both ways are always offered. The answers fill References.md § Design Artifact and the brand book (#27).

## Rules for asking

- A form, not an interrogation. The questions reach the owner as one page they fill in at their own pace, never as a chain of chat messages. Where the session can show a page (a design tool it has, or a static page opened from the design working-files folder), it starts from `templates/design-interview/` and removes or pre-fills what is already known. The session opens the page for the owner itself where it can: the host's preview or browser, or the operating system's open command. Where it cannot open it, it tells the owner exactly what to do, in numbered plain steps: where the file is and how to open it; fill in what you care about; press "Show my answers"; press "Copy answers" and paste them into the conversation, or press "Save answers as a file", put the file in the folder named, and say it is done. Never leave the owner to find or open a file on a hint. Where no page can be shown at all, or the page's scripts are blocked, it asks the same tree in conversation, one gate at a time, and stops at the first "you choose".
- Gates first. Every group opens with one question whose "no" answers the whole group. "Nothing exists yet" settles the whole brand-material group; "no opinion, you choose" settles every color question. Never ask a question a gate already answered.
- Every preference can be left to the session: it has a "you choose" option, or is left blank, and both are recorded as `you-choose`, a decision handed to the session and recorded as session-decided (#27), never a blank to chase. A fact left blank is recorded as `unknown` or `none`, never guessed. Money is the exception: a blank `spend` is recorded as `ask-me`, because spend is the owner's (#29).
- Never ask twice. What discovery already learned (what the product does, who uses it, where, the owner channel, the budget) goes into the page's pre-fill block (one small data block at the top of the page, keyed by the answer keys below; the only part of the page a session edits), `path` included from the owner's answer to discovery's one look question; the page applies the block when it opens and the owner can change anything on it. Ask only what is still unknown.
- Delegating preferences does not delegate constraints. Access needs, languages, mandatory rules, print needs and spending limits stay visible and are recorded on either path. Preserve facts already supplied through pre-fill or discovery; ask only for missing facts that affect the result and record unknowns explicitly.
- Things before opinions. A logo file, a photo of the shop sign, a link to a site the owner likes, a sentence they wrote to a customer: each is worth more than any adjective. Where a thing exists, take the fact from the thing, never from memory.
- Show what words fail at, simply. Light beside dark, four swatch strips, three corner shapes, two row densities, three kinds of lettering: a sample of a feeling with a plain label beside it, so the label alone still answers. Never a real component and never a finished screen in the form; those belong to the direction the owner sees afterwards.
- Never ask the owner a designer's question. Sizes, spacing values, ratios, which component, where a loading indicator goes, what a token is called: these are the session's within the settled direction (#27, #31).
- Scale to the stage (#30). For an `isolated` project the AI recommends the short way and says why; the owner may still take the long one. For `trial` and `operational` projects the owner chooses with no nudge.

## The two ways through

**Choose what fits my business.** Three short preference answers: what the business does and for whom, in the owner's words (pre-filled from discovery when it is already known); how it should feel, in a few words; what the owner calls the things in the product. One gate: does anything exist already (a logo, colors, a font, a site)? If yes, where it is and whether the product should belong with it. The practical constraints in questions 8 through 11 also stay on this path. The AI then commits to one direction grounded in those answers and constraints, shows it, names the alternates it set aside in a line each, and records the decision as owner-delegated (#29). The owner changes it with one word at any later contact.

**I have ideas.** The same opening, then the groups below, each behind its gate. The owner answers the groups they care about and leaves the rest on "you choose". The AI then proposes two to four directions and the owner picks (see "After the answers").

Delegation is said, never inferred. An owner who skips the form has delegated nothing: the pick stays open, the scaffold builds neutral placeholder values, and no UI feature ships until the owner picks or delegates (#27). When nobody can answer at all, #29's no-owner rule applies.

## The tree

Each line is a gate or a question; an indented line is asked only when its gate says so.

1. Start: choose for me, or I have ideas. (Both paths continue with 2 and 3.)
2. Your business in your words; how it should feel; what you call the things in it and any words you hate.
3. Gate: does anything exist already? "Nothing yet" skips the rest of this group.
   - Which of these exist: a logo (every version you have), colors, a typeface or a document template, a site or app people know, written brand rules.
   - Where they can be seen: links, files, a photo.
   - Should the product look like it belongs with this, different on purpose, or you choose?
   - (When colors are among them, the color-family question below is never asked: the colors are measured from the thing.)

The "I have ideas" path continues:

4. Gate: colors. "No opinion, you choose" skips the group.
   - Light, dark, or both. Build every committed scheme. When the committed set has one scheme, record why; keep the semantic token layer ready for another scheme without building an uncommitted one (#6).
   - Which family feels closest: warm, cool, neutral, bold, or you choose.
   - A color people already know you by, and where it can be seen.
   - Colors to stay away from, and why (a competitor's, a bad association).
   - Colors that already mean something to your users (red for urgent, a status system, a safety code). Those meanings are kept and the product's accent stays away from them (#6).
5. Gate: shape and space. "No opinion, you choose" skips the group.
   - Corners: square, soft, or round.
   - How much at once: roomy, or dense like a spreadsheet. (The AI says which it recommends, from how long people stay and what they come back to do, both asked in discovery Group 3, and why; the owner's answer stands.)
   - Lettering: plain, classic, or technical.
6. Feel and voice. Three scales (quiet to lively, plain to warm, formal to casual; the middle means "you choose"); one sentence written the way the owner would say it to a customer; apps or sites whose feel they like and one they dislike; anything it must never look like.
7. Pictures and movement. No pictures, photos, illustrations, or you choose; for photos, of what and who takes them. Movement: keep it still, a little is nice, or you choose.

Both paths continue with the practical constraints:

8. The people who use it. Anyone who has trouble with small text, colors, a mouse, or hearing; bright sun, gloves, a screen reader; "I don't know" is an answer and is recorded as unknown. Other languages, or one written right to left.
9. Gate: rules. "No rules I must follow" skips it. Otherwise: a parent brand, a law for the sector, a customer's or a government's requirements.
10. Print: will print, uniforms, or signage need to match later: no, yes, or not sure yet.
11. Money: free fonts and tools only, or ask me first with the price. A blank is `ask-me`. (Recurring spend is an escalation under #29 either way.)

What the first screen is for, what people come back to do most, and how long they stay are product questions, not look questions: discovery Group 3 asks them, and Group 6 asks what could go wrong and where a question for the owner should go. The screen for what Group 3 says people come back to do most is the one the directions compose, and the purpose sentences of the primary screens (#31) come from those answers. They are recorded on the `First task`, `Return tasks`, and `Session length` lines of References.md § Design Artifact, and `scripts/validate-design.sh` refuses `Brand decided: yes` while the first two are unknown: if discovery left one unanswered, ask it before the directions are drawn.

## The answers

The page writes, and a conversation records, the same `- key: value` lines, so a session, a design tool, and a later reader parse one shape. The keys are the contract; the page is replaceable.

`path` (pick-for-me or my-ideas), `business`, `feel_words`, `words`, `existing` (none, some, or unknown when the owner skipped it), `existing_kinds`, `existing_links`, `belongs`, `color` (written as you-choose when the color gate is closed, absent when it is open), `scheme`, `scheme_reason`, `color_family`, `color_known`, `color_avoid`, `color_meaning`, `shape` (written as you-choose when the shape gate is closed, absent when it is open), `corners`, `density`, `type_feel`, `mood_quiet_lively`, `mood_plain_warm`, `mood_formal_casual`, `voice_sample`, `likes`, `never_like`, `imagery`, `photos_of`, `motion`, `needs`, `languages`, `rules` (none when the owner said so, the rules, or unknown), `print`, `spend`.

A key the owner never saw (behind a closed gate) is absent; a preference they saw and left is `you-choose`; a fact they saw and left is `unknown`, or `none` for a free-text question about things that may not exist, never a guess; a blank `print` is `not-sure`; a blank `spend` is `ask-me`. `scheme_reason` is required and nonempty when `scheme` is `light` or `dark`; it is absent for `both`, `you-choose`, or a closed color gate. The answers file lives in the design working-files folder, committed, named in the brand book.

## After the answers

Directions are shown, never only described: in the design tool the session has, or as static pages in the design working-files folder opened in a browser. Words alone ("a calm blue with soft corners") are not a direction.

- On the short way, one direction: the screen for what discovery Group 3 says people come back to do most, composed, in every committed scheme, with its empty state and three lines of copy in the voice (a button, an error, a success). Beside it, one line for each alternate the AI set aside and why. Recorded at the decision location as owner-delegated, with the owner's own words as the grounds and the artifact revision as evidence.
- On the long way, two to four directions, genuinely different, not three shades of one idea; each with a name, a paragraph of intent tied to the answers, its palette (one accent, the neutrals, the signals), its type pairing, and the same composed screen as above. One recommended, with the reason in plain words. Two questions to the owner: "Which one would you be proud to show a customer?" and "Which one could you live with for five years?" If the answers differ, that is the conversation. The pick is recorded at the decision location with the artifact revision.
- Decision fidelity either way: enough to feel the difference, not enough to argue about a pixel. After the decision the artifact governs and the session executes without asking again; a change of mind is a new decision, not a series of tweaks.

## What the answers become

| Answers | Where they are recorded |
|---|---|
| `path` | The decision record: picked, or owner-delegated (#29) |
| `business`, `feel_words`, `voice_sample`, the three scales | Brand book: voice and tone; the grounds of the direction |
| `words` | `Vocabulary` (templates/vocabulary.md; the AI adds the verbs) |
| `existing`, `existing_kinds`, `existing_links`, `belongs`, `color_known` | Brand book: marks, palette values, type families, measured from the things |
| `scheme`, `scheme_reason` | `Color schemes` in the theme section, including the reason for a single committed scheme (#6) |
| `color_family`, `color_avoid`, `color_meaning` | Palette inputs; the reserved signal meanings (#6) |
| `color`, `shape` (closed gates), `corners`, `type_feel` | Inputs to the directions; session-decided when `you-choose` |
| `likes`, `never_like` | Direction constraints, kept with the directions in the working-files folder |
| `density` | `Density` |
| `imagery`, `photos_of`, `motion` | Brand book: imagery style, motion signature |
| `needs`, `languages` | `Accessibility target`, `Target size`, mirroring and language notes in the brand book |
| `rules`, `spend` | Brand book constraints; the spend ceiling for type and tools (#29) |
| `print` | A print line in the brand book, outside the six parts of the brand set |
| The decision (picked or owner-delegated) | The decision location, with the artifact revision; then `Brand decided: yes` once the brand book records all six parts of the brand set (marks, palette values, type families, voice and tone, imagery style, motion signature), each as a decision or an explicit none |

`Primary context` and `Committed contexts` come from discovery Group 2, not from this form.

## What the framework cannot check

Whether the form was offered, whether a gate was respected, whether "choose for me" was said in words or assumed, whether the directions were shown or only described. No script reads a conversation or an answers file; `scripts/validate-design.sh` reads only the lines the answers end up on. The session follows this document and the independent review reads the decision record (#29).
