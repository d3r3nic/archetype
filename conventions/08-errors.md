# Convention #8: Error Handling, Recovery & Async

## Principle

Errors are handled through one centralized system. Features never implement their own error catching, display, or recovery. The system handles classification, logging, user-facing messages, retry logic, and reporting. Async operations follow a consistent pattern with explicit loading, error, and success states.

AI-era reasoning: AI scatters try/catch blocks across features with inconsistent error messages and handling. A centralized system eliminates this by giving AI one place to route errors.

## Reusable System

- Error service: catches, classifies, logs, reports, and optionally retries
- Error classes: typed errors (NetworkError, ValidationError, NotFoundError, AuthError)
- Error boundaries: at app, route, and feature levels
- Error UI components: fallback, empty state, offline state, 404
- Loading components: unified loading states (full screen, inline, skeleton)
- Retry utility: exponential backoff for transient failures

## Rules

- Never scatter try/catch across features. Use the centralized error system.
- Never create custom loading spinners per feature. Use unified loading components.
- Every async operation has three states: loading, error, success.
- Empty state is not error state. Distinguish "no data" from "failed to load."
- User-facing error messages are friendly and actionable. No stack traces in UI.
- Technical details go to logs and error reporting, not to the user.
- Retry transient errors (5xx, network) with exponential backoff. Never retry 4xx (except 429).
- Use AbortController to cancel async operations on unmount or navigation.
- Never swallow errors. Every catch must log, re-throw, or handle meaningfully.
- No floating promises. Every promise is awaited, returned, or explicitly voided.

## Violations

- try/catch in feature code when the framework already wraps handlers
- Custom error UI in a single feature instead of using the shared error components
- `catch(e) { console.log(e) }` with no user feedback or reporting
- `catch(e) {}` empty catch blocks
- Showing `Error: ECONNREFUSED` to the user instead of a friendly message
- Different loading spinner in every feature
- Missing loading or error state on async operations

## Right vs Wrong

```
WRONG (scattered, inconsistent):
// Feature A
try { await fetchUsers() } catch(e) { alert('Error!') }

// Feature B
try { await fetchOrders() } catch(e) { console.log(e) }

// Feature C
try { await fetchProducts() } catch(e) { setError(true) }

RIGHT (centralized system):
// Features don't handle errors. The system does.
const { data, isLoading, error } = useQuery('users', getUsers)

if (isLoading) return <LoadingSpinner />
if (error) return <ErrorState error={error} retry={refetch} />
if (!data.length) return <EmptyState message="No users found" />
return <UserList data={data} />
```

```
WRONG (custom error UI per feature):
// FeatureA/ErrorMessage.tsx
// FeatureB/ErrorDisplay.tsx
// FeatureC/FailureNotice.tsx

RIGHT (shared error components):
import { ErrorState, EmptyState, LoadingSpinner } from '@/shared/ui'
```

## References.md Section

- Error service: path and usage pattern
- Error classes: available error types and when to use each
- Error boundaries: where they are placed (app/route/feature)
- Error UI components: path to fallback, empty, offline, loading components
- Error reporting: which service (Sentry, etc.) and configuration
