# Convention #7: Type Safety & Type System

## Principle

The type system is the first line of defense against bugs and the primary documentation for AI. Strict typing eliminates entire categories of runtime errors. Types at boundaries (API responses, user input, env vars) are validated at runtime with schema libraries. Richer types produce better AI output because they communicate contracts explicitly.

AI-era reasoning: types are executable documentation for AI. Strong type systems reduce ambiguity in specifications, helping AI produce correct implementations. TypeScript adoption correlates with better AI code quality.

## Reusable System

- Strict tsconfig: project-wide TypeScript configuration
- Shared type definitions: common types used across features
- Validation schema library: Zod/Valibot schemas that infer TypeScript types
- Branded ID types: prevent mixing structurally identical IDs (UserId vs OrderId)

## Rules

- Enable strict mode in tsconfig.
- Never use `any`. Use `unknown` and narrow with type guards.
- Validate unknown data at boundaries (API responses, user input, env vars) with runtime schemas.
- One schema = types + validation. Zod/Valibot schemas infer TypeScript types automatically.
- Explicit return types on public/exported functions.
- Use discriminated unions for variants with a shared literal field.
- Use branded types for IDs to prevent accidental misuse.
- No type assertions (as) unless truly necessary and commented why.

## Violations

- `any` anywhere in production code
- API response used without validation (trusting external data)
- Separate type definition AND validation schema for the same data (they should be one)
- Type assertion (`as`) to silence a real type error instead of fixing it
- Non-null assertion (`!`) to bypass null checks instead of handling null
- Missing return type on exported function

## Right vs Wrong

Examples are illustrative.

```
WRONG (any to silence errors):
function processData(data: any) {
  return data.items.map((item: any) => item.value);
}

RIGHT (unknown + runtime validation):
function processData(data: unknown): number[] {
  const parsed = DataSchema.parse(data);
  return parsed.items.map(item => item.value);
}
```

```
WRONG (duplicate type + schema):
interface User { id: string; name: string; email: string; }

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string(),
});

RIGHT (single source of truth):
const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
});
type User = z.infer<typeof UserSchema>; // derived automatically
```

```
WRONG (assertion to bypass real error):
const user = apiResponse as User;          // trusting external data
const el = document.getElementById('x')!;  // assuming it exists

RIGHT (validate and narrow):
const user = UserSchema.parse(apiResponse);         // throws if invalid
const el = document.getElementById('x');
if (!el) throw new Error('Element not found');
```

## References.md Section

- tsconfig: any project-specific strict settings
- Validation library: which one (Zod, Valibot, etc.)
- Shared types: where common types live
- import type: whether project uses verbatimModuleSyntax
- Branded types: where ID types are defined
