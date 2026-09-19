# Frontend scaffold: theme system

Part of the frontend scaffold playbook (scaffolding/SCAFFOLD-FRONTEND.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step. Before building, read the conventions it names and write how the system will be built in its References.md section (scaffolding/_preamble.md); when it lands, update its feature-tree.md row and its docs/systems/ page.

## Step 2: Theme system
Read: #6; #22; #27 § Design tools; scaffolding/_preamble.md § Convention-mapping rule; project: the brand book and the tokens source named in References.md § Design Artifact
Produces: the token source in every family #6 names, derived from the artifact, with every committed scheme
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: the test page in each scheme, and the search for a hardcoded color

Build:
- Design tokens (colors per scheme, spacing, the type scale and measure, radius, shadow and z-index as shared elevation levels, motion, focus, container widths, breakpoints) as single source of truth (#6, #31).
- **Dark mode from day 1.** Theme has both light and dark variants wired.
- UI library selected and CONFIGURED with the theme, OR thin wrappers over HTML primitives if the project chose no UI library. Either way, features never import raw UI-library components directly — they import from `src/shared/ui/`. Document the choice in References.md § Convention Overrides.
- Theme provider mounted at the app root. Signals: detects system preference, persists user override, toggles via class/attribute (never media-query-only — blocks user override). Research current APIs for the chosen framework + styling system.
- Token values come from the artifact in the recorded direction of truth (`References.md § Design Artifact`) when `Brand decided` is yes: the `Tokens source` under `repository-first`; the artifact itself under `workspace-first`, adopted into the tokens source in the same change. Otherwise build every layer with neutral placeholder values (platform color keywords, inherited typography, relative sizing) so the owner's pick lands as a value change, not a rewrite; the semantic layer is complete either way (#27).

**Verify:** a test page renders with light tokens by default, switches to dark on toggle, and no component hardcodes a color.
