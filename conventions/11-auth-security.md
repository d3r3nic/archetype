# Convention #11: Authentication

For authorization (who may do what), see convention #24. For application security, see convention #23.

## Applies when

The product has accounts, or anything behind a sign-in: people, devices or other services proving who they are. What varies: where the product runs (a web page, a device app, a server, a command-line tool), who provides identity (the product itself or an outside provider), and how sessions last.

## Principle

One owner answers "who is this?", and it is the only way any code learns the caller's identity. Identity always comes from the authenticated session, never from what the caller sends in a request. Credentials are kept where only the code that needs them can read them, and signing out removes everything that grants access.

## Reusable System

The auth owner: it manages the credential lifecycle (storage, renewal, revocation, sign-out), maps the provider's identity to the project's own record of the person, and exposes that identity to the rest of the code. References.md records where it lives, the provider, how credentials are stored and renewed, and how protected parts are guarded. § Boundaries keeps other code from reading credentials or the provider directly.

## Rules

- Get the caller's identity only from the auth owner. Never read it from tokens, claims or cookies elsewhere, and never accept it from a request body or parameter.
- The provider's identifier for a person is not the project's identifier. The auth owner maps one to the other. Mixing them up has broken production systems.
- Store credentials where only the code that needs them can read them: in a web page, out of storage every script on the page can read; on a device, in the platform's secure store; on a server, in its session store.
- Features use the auth owner, never the provider's library directly. Changing providers changes one place.
- Signing out clears every credential, session, cached identity and stored access state.
- Guards in the interface help people; the server checks every request (#21, #24).

## Violations

- Identity taken from a request body, a parameter or an unverified claim.
- The provider's identifier used as the project's record identifier.
- Credentials kept where any script, other app or log can read them.
- Features calling the identity provider directly.
- A sign-out that leaves a token, a session or cached identity behind.

## Wrong vs Right

- WRONG: a handler takes the identifier from the token and queries records with it; every query returns nothing, because the records use the project's own identifiers. RIGHT: the auth owner maps the provider's identifier to the project's record, and handlers use that.
- WRONG: a web page keeps its session token where any script on the page, including a third party's, can read it. RIGHT: the token lives where page scripts cannot reach it, and the browser sends it with requests.
- WRONG: twenty features call the provider's library; changing providers means changing all twenty. RIGHT: they call the auth owner; changing providers changes one place.

## Choosing a provider

The framework prescribes no provider. The categories to weigh: identity bundled with a managed data service, a hosted identity service, an enterprise single-sign-on broker, a cloud platform's identity service, the identity built into the chosen stack, and, last, one built by the project. Match scale, compliance obligations (#30) and who will run it. Whatever is chosen sits behind the auth owner.

## Research Notes

Research the providers that fit the project's scale, obligations and cost, the chosen stack's secure credential storage and renewal patterns, and how the provider's library can sit behind one owner. Record the provider, the credential strategy, the identity mapping and any production lessons in References.md, and the boundary in § Boundaries.
