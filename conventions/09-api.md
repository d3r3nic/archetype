# Convention #9: API Integration & Data Fetching

## Principle

All communication with backends goes through one centralized API layer. Features never make direct HTTP calls. The layer handles authentication headers, request/response transformation, caching, deduplication, error normalization, and retry logic. Data fetching uses a server-state library that manages cache lifecycle automatically.

AI-era reasoning: AI scatters fetch calls across features with inconsistent headers, error handling, and caching. A single API layer forces consistency and prevents duplicate implementations.

## Reusable System

- API client: configured instance with base URL, interceptors, auth headers
- Request interceptors: attach tokens, transform outgoing data
- Response interceptors: normalize errors, transform incoming data
- Data fetching hooks: server-state library integration (cache, dedup, revalidation)
- Optimistic update utilities: immediate UI update with rollback on failure
- Pagination utilities: offset, cursor, and infinite scroll patterns

## Rules

- Never use raw fetch() or axios() in feature code. Use the API layer.
- All API functions live in a dedicated API directory or feature API file.
- Name API functions by domain action: getUser(), createOrder(), not fetchData().
- Transform data at the API boundary. Convert snake_case to camelCase at the layer, not in features.
- Parse dates at the API boundary. Features receive Date objects, not strings.
- Cache strategy is configured once in the API layer, not per feature.
- Invalidate cache only when the user stays on the same page and expects instant updates. If user navigates after mutation, the next mount auto-refetches.
- Type every request and response. No untyped API calls.

## Violations

- `fetch('/api/users')` directly in a component
- Different base URLs or auth header logic in different features
- Transforming API response format inside feature components
- Manual cache management (localStorage, useState) instead of using the server-state library
- Untyped API responses (`any` or missing types)

## Right vs Wrong

```
WRONG (direct fetch in component):
const Component = () => {
  const [data, setData] = useState(null)
  useEffect(() => {
    fetch('/api/users', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(d => setData(d))
      .catch(e => console.log(e))
  }, [])
}

RIGHT (API layer + server-state library):
// api/users.ts
export const userApi = api.injectEndpoints({
  endpoints: (build) => ({
    getUsers: build.query<User[], void>({
      query: () => '/users',
    }),
  }),
})

// Feature component
const { data, isLoading, error } = useGetUsersQuery()
```

## References.md Section

- API client: path to configured instance
- Base URL: how it's configured (env var)
- Auth: how tokens are attached (interceptor)
- Cache strategy: which strategy and configuration
- API file pattern: where feature API definitions live
- Data transformation: where snake_case/camelCase conversion happens
