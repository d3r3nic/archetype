# Convention #14: Accessibility

## Applies when

The product has an interface people use: screens, pages, a device app, a terminal interface, a game. What varies: the platform's own accessibility services, the input methods it supports (pointer, touch, keyboard, controller, voice, assistive technology), and the level the project commits to. A product with no interface skips this convention.

## Principle

The product works for everyone who is meant to use it, whatever their abilities and inputs. Accessibility is built into the shared components during scaffolding, not added after features are done. The project commits to an accessibility target, a recognized standard and level, researched at bootstrap and recorded. Absent a stronger requirement from law, contract or platform, the target is the level that most accessibility laws reference.

## Reusable System

Accessible shared components that every feature uses: dialogs that hold focus and return it, menus and lists that work by keyboard or equivalent, form fields with their labels and errors tied to them, and the platform's way to give assistive technology text that is not shown on screen. References.md records the target, the target size, and the tools that check accessibility.

## Rules

- Use the platform's semantic elements for their meaning: actions are actions and navigation is navigation. Never simulate a control with a generic element.
- Every input has a visible label tied to it. Placeholder text is not a label.
- Every image or icon that carries meaning has a text alternative that says what it means; decoration is marked as decoration.
- Structure is real: headings, regions and reading order follow the content. On web pages this includes heading levels in order and a way to skip repeated navigation.
- Focus is visible on every interactive element, in every scheme, and designed rather than left to a default a reset can erase.
- Every meaning carried by color, sound, motion or position has a second carrier in text, an icon or structure.
- Dialogs keep focus inside while open and return it to where it came from.
- Respect the person's reduced-motion and other platform preferences without losing meaning or control.
- Targets meet the platform's minimum size, recorded on the `Target size` line of References.md, with space between adjacent targets.
- Reading order, visual order and focus order agree.
- At the zoom level the target sets, text reflows without losing meaning or being clipped.
- Every action reachable by pointer is reachable by keyboard and by touch where the platform has them. Hover reveals nothing essential, drag has an alternative, time limits can be extended, and moving content can be paused.

## Violations

- A generic element acting as a button or link.
- An input with no label, or only a placeholder.
- A meaningful image with no alternative, or a meaningless one like "image".
- Structure faked with styling: headings chosen for size, regions that are not regions.
- A focus indicator removed or invisible in one scheme.
- Color as the only signal of state.
- A dialog that lets focus escape or loses it on close.
- Actions reachable only by hover or only by drag.

## Wrong vs Right

- WRONG: a styled box that looks like a button but cannot be reached or activated by keyboard and is not announced. RIGHT: the platform's button, which is reachable, announced and activated with no extra code.
- WRONG: an email field whose only label is placeholder text that disappears on typing. RIGHT: a visible label tied to the field, always shown and always announced.
- WRONG: a chart image described as "image". RIGHT: an alternative that says what the chart shows, such as the growth it reports.

## Research Notes

Research the current accessibility standard and its levels, the laws and contracts that apply to the project (#30), the platform's accessibility services and guidelines, accessible component options for the chosen stack, and tools that test accessibility automatically in the project's checks. Record the target, the target size, the shared components and the checks in References.md.
