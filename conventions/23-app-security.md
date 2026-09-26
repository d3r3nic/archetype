# Convention #23: Application Security

## Applies when

Every project. The floor in #30 applies whenever the protected asset or the hazardous capability exists. What varies by shape: what the product exposes (a service on a network, pages served to browsers, a device app, a local tool), what data it holds, and which regimes apply to that data (#30). Browser-specific protections apply to products that browsers load.

## Principle

Security is a property of every feature, not a feature. Every input from outside is validated, every output is encoded for where it goes, every secret is managed and never written into code, and every error hides the system's internals. The security system is shared: features use one validation, one output encoding, one secret source and one audit trail. They never build their own.

## Reusable System

The security foundation, sized to what the product exposes:
- Input validation at every entry point, allowlisting the fields each accepts (#7).
- Output encoding for every destination (pages, queries, commands, files); raw markup is rendered only after sanitizing.
- Secrets from the environment or a secret store, never from code.
- For products browsers load: the security headers current guidance recommends, an explicit list of allowed cross-origin callers, and protection of state-changing requests from cross-site forgery.
- Rate limiting on public and authentication endpoints, and on anything expensive, when the product is reachable by people outside the owner's control.
- An audit trail kept separate from application logs when regulated data or a commitment requires one (#30, B4).

References.md records each piece and where it lives.

## Rules

- Validate all outside input where it enters. Permit known fields only; never pass raw input to storage, queries, templates or commands.
- Encode output for its destination. Never render people's content as raw markup unless it is sanitized first.
- Never write a secret into code or commit one. Secrets come from the environment or a secret store, and are replaced when they may have leaked.
- Never show internal details to callers: no stack traces, storage errors, file paths or internal identifiers. Log them with a correlation identifier and return a plain message carrying that identifier.
- Encrypt connections that carry anything sensitive.
- Encrypt sensitive data at rest, and give the most sensitive fields their own protection when the facts call for it (#30).
- Check dependencies for known vulnerabilities in the project's checks, keep a lock on exact versions, and review a new dependency before adding it.
- Record security-relevant events: sign-in attempts, access denials, access to sensitive records, administrative actions, configuration changes.
- Handle personal data by the rules that apply to it: collect the minimum, set retention, provide deletion and export, and keep it out of logs and non-production copies (#30).

## Violations

- An endpoint that passes an unvalidated body to storage.
- People's content rendered as raw markup without sanitizing.
- A browser-served product with no security headers, or one that accepts credentialed requests from any origin.
- A public sign-in with no limit on attempts.
- A secret in source code or in history.
- A production error that shows a stack trace or a connection address.
- Sensitive records stored unencrypted.
- No record of who changed or deleted sensitive data.

## Wrong vs Right

- WRONG: an endpoint passes the request body straight into a query, and crafted input rewrites it. RIGHT: the endpoint validates against its allowlist, drops unknown fields, and passes clean data to its owner.
- WRONG: a production error returns the exception, the source file and the line. RIGHT: it returns a plain message and a request identifier; the details are in the log under that identifier.
- WRONG: an environment file with the production database password is committed. RIGHT: an example file lists the variable names and what they are for; the values live in the environment or a secret store, and a check keeps secrets out of commits.

## Research Notes

Research the current security guidance for what the product exposes, the chosen stack's validation, encoding, header and rate-limiting options, dependency scanning for its package manager, encryption and key management for its storage, and the rules for the data it holds (#30). Record each piece of the security foundation in References.md.
