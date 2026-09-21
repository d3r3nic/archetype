# Bootstrap: the Design Artifact section

## Step 4.5: The Design Artifact section
Read: #27 § Design tools; templates/design-artifact-entry.md
Produces: every labelled line of References.md § Design Artifact filled in: from discovery (`Primary context`, `Committed contexts`, `First task`, `Return tasks`, `Session length`), from the interview (`Density`, `Vocabulary`, `Brand book`, `Brand decided`), and from the tool research; a path the scaffold will create is recorded as the path it will have
Check: run scripts/validate-design.sh --required known-screen
Depends on: bootstrap.4.4
Basis: decisions and inputs required
Skip when: the project has no screen (a platform, or a back end alone)

A template keeps every labelled line. Record `Brand decided: deferred to downstream projects`, retain a working-files location for structural design work, and use neutral values so downstream products choose their own identity. A product records the settled or honestly open direction from the interview. These mechanics belong here, after the project shape and build approach are known.

Use the same current decision basis as the interview, and the canonical brief/artifact files as `--input` values when closing. Declare the committed context and scheme decisions too when settled. Avoid hashing all of References.md as one input: scaffold will fill unrelated implementation fields. A replaced choice is recorded as a superseding decision and reopens its dependent work through development/STEPS.md. Templates keep their neutral design and accepted scope basis.
