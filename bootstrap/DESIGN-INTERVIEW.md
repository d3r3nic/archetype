# Design interview: what the designer asks the owner

Routed from `bootstrap/ONBOARD.md` Group 1 when the project is a product. It runs once, at product bootstrap, after discovery has established that the project is a product and not a template. Every question is written for someone who has never designed anything. The AI asks one group at a time, in plain words, and records the answers in References.md § Design Artifact and the brand book (#27). A template project skips it: templates decide no brand, and their downstream products run it at their own bootstrap.

Three rules for asking:

- Ask for things before opinions. A logo file, a photo of the shop sign, a link to a site the owner likes, a sentence they wrote to a customer: each of these is worth more than any adjective. Where a thing exists, take the fact from the thing, never from memory.
- Never ask the owner a designer's question. Sizes, spacing, ratios, which component, whether a button is outlined, where a loading indicator goes, what a token is called: these are the session's to decide within the settled direction (#27, #31). Asking them pushes the designer's job onto the owner (#29).
- A vague answer is recorded as "not yet", never as a default. "I don't know" about color means the AI proposes directions from what exists; it never means the AI picks a color and moves on. "Whatever you think" is a pick only when the owner says it about a specific proposed direction; silence adopts nothing (#29).

## Group A: what already exists

Gather, do not ask for opinions yet.

1. Do you have a logo? Send every version you have: color, one-color, the small one, the old one. If there is none, say so; the product will set its name in plain type until one exists, and nobody will draw one for you.
2. Do you have colors already, from the logo, a website, printed material, a sign, a uniform, packaging? Send a photo or a link. The colors will be measured from that, not guessed.
3. Do you have a typeface, or a document template your people already use (letters, invoices, slides)? Send it.
4. Is there a website, app, or document of yours that people already know? Link it. Should the new product look like it belongs with it, or be different on purpose?
5. Do you have any written rules about how the brand looks or talks, even a single page? Send it.

Fills: `Brand book`, the marks, palette values, and type families of the brand set, and `Brand decided` (yes only when all six parts of the brand set are answered, here or in Group D).

## Group B: who uses it, and where

6. Who will use it most: you, your team, your customers, the public? Roughly how many at once?
7. Where are they when they use it: sitting at a desk, on a phone while doing something else, on a shared screen in a room, outdoors? Which of those is most of the time?
8. How long do they stay: a quick check a few times a day, or hours at a stretch?
9. Do any of your users have trouble seeing small text, telling colors apart, using a mouse, or hearing? Do any work in bright sunlight, wear gloves, or use a screen reader? If you do not know, say so.
10. Will people use it in a language other than yours, or in one written right to left?

Fills: `Primary context`, `Committed contexts`, the accessibility target and the platform minimum for target size, the density recommendation (long hours favor a quiet palette and a dense layout), the measure and mirroring decisions.

## Group C: what it is for

11. When someone opens it for the very first time, what is the one thing they should be able to do within a minute?
12. What do people come back to do most often, day to day? Name the top three.
13. What must never go wrong, or would be costly to undo: sending something, paying, deleting, publishing, changing a record other people rely on?
14. What do you call the things in your product? Cases, jobs, orders, clients, tasks, sessions. Give me the words you already use with your team and your customers, and any words you hate.

Fills: the purpose sentence of the first screen and of the three primary screens (the artifact), the confirm-versus-undo treatment of destructive actions, and `Vocabulary` (the glossary starts from the owner's words; the AI adds the verbs).

## Group D: how it should feel

15. Show me two or three apps or sites whose feel you like, even if they do something completely different, and say in one sentence what you like about each. Then show me one you dislike, and say why.
16. Should it feel calm, with a few things at a time, or packed with information like a spreadsheet?
17. Between these pairs, where does it sit: quiet or lively; plain or warm; formal or casual; classic or modern? A word or a point between them is enough.
18. How should it talk to people: like a colleague, like a form, like a friend? Write me one sentence you would send to a customer, in your own words.
19. Do you want a dark appearance as well as a light one? Do you or your users use dark mode on their phones? (The product builds both unless you say no and give a reason (#6); the question confirms, it does not decide.)
20. Photos, illustrations, or neither? If photos, of what: your people, your products, your places? Who takes them?
21. Do animated interfaces annoy you, or do you like a little movement?
22. Is there anything it must never look like: a competitor, an old version, a product people associate with a bad experience?

Fills: `Density`, the tone line of the brand set, `Color schemes`, the imagery and motion lines of the brand set, and the direction constraints the AI works within.

## Group E: color, only when Group A found nothing

23. Is there a color your business is already known by, even informally: the sign, the van, the uniforms, the packaging, the old brochure? If yes, that is your color. Send a photo.
24. If there is none, I will propose two to four directions in different colors and you will pick one. To make them good, tell me: colors you cannot stand; colors your competitors already own; whether it should feel warm (reds, oranges, earth tones), cool (blues, greens, grays), or neither; whether it should look restrained and expensive or bright and energetic.
25. Does anything in your world already carry a color that means something to your users: red for urgent, green for done, a status system, a safety code, a team color? Those meanings will be kept, and the product's main color will stay away from them.
26. Will printed material, uniforms, or signage need to match the product later?

Fills: the palette inputs for the direction proposals, the reserved signal meanings (#6), and whether the brand set includes print.

## Group F: practicalities

27. Are there rules you must follow: an industry standard, a parent company's brand, an accessibility law for your sector, a customer's or a government's style requirements?
28. Who says yes to the design: you alone, or other people too? How quickly can you usually answer? (Reuse the owner-channel answer from ONBOARD.md if given.)
29. Do you want to see the design as pictures before it is built, or see it working and change it after? (Fidelity follows purpose (#29); this only matters when the purpose leaves it open.)
30. If a typeface or a design tool costs money, is that acceptable, and roughly how much? (Recurring spend is an escalation under #29; the answer sets what the AI may propose.)

Fills: the constraints line of the brand book, the owner channel, the deliverable fidelity, and the spend ceiling for type and tools.

## After the interview: the direction pick

The owner decides how the product looks by picking from directions the AI proposes (#27, #29). Nothing in the interview replaces that pick; the interview makes the proposals good.

What the AI prepares:

- Two to four directions, genuinely different, not three shades of one idea. Each direction has a name, one paragraph of intent tied to the interview answers, a palette (one accent, the neutrals, the signals), the type pairing, and one composed screen: the most frequent screen from question 12, in both color schemes, with its empty state, plus three lines of copy in the direction's tone (a button, an error, a success).
- Decision fidelity, not finished screens: enough to feel the difference, not enough to argue about a pixel.
- One recommended, with the reason in plain words tied to the answers ("you said hours at a stretch and a team of specialists, so the quiet, dense direction").

How the AI presents it to a non-designer:

- Side by side, the same screen in each, no jargon. For each direction: what it is good at, and what it gives up.
- Two questions to ask the owner: "Which one would you be proud to show a customer?" and "Which one could you live with for five years?" If the answers differ, that is the conversation.
- The pick is recorded at the decision location with the artifact revision as evidence. After the pick the artifact governs and the AI executes without asking again; a change of mind is a new pick, not a series of tweaks.

What the owner is never asked after the pick: sizes, spacing, which component, where a state goes, what a token is called, whether a button is outlined. The session decides those within the direction and records them as session-decided entries in the artifact (#27).

## What the answers become

| Interview answer | Where it is recorded |
|---|---|
| Logo, colors, typeface, brand rules (1 to 5) | Brand book; `Brand decided`; the six lines of the brand set |
| Who, where, how long (6 to 8) | `Primary context`, `Committed contexts`, `Density` |
| Users' needs (9, 10) | `Accessibility target`, `Target size`, mirroring and language notes in the brand book |
| First thing, top three, must-not-fail (11 to 13) | Purpose sentences in the artifact; destructive-action treatment in the artifact |
| The owner's words (14) | `Vocabulary` (the glossary file) |
| Feel, tone, schemes, imagery, motion, never-look-like (15 to 22) | Brand book tone, imagery, motion lines; `Color schemes`; direction constraints |
| Color inputs (23 to 26) | Palette proposals; reserved signals; print in the brand set |
| Constraints, approver, fidelity, spend (27 to 30) | Brand book constraints; owner channel; deliverable purpose; the spend ceiling |
| The pick | Decision location, with the artifact revision |
