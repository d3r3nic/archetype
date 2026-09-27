# Bootstrap: an existing project

## Step 4.1: Existing project: scan, extract, migrate
Read: bootstrap/EXISTING-PROJECT.md
Produces: MIGRATION-NOTES.md mapping each original rule to its one home, the project-root CLAUDE.md.additions and any override or protocol files the rules moved into, and the References.md and feature-tree.md the adoption writes from what it found, with the Peer coding line (and peer-coding/SETTINGS.md when the owner chose peer coding)
Check: run scripts/validate-migration.sh
Depends on: bootstrap.3
Skip when: the project is new and has no code or guidance of its own

The adoption flow (what exists, the owner's rules, the project's documents) lives in `bootstrap/EXISTING-PROJECT.md`. Follow it end to end; it writes References.md and feature-tree.md itself, so Step 4.2 is skipped for an existing project. PROFILE.md and the design steps below still run, with what adoption found.

**Critical:** adoption loses nothing the owner wrote and keeps one home per rule. The check fails when References.md, feature-tree.md or the map (MIGRATION-NOTES.md; an adoption under an earlier version may keep it in INDEX.md) is missing, or when the owner's peer-coding answer is not recorded, and it says whether earlier entry files were preserved. Whether every rule found its home is the walk through each original that the flow describes, and the independent review reads the map.
