# Frontend scaffold: global site config (content, not code)

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 1b: Global site config (content, not code)
Read: #28; #0; #1; #7; scaffolding/_preamble.md § Convention-mapping rule
Produces: the typed site config module with its defaults, read everywhere site-wide content appears
Check: run project: typecheck, lint; evidence: what was seen when this was tried: the search for hardcoded site name, tagline, and navigation labels, and one value changed in the config showing everywhere

One source of truth for site-wide business CONTENT: site name, tagline, navigation items, contact details, brand marks, footer links, meta description, social URLs. Anything that appears on more than one page OR would be a find-and-replace hazard belongs here.

Build:
- A typed config module exporting a `site` object (or equivalent structure).
- Values that vary per environment (public contact email, analytics IDs, feature flags) read through the validated env layer from Step 1 — NOT duplicated as string constants.
- Editor-authored values (tagline variants, about copy, announcement banners) come from the CMS at runtime via the API layer (Step 6). The site config module holds the STRUCTURE + FALLBACKS; the CMS provides the current values.
- Default values so the app builds before a CMS is wired. A fresh clone renders with placeholders; overriding one file changes the whole site.

Rules:
- If a business string appears on more than one page, it MUST be in site config.
- If a value is environment-specific, it MUST be in the env layer (not duplicated in site config).
- Components NEVER hardcode business strings. They import `site` (or equivalent) and read from it.

**Verify:** grep for hardcoded site name / tagline / nav labels across source — zero hits. Changing one value in the site config module reflects everywhere it appears.

This pattern is hoisted to framework level because every CMS-driven consumer site faces the same need. Template projects ship the structure (placeholder values); product projects fill in values at their own bootstrap.
