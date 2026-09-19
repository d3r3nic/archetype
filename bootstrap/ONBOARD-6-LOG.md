# Bootstrap: logging the bootstrap

Part of the bootstrap playbook (bootstrap/ONBOARD.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step: read it when the script names it, with the reading it lists, and close it before opening the next.

## Step 6: Log the Bootstrap
Read: none
Produces: the bootstrap entry in VERSION-LOG.md at the project root, with any open pre-production gate (an unanswered regulated-data question) named in it
Check: run scripts/check-exists.sh VERSION-LOG.md

After bootstrap completes, update VERSION-LOG.md (at the **project root**, not inside archetype/ — the version log is project-owned, and framework updates overwrite the engine) to record what was done. If VERSION-LOG.md doesn't exist, create it.

Append a bootstrap entry:

```
## Bootstrap

Date: [today's date]
Type: [template / product / existing-project-migration]
Tech stack: [the tech stack chosen]
Profile: [operating stage], decision authority [owner-decides / ai-decides] ([owner-stated / defaulted]), facts still unknown: [list or none]
Files generated:
- References.md ([word count] words)
- PROFILE.md ([operating stage], [number of facts still unknown] unknown)
- feature-tree.md ([number of systems] systems, [number of features] features)
- [for existing projects] conventions/overrides/ ([number] files)
- [for existing projects] protocols/ ([number] files)
- [for existing projects] catalogs/ ([number] files)
- [for existing projects] docs/migrated/ ([number] files copied)
- [for existing projects] docs/audit/ ([number] audits, [summary: clean/minor/major/stale])
Conventions read during bootstrap: [list which convention docs were read]
Discovery: [PROGRESS.md steps 2.1 to 2.7 hold the questions and the owner's answers in their words; name here only what is still unknown or declined]
Key decisions made: [any tech stack choices, systems included/excluded, overrides noted]
```

This log ensures a future AI or developer can see exactly what happened during bootstrap, what was generated, and what decisions were made.
