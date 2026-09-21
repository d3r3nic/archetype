# Convention #4: Component Design & API

## Principle

Interface components should make the project's chosen interaction model easier to understand, test, and change. The right boundary depends on the runtime, existing code, accessibility needs, expected reuse, and the cost of abstraction. Direct platform elements, a library API, selective adapters, or project-owned components can all be sound choices. Research the current options, record a consequential boundary, and apply the selected contract consistently.

## Reusable System

Establish the component approach the project actually needs:
- An inventory of existing components and platform capabilities before new work begins.
- A public interface for shared behavior where reuse, access needs, or change cost justify one.
- Consistent names for the same concepts within that interface. Different components may expose different concepts.
- Clear ownership of rendering, interaction state, data access, and business rules, with boundaries chosen for cohesion and testability.
- Layout helpers only where repeated arrangements or platform behavior justify them.

## Rules

- Before building a component, inspect the existing code, the selected platform or foundation, and the feature inventory.
- When selecting or materially changing the component approach, research the runtime's current component and composition patterns. Choose direct use, adapters, wrappers, or project-owned components for a stated reason.
- Follow the project's recorded import and composition boundary. Do not add an abstraction that merely renames an API without reducing a demonstrated cost.
- Use the same name for the same concept within the chosen component family. Do not force unlike components into one size, variant, or state vocabulary.
- Keep behavior together when that improves comprehension. Extract data access, business logic, or interaction state when separation produces a clearer contract, safer reuse, or better tests.
- Expose an element reference, handle, or equivalent only when focus management, measurement, imperative platform behavior, or interoperation needs it.
- Evaluate component size by responsibility and comprehension, not a universal line count.
- Preserve the project's accessibility target and the behavior promised by the design artifact regardless of component architecture.

## Violations

- Building a component without checking existing project and platform capabilities.
- Bypassing the project's recorded component boundary without a relevant change or new evidence.
- Adding a wrapper or layout primitive with no demonstrated consumer or responsibility.
- Giving the same concept incompatible names without a reason.
- Hiding business rules or access behavior inside presentation code so they cannot be understood or verified.
- Removing keyboard, focus, semantic, or state behavior when changing component structure.

## Wrong vs Right

- WRONG: wrap every library control because wrappers are assumed to be universally safer.
- RIGHT: compare direct use and selective adapters against the project's change risks, access requirements, and library stability, then record and enforce the selected boundary.
- WRONG: force Button, Chart, and Scene into the same size and variant props although their behaviors differ.
- RIGHT: keep shared vocabulary where the concepts match and let different responsibilities have different interfaces.
- WRONG: split a cohesive interaction across files only to satisfy a size preference.
- RIGHT: separate responsibilities when the resulting boundary is easier to reason about, test, reuse, or replace.

## Research Notes

Dated notes: anything named in this section is an example from the time of writing and expires. Verify current options when the component approach is selected or materially challenged.

- Research the platform's native elements, established foundations, accessibility behavior, composition model, and testing support.
- Inspect current project use before choosing a wrapper or shared-component boundary.
- Test the selected pattern with actual interactions, including focus, keyboard or controller input where applicable, and committed states.
- Record the component approach, import boundary, discovery surface, and material reasons in References.md.
