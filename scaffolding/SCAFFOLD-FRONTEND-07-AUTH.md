# Frontend scaffold: auth

Use scaffolding/SCAFFOLD-FRONTEND.md for this route and scaffolding/_preamble.md for shared scaffold guidance.

## Step 7: Auth
Read: #11; #24; scaffolding/_preamble.md § Convention-mapping rule
Produces: the auth owner, the session handling, the refresh or redirect on an expired session, and the identity line in References.md § Boundaries
Check: run project: typecheck, lint, build; evidence: what was seen when this was tried: login and logout end to end, and an expired token
Skip when: the product has no accounts and nothing behind a login

Apply #11 through the recorded provider decision:
- The auth owner: sign-in, credential storage as #11 says for a web page, renewal, complete sign-out and session restore, and the one way screens learn who is signed in.
- Record `` - Identity: `<the provider library's import pattern>` only in `<the auth owner's path>` `` in References.md § Boundaries, so features never call the provider directly.

**Verify:** sign-in and sign-out work end to end on a test page; an expired session renews or redirects to sign-in; after sign-out nothing that grants access remains.
