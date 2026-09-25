# Bootstrap: hooks

## Step 5: Set Up Hooks (optional - can be done later)
Read: templates/hooks-spec.md; bootstrap/hooks/README.md
Produces: the framework's destructive-command guard, or the host's equivalent, installed for the working session
Check: evidence: which hooks were set up and where, and for the framework's guard what scripts/check-hooks.py reported
Depends on: bootstrap.4.3
Skip when: hooks are deferred to scaffolding, or the build approach is a platform

A hook runs on every trigger, whatever the session remembers. The framework ships one: a guard that blocks known-destructive shell commands before they run (templates/hooks-spec.md, bootstrap/hooks/README.md). Install it as the README says for the project's layout, run `scripts/check-hooks.py` from the project root, and fix what it reports before recording the step. Installing it, or deferring it to scaffolding, is a technical choice (#29), not a question for the owner.
