# Frontend scaffold: theme system

Part of the frontend scaffold playbook (scaffolding/SCAFFOLD-FRONTEND.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step. Before building, read the conventions it names and write how the system will be built in its References.md section (scaffolding/_preamble.md); when it lands, update its feature-tree.md row and its docs/systems/ page.

## Step 2: Theme system
Read: #6; #22; #31; #27 § Design tools; scaffolding/_preamble.md § Convention-mapping rule; project: the brand book and the tokens source named in References.md § Design Artifact
Produces: the token source in every family #6 names, derived from the artifact, with every committed scheme
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: the test page in each scheme, and the search for a hardcoded color
Depends on: scaffold-frontend.1; bootstrap.4.5
Basis: decisions and inputs required

Build:
- Design tokens (colors per scheme, spacing, the type scale and measure, radius, shadow and z-index as shared elevation levels, motion, focus, container widths, breakpoints) as single source of truth (#6, #31).
- Build every scheme committed in the design artifact from day 1. When the committed set has one scheme, build that scheme and retain its recorded reason. Keep semantic role tokens capable of another scheme without making components change or claiming an uncommitted scheme exists.
- UI library selected and CONFIGURED with the theme, OR thin wrappers over HTML primitives if the project chose no UI library. Either way, features never import raw UI-library components directly — they import from `src/shared/ui/`. Document the choice in References.md § Convention Overrides.
- Theme values are applied at the app root. With multiple committed schemes, detect system preference, persist the person's override, and switch via a class or attribute so the person can override the media query. With one committed scheme, do not expose a switch to a scheme the product has not built. Research current APIs for the chosen framework and styling system.
- Token values come from the artifact in the recorded direction of truth (`References.md § Design Artifact`) when `Brand decided` is yes: the `Tokens source` under `repository-first`; the artifact itself under `workspace-first`, adopted into the tokens source in the same change. Otherwise build every layer with neutral placeholder values (platform color keywords, inherited typography, relative sizing) so the owner's pick lands as a value change, not a rewrite; the semantic layer is complete either way (#27).

**Verify:** a test page renders in every committed scheme, switches among them when there is more than one, and no component hardcodes a color.
