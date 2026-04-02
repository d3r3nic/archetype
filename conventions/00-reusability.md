# Convention #0: Reusability & Composition (META)

## Principle

Everything is built once and configured for context. This governs how every other convention is implemented. When any convention is applied, it produces one reusable foundational system. Features plug into systems, never build ad-hoc. AI duplicates more than humans - one reusable source prevents drift.

## Reusable System

This convention doesn't produce a single system. It governs HOW all systems are built. Every other convention in this framework produces a foundational system following these rules:
- Every system is config-driven. It accepts configuration objects, not hardcoded values.
- Every system has one location in the codebase. Single source of truth.
- Every system is usable by any feature through simple imports and configuration.
- When the same logic appears in two places, that's a signal a reusable system is missing.

## Rules

- Before building anything, read feature-tree.md to see what systems and features already exist.
- If a system exists for what you need, use it. Configure it for your context.
- If no system exists, build it as a reusable service, not a one-off solution.
- One component or service handles many contexts via configuration. Never fork code for different use cases - configure the same code differently.
- Duplication between features means a shared system should be extracted.

## Violations

- Creating a custom error handler in a feature instead of using the centralized error service.
- Building a feature-specific loading spinner instead of using the unified loading components.
- Writing direct API calls in a feature instead of going through the API layer.
- Hardcoding values that should come from a configuration object.
- Building separate table components for each data type when one configurable table would serve all.
- Building anything without first checking what already exists.

## Wrong vs Right

- WRONG: each feature has its own error handling, its own API calls, its own loading spinner, its own validation logic. Five features means five different implementations of the same thing.
- RIGHT: one error system, one API layer, one set of loading components, one validation pattern. Five features all plug into the same systems with different configurations.
- WRONG: PharmacyTable, InsuranceTable, PhysicianTable as three separate components with 90% duplicate code.
- RIGHT: VendorTable configured with pharmacyConfig, insuranceConfig, physicianConfig. One component, three configurations.

## Research Notes

When bootstrapping, for each convention in this framework, the bootstrapper should:
- Design the foundational system as a reusable service with a configuration API
- Research the framework's recommended patterns for building reusable, config-driven services
- Research factory patterns and dependency injection patterns specific to the chosen framework
- Ensure every system can be imported and used by any feature with minimal setup
