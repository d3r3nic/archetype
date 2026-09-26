# Convention #22: Design System

## Applies when

The product has an interface built from reusable controls. What varies: the platform's native controls, whether an established foundation fits, and how many screens share the same controls. A product with no interface skips this convention.

## Principle

Every control the product uses has one implementation, and every screen reuses it. Choose the interface foundation that best serves the project's purpose, platform, existing work, access needs, and likely change. An established library may carry valuable behavior. Native elements may already provide the right contract. Selective adapters may isolate real volatility. A project-owned foundation may be justified. Research current evidence and record the consequential choice instead of assuming that every project needs a library, wrapper layer, or catalog.

Whatever the architecture, the implemented interface must honor the accepted artifact, committed schemes and contexts, accessibility target, and tested interaction behavior.

## Reusable System

Establish the interface system the project chose:
- The selected foundation and why it fits, including direct native or direct library use when appropriate.
- The import or composition boundary that consumers actually follow.
- Theme or styling integration according to convention #6 and the accepted artifact.
- A discovery surface proportional to the project, such as existing code search, generated documentation, a catalog, previews, or a combination.
- A replacement and migration approach for shared interfaces that change.

## Rules

- Research native capabilities and current maintained foundations against required behavior, accessibility, platform fit, maintenance, bundle or runtime cost, and existing project use.
- Record the selected foundation and boundary before scaffolding shared interface code. Revisit it only when relevant evidence or requirements change.
- Follow the chosen boundary. If direct imports are the recorded pattern, use them consistently. If adapters or wrappers isolate a real concern, consumers use that layer.
- Add an adapter only when it configures behavior, preserves a stable project contract, centralizes a meaningful policy, or isolates demonstrated volatility.
- Do not rebuild a control when an existing option meets the requirement. Do not adopt an existing option merely because it is popular when its behavior or cost does not fit.
- When a second screen needs a control the project already has, it uses that control; when two screens hold the same control, it becomes one shared component. Never build a second copy. Keep apart only controls that look alike but serve different roles, and record why (#0).
- Name components and variants from their project meaning. Similar roles should look and behave consistently; different roles may use different patterns.
- Keep available components and interaction states discoverable through the project's recorded method. A catalog is required only when it is the selected discovery and review surface.
- Preserve focus, input, semantics, state communication, and every committed scheme and context through component changes.
- Record deprecation and migrate consumers before removal when a shared contract changes.
- Use an icon strategy coherent with the accepted direction and accessibility target. More than one source requires a reason and a consistency plan, not an automatic failure.
- Design content may draw controls directly. Code implementing it follows the project's selected interface and styling contracts.

## Violations

- Choosing a foundation or wrapper policy without examining the project's actual platform and requirements.
- Bypassing the recorded import or composition boundary without new evidence or a migration decision.
- A second implementation of a control the project already has.
- Adding pass-through wrappers, unused primitives, or catalog entries with no demonstrated purpose.
- Rebuilding interaction and accessibility behavior that a fitting selected foundation already provides.
- Losing required keyboard, focus, controller, semantic, state, scheme, or context behavior.
- Letting foundation-specific details spread across the project after deciding to isolate them.

## Wrong vs Right

- WRONG: install the most popular library, wrap every control, and call the architecture reusable before testing the product's interactions.
- RIGHT: compare native, library, adapter, and project-owned options against the actual requirements, exercise the risky interactions, then enforce the selected contract.
- WRONG: import directly in some features and through wrappers in others because both patterns were convenient locally.
- RIGHT: use the recorded boundary consistently, or change it through a migration decision with affected evidence reopened.
- WRONG: require a catalog for a small native interface when code search and focused previews already make the system discoverable.
- RIGHT: choose a discovery and review surface proportional to the project and keep it current.

## Research Notes

- Research current platform controls and maintained foundations, including accessibility, theming, interaction coverage, maintenance, runtime cost, and migration risk.
- Inspect the project's existing components and actual repeated behavior before proposing a new layer.
- Prototype or test the interactions whose quality cannot be established from documentation alone.
- Document the foundation decision, consumer boundary, styling integration, discovery surface, and verification evidence in References.md.
