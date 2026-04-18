# Convention #0: Reusability & Composition (META)

## Principle

Everything is built once and configured for context. This governs how every other convention is implemented. When any convention is applied, it produces one reusable foundational system. Features plug into systems, never build ad-hoc. AI duplicates more than humans - one reusable source prevents drift.

Reusability operates at two levels:

**Inside a project** — one error system, one API layer, one theme, one auth utility. Features share the systems. Do not fork or duplicate.

**Across the software landscape** — if a platform, library, or service already solves the problem end-to-end, use it. Do not rebuild what already exists as a market-available product. Common categories where a platform is usually the right answer: content/blog management, e-commerce, booking/scheduling, HIPAA practice management, payments, identity/SSO, newsletter/email, analytics. For each category, research current market-leading options at bootstrap time — do not rely on specific vendor names in this convention, they drift. Custom code is for the layer platforms do not cover.

Both levels prevent the same failure: building what already exists, wasting effort, creating drift between the built version and the canonical version. This convention governs decisions in bootstrap (do we need custom code at all?) AND in development (does a system for this exist already?).

## Reusable System

This convention doesn't produce a single system. It governs HOW all systems are built. Every other convention in this framework produces a foundational system following these rules:
- Every system is config-driven. It accepts configuration objects, not hardcoded values.
- Every system has one location in the codebase. Single source of truth.
- Every system is usable by any feature through simple imports and configuration.
- When the same logic appears in two places, that's a signal a reusable system is missing.

## Rules

- Before committing to a custom build, check whether an existing platform or service already covers the use case. If yes, use it. Custom code is for the layer platforms do not cover.
- Before building anything inside the project, read feature-tree.md to see what systems and features already exist.
- If a system exists for what you need, use it. Configure it for your context.
- If no system exists, build it as a reusable service, not a one-off solution.
- One component or service handles many contexts via configuration. Never fork code for different use cases - configure the same code differently.
- Duplication between features means a shared system should be extracted.
- Duplication between what the project does and what a market platform does means the project is building the wrong thing.
- Learning-project exception: if the user's stated goal is to learn a specific technology (not to ship a product), the external-reuse rule bends — the chosen technology IS the point. Scale-fit still matters (pick the cheapest way to exercise the tech). See `bootstrap/ONBOARD.md` Step 3 for the full flow.

## Violations

- Creating a custom error handler in a feature instead of using the centralized error service.
- Building a feature-specific loading spinner instead of using the unified loading components.
- Writing direct API calls in a feature instead of going through the API layer.
- Hardcoding values that should come from a configuration object.
- Building separate table components for each data type when one configurable table would serve all.
- Building anything without first checking what already exists.
- Building a custom CMS / blog platform when content-management vertical SaaS exists.
- Building a custom commerce platform when e-commerce vertical SaaS exists.
- Building a custom HIPAA patient portal when HIPAA practice-management vertical SaaS exists.
- Building a custom booking system when scheduling vertical SaaS exists.
- Scaffolding a greenfield custom app for any use case a vertical SaaS already solves end-to-end (research current options at bootstrap time; do not assume specific vendors).

## Wrong vs Right

- WRONG: each feature has its own error handling, its own API calls, its own loading spinner, its own validation logic. Five features means five different implementations of the same thing.
- RIGHT: one error system, one API layer, one set of loading components, one validation pattern. Five features all plug into the same systems with different configurations.
- WRONG: PharmacyTable, InsuranceTable, PhysicianTable as three separate components with 90% duplicate code.
- RIGHT: VendorTable configured with pharmacyConfig, insuranceConfig, physicianConfig. One component, three configurations.
- WRONG: "I want a therapy practice app" → scaffold a HIPAA patient portal from scratch (auth, document storage, BAA, encryption, intake forms, notes, scheduling) when HIPAA practice-management vertical SaaS solves 80%+ out of the box.
- RIGHT: "I want a therapy practice app" → research current HIPAA practice-management platforms; recommend the one that fits the practice size and clinical workflow; build custom only for product-unique logic on top.
- WRONG: "I want a personal blog" → stack with caching layer + relational DB + container orchestration for 5 readers.
- RIGHT: "I want a personal blog" → a content-management vertical SaaS, or a static-site generator deployed anywhere.
- EXCEPTION: "I want a personal blog AS a project to learn [enterprise technology]" — the technology choice IS the point. Custom overkill stack is correct when learning is the explicit goal. Still pick the cheapest local tier to exercise the target tech (research current local-dev options for the technology). Full flow: `bootstrap/LEARNING-PROJECTS.md`.

## Research Notes

When bootstrapping, for each convention in this framework, the bootstrapper should:
- Design the foundational system as a reusable service with a configuration API
- Research the framework's recommended patterns for building reusable, config-driven services
- Research factory patterns and dependency injection patterns specific to the chosen framework
- Ensure every system can be imported and used by any feature with minimal setup
