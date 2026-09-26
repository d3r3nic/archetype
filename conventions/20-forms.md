# Convention #20: Forms & User Input

## Applies when

The product collects input from people: sign-up, settings, checkout, data entry, search with options. What varies: the platform's input controls, how long the forms are, and whether a draft can be kept. A product that takes no input skips this convention.

## Principle

Every form uses the project's one form system: its fields, validation, error display and submission. People never lose what they typed, always know which field needs attention and why, and can fix it with any input method. Validation rules are defined once, with the data's shape (#7).

## Reusable System

The form system: field components with their labels and errors tied to them, validation from the one shape definition, the mapping of server errors onto fields, the submission and waiting states, and the draft or leave-warning behavior. References.md records where it lives and how features build a form with it.

## Rules

- Build every form with the shared form system; never hand-write validation and error display in a feature.
- Define validation once with the data's shape (#7); the form, the server and the type all use that definition, or one generated from it.
- Do not show an error for a field the person is still filling in for the first time. Clear an error as soon as it is fixed. On submit, check everything and take the person to the first problem.
- Show each error at its field, in words that say how to fix it (#31), and tie it to the field for assistive technology (#14).
- Map validation errors from the server onto the fields they concern, never a generic failure message.
- Keep a draft where the product can; otherwise warn before leaving a form with unsaved input, and say what would be lost.
- Split a long form into steps when that helps people, validating each step before the next.

## Violations

- Validation written by hand, field by field, in a feature.
- The same rules defined separately for the form and for the data.
- A server's field error shown as a generic failure.
- Errors shown while the person is still typing a first entry, or left showing after they are fixed.
- An error that assistive technology cannot connect to its field.
- Input lost on an accidental navigation.

## Wrong vs Right

- WRONG: a submit handler checks each field with its own conditions, and the data's shape is defined again elsewhere. RIGHT: one definition validates the form; the form system runs it and shows each error at its field.
- WRONG: the server says the email is taken and the person sees "Something went wrong". RIGHT: "This email already has an account" appears at the email field.
- WRONG: half a long form is lost to a mistaken tap on a link. RIGHT: the draft is kept, or the person is warned and stays.

## Research Notes

Research the chosen stack's form handling options, how they share one validation definition with the data's shape, accessible error patterns on the product's platforms, and draft or unsaved-change handling. Record the form system and its usage in References.md.
