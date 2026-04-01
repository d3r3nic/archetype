# Convention #20: Forms & User Input

## Principle

Forms are handled through one form system. Validation schemas define both types and rules in one place. Error messages are accessible and mapped to specific fields. Complex forms use a multi-step pattern with per-step validation. The form system is reusable across all features.

## Reusable System

- Form library integration: configured form library with project defaults
- Validation schemas: Zod/Yup schemas that infer types and validate
- Form field components: input, select, checkbox with built-in error display
- Multi-step wizard: reusable stepper with per-step validation
- Dirty tracking: unsaved changes warning on navigation

## Rules

- One schema = types + validation. Never maintain both separately.
- Validate on blur/change at field level. Validate on submit at form level.
- Error messages are associated with fields via aria-describedby.
- Warn users when navigating away from unsaved changes.
- Server validation errors are mapped back to specific form fields.
- Default values are always explicit for every field.

## Violations

- Manual validation logic instead of schema-based
- Separate TypeScript interface AND Zod schema for the same form (should be one)
- Error messages not associated with their fields (accessibility)
- No unsaved changes warning on forms with user input
- Server errors shown as a generic toast instead of mapped to fields

## References.md Section

- Form library: which one and configuration
- Validation: which schema library
- Form components: path to shared form field components
- Wizard: path to multi-step form pattern if exists
