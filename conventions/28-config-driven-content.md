# Convention #28: Config-Driven Brand & Content

## Applies when

The project is a template that serves many customers or brands from one codebase, or a product whose brand and content must change without code edits (white-label, multi-tenant, reseller). A single-purpose product with one brand and no customer variation marks #28 not applicable in feature-tree.md with a one-line reason; the configuration rule of #1 and the styling source of #6 still apply to it.

## Principle

A template ships once and serves many customers. Every value that varies between customers (copy, labels, colors, contact details, navigation, integration keys) lives in one configuration surface, validated against a schema and read through one accessor. Changing a customer's brand, content or wiring never requires editing view code. A brand name, an email, a headline or a section title written into a component violates this convention.

## Reusable System

One configuration surface:
- a typed schema for every value that varies by customer: branding, theme, typography, navigation, contact, social, content per page shape, commerce, compliance, integrations, search metadata, operational settings;
- a resolution order chosen for the deployment model, such as a value injected in production, a local file in development, and neutral defaults for a demo;
- one accessor, with one name across the codebase, that returns the parsed and validated configuration wherever the code runs;
- one document that lists every configurable field and shows a customer's configuration.

Components read from the accessor and fall back to a neutral default. Defaults live with the schema or in content modules beside it, never inlined into rendered output. The delivery details (the variable name, the file path, the accessor's name) are the template's own and are recorded in its References.md.

## Rules

- Never write customer-facing copy into view code. Read it from the configuration, with a default.
- Never write contact details, social handles, brand names or emails into code. They live in the configuration's contact and branding fields.
- Colors, fonts and theme values come from the configuration and reach the interface through the theme system (#6).
- Public integration keys live in the configuration; secrets stay in server-only environment values.
- Never assume an industry. An industry-specific string is configurable.
- Never pin a customer-specific identifier in template code (cache tags, identifiers, brand-named exports). Derive it at run time from the configuration.
- Validate the configuration where it enters. Bad configuration fails loudly, with a clear error, before anything renders.
- A feature with customer-shaped values extends the schema before its component reads them.
- Making a customer's product from the template means copying the template and writing the configuration. Any other change needed is a leak to fix in the template.

## Acceptable hardcoding

These do not need to be in the configuration:
- **State markers:** "Out of stock", "Loading", error messages from the network layer. They describe run-time state, not brand voice.
- **Infrastructure:** route responses, internal redirects, internal cookie names, internal identifiers.
- **Structural marks** that are part of the template's identity, such as an active-page marker. Document them in the configuration document so they are explicitly endorsed.
- **The order of sections** on composed pages: order is structural identity, not brand voice.

When in doubt, ask whether a customer in a different industry would need to change it. If yes, configure it.

## Violations

- Brand text written into views.
- A contact email pinned in a link.
- Industry-specific options in a list written into a form.
- Customer-named identifiers exported from template modules.
- A schema field that exists but that the component never reads: declared but unused configuration is the same as none.
- A component that reads the configuration and a local constant for the same value.
- The same copy in two or more files instead of one configuration field.

## Wrong vs Right (illustrative; the syntax depends on the stack)

The accessor's name below is an example project's choice, not a prescription.

**Wrong:**

```
function ContactCTA() {
  return view`
    <h2>Start a conversation.</h2>
    <p>Tell us about the project.</p>
    <a href="mailto:hello@example.com">hello@example.com</a>
  `;
}
```

**Right:**

```
function ContactCTA() {
  const cfg = getSiteConfig();
  const headline = cfg.content?.home?.contactCta?.headline ?? 'Start a conversation.';
  const body = cfg.content?.home?.contactCta?.body ?? 'Tell us about the project.';
  const email = cfg.contact?.email ?? cfg.operational?.supportEmail ?? 'hello@example.com';
  return view`
    <h2>${headline}</h2>
    <p>${body}</p>
    <a href="mailto:${email}">${email}</a>
  `;
}
```

The customer changes any of these by editing the configuration; the component never changes.

## Test

Before committing a component that shows text, an image, an address, a number or any other visible value, ask:
1. Could a different customer want this changed?
2. If yes, is it read from the configuration?
3. If no, is it documented as fixed (a state marker, a structural mark)?

If any answer is missing, the component is not ready. A reviewer applies this test; no script does.

## Research Notes

Research configuration delivery for the project's deployment model: which values reach code that people can inspect, when an update takes effect, and how schema validation fails. Public content belongs in public configuration; credentials need a separate protected store. Keep the accessor stable when the delivery changes, and record the delivery details in References.md.
