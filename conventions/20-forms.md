# Convention #20: Forms & User Input

## Principle

Forms are handled through one reusable form system. Validation is schema-based: one schema definition produces both the type and the validation rules. Error messages are accessible and mapped to specific fields. Complex forms use a multi-step pattern with per-step validation. The form system is built once during scaffolding and used by every feature that collects user input.

## Reusable System

Create a form system that establishes:
- Integration with a form handling library configured with project defaults
- Schema-based validation where one schema definition produces both the type and the runtime validation. Never maintain a separate type definition and a separate validation schema for the same form data.
- Form field components with built-in error message display, label association, and accessibility. Every field shows its error inline, associated with the field for screen readers.
- A multi-step wizard pattern with per-step validation for complex forms that would be overwhelming as a single page
- Unsaved changes detection that warns users when navigating away from a form with modified data
- Server error mapping that takes field-specific validation errors from the server and displays them on the correct form fields

## Rules

- One schema = types + validation. Define the schema once, derive the type from it. Never write a separate type definition and a separate validation schema for the same form.
- Validate on field blur or change for immediate feedback. Validate the entire form on submit for final verification.
- Error messages are displayed inline below the field and are programmatically associated with the field for screen readers.
- Server-side validation errors must be mapped back to specific form fields, not shown as a generic toast or alert.
- Always warn users when navigating away from a form with unsaved changes.
- Always provide explicit default values for all form fields. Missing defaults cause framework warnings and inconsistent behavior.

## Violations

- Manual validation logic (checking each field with if statements) instead of schema-based validation
- Separate type definition AND validation schema for the same form (they drift apart when one is updated)
- Error messages shown as a generic toast instead of mapped to specific fields
- No unsaved changes warning on forms with user input
- Missing default values on form fields
- Error messages not associated with their fields for screen readers (accessibility violation)

## Wrong vs Right

- WRONG: a submit handler that checks each field with if statements: if email is empty, set error. If email doesn't contain @, set error. If password is short, set error. Manual, repetitive, and the type definition is maintained separately.
- RIGHT: a validation schema that defines email must be valid, password must be minimum length. The type is derived from the schema automatically. The form library runs the schema on submit and maps errors to fields automatically.
- WRONG: the server returns a validation error saying the email is already taken. The feature shows a generic "Something went wrong" toast. The user doesn't know which field to fix.
- RIGHT: the server returns field-specific errors. The form system maps "email: already taken" to the email field, showing the error inline below the email input.
- WRONG: user fills out half a long form. Accidentally clicks a link. Navigates away. All form data is lost. User is frustrated.
- RIGHT: user fills out half a form. Clicks a link. A prompt asks "You have unsaved changes. Leave without saving?" User stays and finishes the form.

## Research Notes

When bootstrapping this convention:
- Research the framework's recommended form handling library. Find one that integrates with schema-based validation where schemas produce both types and validation.
- Research validation schema libraries that work with the form library and produce type-safe form types
- Research accessible form error patterns for the framework (how to associate error messages with fields programmatically)
- Research the framework's patterns for dirty/unsaved changes detection and navigation guards
- Research multi-step form wizard patterns for the framework
- Document the form library, validation approach, field components, and patterns in References.md
