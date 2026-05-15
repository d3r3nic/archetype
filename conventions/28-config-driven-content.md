# Convention #28: Config-Driven Brand & Content

## Principle

A template ships once and serves many customers. Every value that
varies between customers — copy, labels, colors, contact details,
nav structure, integration keys — lives in a single config surface
the customer edits without touching view code. AI agents constantly
hardcode these values; this convention prevents that and keeps the
template reusable.

The contract is: **edit JSON, never edit view code** to change a
customer's brand, content, or wiring. If you find yourself writing
a brand name, an email, a hero headline, or a section title into a
component, you are violating this convention.

## Reusable System

Establish a single config surface:

- A typed schema (Zod / Pydantic / equivalent) that defines every
  brand-shaped value: branding, theme, typography, nav, contact,
  social, content (per page-shape), commerce, compliance,
  integrations, SEO, operational settings.
- A three-layer resolver: env-var blob → on-disk fallback file
  (gitignored) → typed defaults. Production injects the env var;
  local dev uses the file; defaults render a neutral demo.
- A universal getter (`getSiteConfig()` or equivalent) that runs on
  both server and client surfaces and returns the parsed,
  validated config. One name across the codebase.
- One canonical doc (e.g. `docs/CONFIG.md`) that lists every
  configurable field and shows the JSON shape for a customer.

Components read from the config getter and fall back to a sensible
default for the demo. Defaults live in the schema package's
`DEFAULTS` constant or in colocated content modules — never
inlined into render output.

The specific env-var name (e.g. `NEXT_PUBLIC_SITE_CONFIG` for
Next.js, `EXPO_PUBLIC_SITE_CONFIG` for Expo, `VITE_SITE_CONFIG` for
Vite, etc.) is template-local and documented in the template's
References.md — not part of this convention.

## Rules

- Never hardcode customer-facing copy in view code. Read from the
  cfg with a default fallback.
- Never hardcode contact info, social handles, brand names, or
  emails. They live in `cfg.contact`, `cfg.social`, `cfg.branding`.
- Never hardcode colors, fonts, or theme values. They live in
  `cfg.theme` and apply via the theme system (see Convention #6).
- Never hardcode integration keys (payment publishable key,
  analytics project id, etc). They live in `cfg.integrations`.
  Secrets stay in regular server-only env vars.
- Never assume an industry. If a string is industry-specific
  ("Residential / Commercial / Interior") it must be configurable.
- Never pin a customer-specific identifier in template code (cache
  tags, IDs, brand-named exports). Derive at runtime from
  `cfg.operational.customerId` or equivalent.
- Schema validation runs at trust boundaries (env parse, server-
  action input). Bad config fails loud with a clear error, not at
  render time.
- A new feature with brand-shaped values extends the schema BEFORE
  the component reads them. Component authors and schema authors
  are the same person — keep them in sync.
- Customer site spawn = clone template + write the config blob.
  Anything else is a leak.

## Acceptable hardcoding

These do NOT need to be in the config:

- **State markers**: "Out of stock", "Loading…", "Pick options",
  error messages from the network layer. These describe runtime
  state, not brand voice.
- **Framework infrastructure**: route-handler responses, redirect
  URLs internal to the app, internal cookie names, internal IDs.
- **Structural glyphs / brand-language marks** that are part of
  the template's identity (e.g. an active-page marker, copyright
  glyph). Document these in HANDOFF.md so they're explicitly
  endorsed.
- **Page section ORDER** on composed pages — order is structural
  identity, not brand voice. Customer sites override copy, not
  layout.

When in doubt: ask "would a customer in a different industry need
to change this?" If yes, configure it.

## Violations

- Brand text inlined in views (use `cfg.branding.name`)
- Contact email pinned in a `mailto:` (use `cfg.contact.email`)
- Industry-specific labels in a select / radio options array
  (use `cfg.content.forms.<form>.options`)
- Customer-named cache tags or identifiers exported from template
  modules
- A schema field exists but isn't threaded into the component that
  uses the value (declared-but-unused config is the same as no
  config)
- Component that reads cfg AND a feature-local constants module
  for the same value — pick one source of truth
- Duplicate copy in 2+ files. Extract to a single cfg field; all
  call sites read it.

## Wrong vs Right (illustrative — exact syntax depends on stack)

**Wrong:**

```
function ContactCTA() {
  return view`
    <h2>Start a conversation.</h2>
    <p>Tell us about the project.</p>
    <a href="mailto:hello@designtank.studio">hello@designtank.studio</a>
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

The customer changes any of these by editing the config blob. The
component code never moves.

## Test

Before committing a component that displays text, an image, a URL,
a number, or any user-visible value, ask:

1. Could a different customer want this changed?
2. If yes, is it read from cfg?
3. If no, is it documented as code-pinned (state marker, brand-
   language glyph, structural)?

If you can't answer all three, the component isn't ready.
