# Convention #31: Interface Craft

## Principle

A screen is good when a person can do what they came for without noticing the interface. That takes more than consistency: one purpose per screen and one primary action; type, space, color, and motion that each carry meaning and never decorate; words written from the person's side; and the removal of every default nobody chose. The design artifact (#27) says what a screen is; this convention says what makes it good. The token system (#6) and the component foundation (#22) supply the materials; this convention says how they are composed.

Every rule here is applied by the session alone, within the direction the owner picked (#27, #29). The design interview (bootstrap/DESIGN-INTERVIEW.md) supplies the inputs, the owner's words for things, the density preference, the primary context; the session turns them into the decisions and records them. No rule here is a question to put to the owner.

## Reusable System

The project builds these once and every screen uses them:

- A purpose sentence per screen, kept in the design artifact beside the screen's entry: what a person came here to do. It is the first thing a reviewer reads.
- A vocabulary: one file, recorded on the `Vocabulary` line of References.md § Design Artifact, that names every thing the product has, once, with the verb that acts on it. Navigation, headings, buttons, errors, and messages use these words and no others.
- The type scale, the measure, the motion tokens, the focus token, and the container widths, in the theme system (#6), so that nothing in this convention needs a literal value in code.
- The state components (#8, #27), so that a state is composed, not rebuilt.
- A density decision, on the `Density` line of References.md § Design Artifact, that sets the spacing ladder's step for the whole product.
- The design review checklist (#27 "Design review", templates/design-review.md), which reads this convention in order.

## Rules

### Hierarchy

- Every screen has one purpose sentence. If it needs two, it is two screens, or one screen with a chosen focus and the rest a step away.
- One primary action per screen, or per region that reads as one. Secondary actions are quieter by weight, position, or size. A destructive action is never the primary and never sits beside it without space between them.
- Reading order is designed: the purpose first, the primary action within it, the rest in decreasing weight. Same things look the same; different things look different; nothing looks important that is not.
- A first screen for a new person shows what this is, what to do first, and nothing that only makes sense later. It appears once.
- Density is chosen once for the product and held on every screen, never chosen per screen or per developer.

### Type

- The scale is short and closed. Each step has a size, a line height, a weight set, and a job (display, title, heading, body, caption, code). A size off the scale is a violation, as a color off the palette is.
- Hierarchy uses at most the levels a screen needs, separated by size, weight, and space together, never by size alone. Two adjacent levels that cannot be told apart are one level.
- Measure is a token. Reading text never exceeds it, whatever the viewport; a form or a column of text at desk width sits inside it.
- At most two families, each with a job (text and display, or text and code). A third family needs a recorded reason.
- Numbers that align in columns use tabular figures where the family offers them; a column of numbers aligns on the decimal.

### Space and alignment

- The spacing scale is a ladder of relationship: the closer two things sit, the more they belong together; the gap between groups is always larger than any gap within a group.
- Things that align are the same kind. A misalignment is a statement, and is either intended and recorded or fixed. Data aligns by kind: numbers on the decimal, text to the left, dates in one format.
- One grid, or a recorded reason for none. Container widths are tokens. Reading content never stretches to the viewport.
- Elevation agrees with layering: a shadow or a scrim says something floats above the page; the z-index scale and the shadow scale name the same levels; nothing floats that does not.

### Motion

- Motion tokens (a duration scale and an easing set) live beside color and space; code references them and nothing else.
- Motion has a job: it answers the person's action, or shows where something came from or went. Entrance motion on content the person did not cause is a violation.
- Nothing moves under the person's attention. Arriving data never shifts what is being read; the layout holds and fills.
- One orchestrated moment per flow at most (the first run, the completion), never every element. If two things animate at once, one of them is wrong.
- Under the platform's reduced-motion preference every transition collapses to instant or a crossfade and nothing is lost, which requires that no meaning was carried by motion alone (#14).

### Words

- One vocabulary. Each thing the product has is named once, with the verb that acts on it, and carries that name everywhere. A second name for one thing is a violation.
- Buttons and links are verbs that name the outcome, never a bare "Submit", "OK", or "Yes". A confirmation names the thing it confirms.
- An error says what happened, what the person can do, and what was kept, in that order, without blame and without a code. The system's reasons stay in the log (#8).
- No filler: no greeting, no marketing sentence, no explanation of what a control obviously does. A sentence whose removal changes nothing is removed.
- Tone is the brand's, recorded once in the brand book (#28 for templates). Vocabulary discipline and error structure are not tone; they hold under every brand.

### The default is not a design

- Every visual choice traces to the artifact, a token, or a recorded reason. A default nobody chose is removed.
- Decoration has a job: a shadow says something floats, a border separates, an icon means something the label does not already say, a gradient or a glow has a recorded reason. Otherwise it goes.
- A container holds a thing that is one thing. Cards inside cards, a card around a whole page, and everything-as-card are violations.
- The foundation's default look (its theme, radii, shadows, type) is a placeholder, never a shipped product. A product whose theme equals the foundation's default has not decided its look.
- Copy that could belong to any product is filler.

## Violations

- Three same-weight buttons in one bar; a destructive action beside the primary one
- A first screen that is an empty table under a toolbar
- Density that changes from screen to screen
- A font size not on the scale; a heading distinguished from body by size alone; four font families
- Body text stretched across a wide viewport; a numeric column aligned left
- Every gap the same size; unrelated things as close as related ones
- A shadow on every section, card, and button; a floating look on something that does not float
- A list whose rows animate in on every load; a spinner in every button on every click; content that jumps when data lands
- "Submit" on a form that creates something with a name; "OK" as the only choice
- An error that reads "Request failed" with a code and no next step
- The same thing called Delete on one screen and Remove on another
- A greeting, a hero banner, or three icon columns on a working screen
- Six cards each holding one toggle; a card inside a card inside a card
- A shipped product on the foundation's untouched default theme
- Emoji as icons; icons from two sets

## Wrong vs Right

- WRONG: a record screen with Save, Delete, Duplicate, Export as four equal buttons. RIGHT: Save primary; Duplicate and Export quiet; Delete separated and quiet; the record's title and status read first.
- WRONG: six sizes a step apart used as six heading levels. RIGHT: body, title, display, each with its own weight and the space above it; three levels that read as three.
- WRONG: label, field, help text, and the next label all one step apart. RIGHT: label and field close, help text closer still, the next field a group step away.
- WRONG: a page whose cards slide in staggered from below. RIGHT: the page appears; the one item the person just created highlights briefly and settles.
- WRONG: "Error: validation failed for field email". RIGHT: "That email address is missing an @. Fix it and save again; nothing else was changed."
- WRONG: a status page with a gradient banner, three feature cards, and "Welcome back!". RIGHT: the current status first, the incidents in a list, the one action (subscribe) primary, no banner.

## What the framework cannot check

None of this convention is checked by a script. A lint can find a literal size, color, spacing, or duration in code where the token rules of #6 already forbid one; that is the whole of the machine help. Whether the primary action is the right one, whether the levels read as levels, whether a gap means what it should, whether a motion has a job, whether a sentence speaks from the person's side, and whether a default was chosen or merely inherited are read by the design review (#27) and by the independent reviewer (#29). A clean lint run is not evidence that any of this holds.

## Research Notes

Dated notes: anything named in this section is an example from the time of writing and expires. Verify current options at bootstrap.

When bootstrapping this convention:
- Record the density decision and the primary context from the design interview (bootstrap/DESIGN-INTERVIEW.md) before setting the spacing ladder's step, the row heights, and the type scale's body size; those values follow the decision, not the other way around.
- Research the platform's conventions for reduced motion, tabular figures, and text reflow at the accessibility target's zoom level, and wire the type scale, measure, motion, focus, and container tokens into the theme system (#6) before the first screen.
- Start the vocabulary from the owner's own words (the design interview, Group C) and add the verbs; keep it as one file the whole team edits.
- Copy templates/design-review.md into the project and read it in order at every screen review.
- The tells of a generated interface change with the tools that generate them; refresh the review's last check from what generated interfaces do at the time, and keep the rule (decoration has a job, a default is not a decision), which does not change.
