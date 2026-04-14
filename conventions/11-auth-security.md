# Convention #11: Authentication

For authorization (permissions, RBAC, access checks), see convention #24.
For application security (OWASP, CORS, encryption, headers), see convention #23.

## Principle

Authentication is handled through one centralized system. Features never implement their own auth logic or token management. The auth system handles identity: who is this user? A single auth utility is the ONLY way to get the authenticated user. Features call this utility, never parse tokens or read cookies directly.

## Reusable System

Create an auth and security system that establishes:
- An auth service that manages the full token lifecycle: secure storage, automatic refresh before expiry, rotation for stolen token detection, and complete cleanup on logout
- An auth utility function that is the ONLY way to get the authenticated user's identity. Features call this one function. They never parse tokens, read cookies, or extract claims directly.
- An auth context or provider that makes auth state available throughout the application without prop drilling
- Route or endpoint protection that redirects unauthenticated users and checks permissions before executing protected actions
- Authorization checks at the service layer, not at the UI or handler layer. UI can hide buttons, but the service layer enforces whether the action is actually allowed.
- Input validation and sanitization at all entry points. Never trust user input.
- Security headers configured at the infrastructure level (content security policy, transport security, CORS)

## Rules

- Use the project's auth utility to get user identity. Never extract identity from tokens, claims, or request bodies directly. The auth utility returns a database ID, not an auth provider ID. This distinction has caused production bugs.
- Store tokens securely. Never in client-accessible storage like localStorage. Use httpOnly cookies or secure server-side sessions.
- Never hardcode secrets, API keys, credentials, or environment-specific URLs in source code.
- Never put secrets in client-side environment variables. Server secrets stay on the server.
- Authorization checks happen at the service layer, not just the UI. A hidden button is not security. The service must verify permission before executing.
- Object access checks: always verify the user owns or has access to the resource before returning it. A user should not be able to access another user's data by guessing an ID.
- Validate and sanitize all user input at entry points. Never render unsanitized user content.
- Use presigned URLs or equivalent for file operations. Never proxy file content through your application servers.

## Violations

- Using the auth provider's ID (like a Cognito sub or OAuth provider ID) as the database user ID. They are different things. This broke production.
- Storing tokens in localStorage or sessionStorage (accessible to any script on the domain)
- Hardcoded API keys, secrets, or database credentials in source code
- Auth checks only in the UI (hidden button but unprotected API endpoint)
- Missing object access checks (user can access another user's data by changing an ID in the URL)
- Rendering unsanitized user content in the UI
- Accepting user identity from the request body instead of deriving it from the authenticated session

## Wrong vs Right

- WRONG: a handler reads the user ID from the token claims and uses it as the database ID. The token claim is the auth provider's ID, not the database UUID. All queries return zero results.
- RIGHT: a handler calls the auth utility, which looks up the auth provider ID in the database and returns the database UUID. All queries work correctly.
- WRONG: auth check is only a hidden button in the UI. A user inspects the page, finds the API endpoint, calls it directly, and gets admin-level access.
- RIGHT: the UI hides the button AND the service layer verifies the user has admin permission before executing the action. Direct API calls are also rejected.
- WRONG: tokens stored in localStorage. A third-party script (analytics, ad tracker) on the page can read them.
- RIGHT: tokens stored in httpOnly cookies that JavaScript cannot access. The browser sends them automatically on requests.

## Common Auth Providers

The framework doesn't prescribe a specific provider. Bootstrap picks based on your context:

- Supabase Auth: bundled with Supabase DB, drop-in for small teams, generous free tier
- Clerk: best React developer experience, fast setup, usage-based pricing
- Auth0: mature, enterprise features, expensive at scale
- AWS Cognito: AWS-native, cheap at scale, rougher developer experience, HIPAA eligible
- Firebase Auth: Google ecosystem, good for mobile
- ASP.NET Identity / Django auth: framework-native, no external dependency
- Custom JWT: only if you truly know why. Most teams should not build their own auth.

Whatever you choose, wrap it in a project auth utility per this convention's Rules section. Features never import the provider's SDK directly.

## Research Notes

When bootstrapping this convention:
- Research auth providers suitable for the project's scale, compliance needs, and team experience
- Research the framework's recommended token storage patterns (httpOnly cookies vs in-memory)
- Research silent token refresh patterns for the framework
- Research the provider's SDK and how to wrap it behind a project auth utility
- Document the auth utility, token strategy, route protection, and provider choice in References.md. Include any production lessons about identity (provider ID vs database ID).
