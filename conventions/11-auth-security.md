# Convention #11: Auth & Security

## Principle

Authentication and security are handled through one centralized system. Features never implement their own auth logic, token management, or security checks. The auth system handles identity, the authorization layer handles permissions, and security conventions are enforced at the infrastructure level, not scattered across features.

AI-era reasoning: AI generates 2.74x more security vulnerabilities than human code. It hardcodes secrets, skips CSRF protection, and reimplements auth logic in multiple files. Security rules must be explicit and enforced, not assumed.

## Reusable System

- Auth service: token management (storage, refresh, rotation, logout cleanup)
- Auth utility: single function to get authenticated user identity from request
- Auth context/provider: makes auth state available throughout the app
- Route guard: protects routes that require authentication
- Authorization checks: permission verification at the service layer
- Security headers: CSP, HSTS, CORS configuration
- Input sanitization: centralized validation at system boundaries

## Rules

- Use the project's auth utility to get user identity. Never extract from JWT claims directly.
- Store tokens in httpOnly cookies. Never in localStorage.
- Never hardcode secrets, API keys, credentials, or environment-specific URLs.
- Never put secrets in client-side code or environment variables exposed to the browser.
- Authorization checks happen at the service layer, not in handlers or components.
- Object access checks: always verify the user owns or has access to the resource.
- Validate all external input at boundaries with schema validation.
- Never use dangerouslySetInnerHTML, eval(), or new Function().
- Use presigned URLs for file operations. Never proxy files through handlers.
- Sanitize user input before rendering in the UI.

## Violations

- Using claims.sub (OAuth provider ID) as a database user ID
- Storing JWT in localStorage
- Hardcoded API keys in source code
- Auth checks only in the UI (bypassed by API calls)
- Missing CSRF protection on state-mutating endpoints
- `dangerouslySetInnerHTML` with unsanitized user content
- Accepting userId from request body instead of deriving from auth

## Right vs Wrong

```
WRONG (extracting from JWT directly):
const claims = requireAuth(event)
const userId = claims.sub  // This is OAuth provider ID, NOT database ID!

RIGHT (using auth utility):
const { userId } = await getAuthenticatedUser(event)  // Returns database UUID
```

```
WRONG (token in localStorage):
localStorage.setItem('token', jwt)
fetch('/api', { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }})

RIGHT (httpOnly cookie):
// Token is in httpOnly cookie, attached automatically by browser
// Auth interceptor handles refresh silently
fetch('/api', { credentials: 'include' })
```

```
WRONG (auth check only in UI):
{user.isAdmin && <DeleteButton />}  // API still accessible without this check

RIGHT (auth check at service layer):
// Service layer verifies permissions regardless of UI
if (!await hasPermission(userId, 'delete', resourceId)) {
  throw new ForbiddenError('Not authorized to delete this resource')
}
```

## References.md Section

- Auth utility: path and what it returns
- Token strategy: how tokens are stored and refreshed
- Route guard: path to component and usage
- Authorization: where permission checks live
- Critical auth lessons: production bugs and rules that prevent them
- Security headers: where CSP/CORS/HSTS are configured
