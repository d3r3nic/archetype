# Convention #0: Reusability & Composition

## Principle

Everything is built once and configured for context. This is the meta-convention that governs how every other convention is implemented. When any convention is applied to a project, it produces ONE reusable foundational system. Features never build ad-hoc solutions - they plug into existing systems.

This applies at every level: one theme system, one error system, one API layer, one auth system, one component foundation. The same thinking that makes a Button reusable also makes error handling reusable, makes theming reusable, makes validation reusable.

AI-era reasoning: AI agents duplicate logic across sessions because they lose context. A single reusable system is the map that prevents the AI from drawing a new one every time. Context engineering IS DRY enforcement.

## Reusable System

This convention doesn't produce a single system. It governs HOW all other systems are built:

- Every convention produces a foundational system at project creation
- Every system is config-driven (accepts configuration, not hardcoded values)
- Every system has one location (single source of truth)
- Every feature uses the system, never builds around it

## Rules

- Before building anything, ask: does a system for this already exist?
- If yes: use it. Configure it for your context.
- If no: build it as a reusable system, not a one-off.
- One component handles many contexts via configuration, not code forks.
- Same pattern at every level: UI components, services, utilities, infrastructure.
- Duplication is the signal that a reusable system is missing.

## Violations

- Creating a custom error handler in a feature instead of using the centralized error system
- Building a feature-specific loading spinner instead of using the unified loading component
- Writing ad-hoc fetch calls instead of using the API layer
- Hardcoding values that should come from configuration
- Creating a new table component when the existing one accepts config for different data types
- Building one-off form validation instead of using the form system

## Right vs Wrong

Examples are illustrative. See References.md for this project's specific implementation.

```
WRONG (one-off, scattered, duplicated):
// Feature A
try { const data = await fetch('/api/users') } catch(e) { alert('Error') }

// Feature B
try { const data = await fetch('/api/orders') } catch(e) { console.log(e) }

// Feature C
try { const data = await fetch('/api/products') } catch(e) { toast.error('Failed') }

RIGHT (one system, configured per context):
// Shared error system handles all errors consistently
// Shared API layer handles all requests consistently
// Features just use them:
const { data } = useQuery('users', getUsers)  // API layer handles fetch, cache, errors
```

```
WRONG (one-off component):
<PharmacyTable />    // only works for pharmacies
<InsuranceTable />   // duplicates 90% of PharmacyTable
<PhysicianTable />   // duplicates again

RIGHT (one component, configured):
<VendorTable config={pharmacyConfig} />
<VendorTable config={insuranceConfig} />
<VendorTable config={physicianConfig} />
```

## References.md Section

- Existing reusable systems: list of all foundational systems with locations
- Reference implementations: 2-3 features that demonstrate the pattern well
- Factory examples: config-driven components to study before building new ones
