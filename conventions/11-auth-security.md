# Convention #11: Auth & Security

## Principle

Authentication and security are handled through one centralized system. Features never implement their own auth logic, token management, or security checks. The auth system handles identity, the authorization layer handles permissions, and security rules are enforced at the infrastructure level, not scattered across features. AI generates 2.74x more security vulnerabilities than human code - security rules must be explicit.

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

## Research Notes

When bootstrapping this convention:
- Research the framework's recommended authentication patterns. How should tokens be stored securely? How should silent refresh work?
- Research the framework's authorization patterns. Where should permission checks happen? How do you protect routes or endpoints?
- Research security header configuration for the framework's deployment target (content security policy, strict transport security, CORS)
- Research input validation and sanitization libraries for the framework
- Research file handling security patterns (presigned URLs, upload verification)
- Document the auth utility, token strategy, route protection, and authorization patterns in References.md. Include any production lessons about identity (provider ID vs database ID).
