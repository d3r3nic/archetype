# Convention #3: Code Architecture & Patterns

## Principle

Code is organized in layers with clear boundaries. Each layer has one job. Handlers/controllers are thin entry points. Services contain business logic. Data access is abstracted. Features are self-contained and never import from each other. When code needs to be shared, it moves to a shared layer explicitly.

## Reusable System

- Service layer: business logic services that features use
- Data access layer: ORM/query abstractions
- Shared utilities: cross-feature helpers in a dedicated location
- Module boundaries: barrel exports that define each module's public API

## Rules

- Handlers/controllers are thin. They parse input, call services, return responses.
- Business logic lives in services, not in handlers or components.
- Features are self-contained. They never import from other features.
- If code needs sharing across features, move it to shared/ (ask first).
- Duplication between features is better than coupling between features.
- Each module exports a public API through its index file. Internals are private.
- No circular dependencies. If A imports B, B must not import A.

## Violations

- Business logic in a handler/controller/component
- Feature A importing from Feature B's internals
- Circular dependency between modules
- Utility functions scattered across random locations
- No clear boundary between layers (everything mixed in one file)
- Over-specification: adding phantom requirements nobody asked for (batch mode, dry-run, legacy format)
- Hallucinated helpers: calling functions or modules that don't exist in the project
- Never refactoring: adding new code without consolidating existing code

## Right vs Wrong

Examples are illustrative.

```
WRONG (business logic in component):
function OrderPage() {
  useEffect(() => {
    fetch('/api/orders').then(data => {
      const filtered = data.filter(o => o.status !== 'cancelled');
      const sorted = filtered.sort((a, b) => b.date - a.date);
      const withTotals = sorted.map(o => ({
        ...o, total: o.items.reduce((sum, i) => sum + i.price * i.qty, 0)
      }));
      setOrders(withTotals);
    });
  }, []);
}

RIGHT (thin component, logic in service):
function OrderPage() {
  const { data: orders } = useOrders(); // hook uses service layer
  return <OrderList orders={orders} />;
}
// services/orderService.ts handles filtering, sorting, totals
```

```
WRONG (AI over-specifies with phantom requirements):
function createUser(data) {
  if (Array.isArray(data)) return data.map(createSingle); // nobody asked for batch
  if (data.dryRun) return simulate(data);                 // nobody asked for dry-run
  if (data.legacyFormat) return createLegacy(data);       // nobody asked for legacy
  return createSingle(data);
}

RIGHT (build what the spec says):
function createUser(data: UserInput): User {
  const validated = UserSchema.parse(data);
  return db.user.create({ data: validated });
}
```

## References.md Section

- Layer pattern: the project's specific layering (e.g., handler → service → db)
- Feature location: where feature code lives
- Shared location: where shared code lives
- Import rules: what can import from what
