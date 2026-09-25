# Bootstrap: logging the bootstrap

## Step 6: Log the Bootstrap
Read: none
Produces: the Bootstrap section of VERSION-LOG.md at the project root, completed, with any open pre-production gate (an unanswered regulated-data question) named in it
Check: run scripts/validate-bootstrap.py log; evidence: the bootstrap record names unresolved facts and open pre-production gates, or explicitly records none
Depends on: bootstrap.4.5; bootstrap.4.3; bootstrap.5

After bootstrap completes, record what was done in VERSION-LOG.md (at the **project root**, not inside archetype/ — the version log is project-owned, and framework updates overwrite the engine).

The installer wrote the log's `## Bootstrap` section with its install lines (Date, Source, Commit, Method). Complete that section: keep those lines and add the lines below under them, completing a line that is already there instead of repeating it. If the section has no Date, or its Date says unknown, write today's date there, in year-month-day form. Update entries stay under `## Updates`, and setup adds no second Bootstrap section; where a log already has two, complete the later one. A project without the file creates it in that shape: a `# Version Log` heading and a line saying what each section records, the `## Bootstrap` section with the date and the lines below, then an empty `## Updates` section.

```
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
Key decisions made: [links to the canonical decisions, not copied reasons]
Open pre-production gates: [each unresolved gate and its recorded facts, or none]
```

This log ensures a future AI or developer can see exactly what happened during bootstrap, what was generated, and what decisions were made.
