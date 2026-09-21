# Frontend scaffold: design-system and component foundation

Part of the frontend scaffold playbook (scaffolding/SCAFFOLD-FRONTEND.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step. Before building, read the conventions it names and write how the system will be built in its References.md section (scaffolding/_preamble.md); when it lands, update its feature-tree.md row and its docs/systems/ page.

## Step 4: Design-system and component foundation
Read: #4; #22; #14; #31; #27 § Design review; scaffolding/_preamble.md § Convention-mapping rule
Produces: the wrappers in use, the layout primitives, the catalog, the icon set, the focus token, the state gallery, the capture command recorded in References.md § Commands, and the lint rule on the wrapper boundary
Check: run project: typecheck, lint, build, capture; evidence: what was seen when this was tried: the wrapper-only test page, the lint rule run against a direct import, and what the captures show
Depends on: scaffold-frontend.2; scaffold-frontend.3
Basis: decisions and inputs required

Build:
- Base wrapper components around the UI library: the ones the artifact specifies and the ones the state components, the layouts, and the smoke-test feature use, each with its catalog entry. Any other wrapper is added in the change that first uses it; a wrapper nothing uses is not built, so the catalog never opens with an unused component (#22).
- Wrappers enforce accessibility (ARIA, focus management, keyboard nav) the UI library's defaults might miss.
- Layout primitives: Stack, Grid, Page container.
- Component catalog, always (#22); the tool is the project's choice.
- Consistent component API across wrappers (consistent prop names, variant system).
- One icon set, recorded in References.md; the focus token wired so every wrapper shows it on every surface in every scheme (#14, #22).
- A state gallery: a dev-only route, or the catalog, that renders every state component and each feature screen in each applicable state from fixtures, in every committed scheme; and a capture command, recorded in `References.md § Commands`, that saves the capture set the design review reads (#27). Production builds exclude the gallery.
- Wrapper defaults, variants, and the catalog follow the artifact's component specifications where they exist (#27). A component the artifact shows and the foundation lacks is a wrapper to add; a spec the artifact lacks is designed first, not improvised in the wrapper.
- **Lint-enforce the wrapper boundary.** Direct UI-library imports outside `src/shared/ui/` must fail the build. Use your linter's import-restriction mechanism — feature/app code cannot bypass the wrapper layer. Exempt `src/shared/ui/` itself. Research current linter rule for the chosen language.

**Verify:** a test page built from wrappers only (no raw HTML, no direct UI library imports) renders correctly. Running the lint rule against a direct import fails. The capture command saves a capture of every state component in every committed scheme.
