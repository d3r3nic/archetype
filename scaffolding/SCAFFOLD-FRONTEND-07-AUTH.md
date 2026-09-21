# Frontend scaffold: auth

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 7: Auth
Read: #11; #24; scaffolding/_preamble.md § Convention-mapping rule
Produces: the auth utility, the session handling, and the refresh or redirect on an expired token
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: login and logout end to end, and an expired token
Skip when: the product has no accounts and nothing behind a login

Build:
- Auth service wrapping the auth provider (token storage, refresh, logout cleanup, session restore).
- Features NEVER import the auth SDK directly — only the wrapper.
- Auth context/provider mounted at the app root.
- Token storage chosen securely (httpOnly cookie > localStorage for most cases; research current guidance).
- `useAuth()` / `getAuthenticatedUser()` utility.

**Verify:** login/logout flow in a test page works end-to-end; expired token triggers refresh or redirect.
