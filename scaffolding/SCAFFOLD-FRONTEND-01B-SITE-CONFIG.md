# Frontend scaffold: site-wide content in one place

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 1b: Site-wide content in one place
Read: #28; #0; #1; #7; scaffolding/_preamble.md § Convention-mapping rule
Produces: the typed module that holds site-wide business content and its defaults, read everywhere that content appears
Check: run project: typecheck, lint; evidence: what was seen when this was tried: the search for hardcoded site name, tagline, and navigation labels, and one value changed in the module showing everywhere
Skip when: the product shows no business content that repeats across screens (a name, contact details, navigation, footer links)

Business content that appears on more than one screen, or that would be a find-and-replace hazard, has one owner (#0): the site name, tagline, navigation, contact details, brand marks, footer links, page descriptions, social links. For a template or white-label product this is the configuration surface of #28.

Build:
- One typed module (or the #28 configuration surface) holding that content's structure and defaults, so a fresh clone renders with neutral placeholder values.
- Values that differ per environment come from the configuration owner of Step 1, never repeated here as constants.
- When people other than developers edit some of this content, the current values come from the content source the project chose, through the API layer (Step 6); this module keeps the structure and the fallbacks.

Components read the module; they never write business strings of their own.

**Verify:** a search for the site name, tagline and navigation labels across the source finds them only in the module; changing one value there changes it everywhere it appears.
