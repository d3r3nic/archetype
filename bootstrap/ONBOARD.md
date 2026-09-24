# Phase 1: Bootstrap

Onboard a project into the framework. Run once at project creation or when adopting the framework on an existing project.

Step ledger: bootstrap
Step files: bootstrap/ONBOARD-2.1-WHAT-IS-IT.md; bootstrap/ONBOARD-2.2-WHERE-IT-RUNS.md; bootstrap/ONBOARD-2.3-WHAT-USERS-DO.md; bootstrap/ONBOARD-2.4-SCALE.md; bootstrap/ONBOARD-2.5-SENSITIVITY.md; bootstrap/ONBOARD-2.6-CARE-AND-AUTHORITY.md; bootstrap/ONBOARD-2.7-READ-TOGETHER.md; bootstrap/ONBOARD-3-RESEARCH.md; bootstrap/ONBOARD-4.1-EXISTING-PROJECT.md; bootstrap/ONBOARD-4.2-REFERENCES.md; bootstrap/ONBOARD-4.3-PROFILE.md; bootstrap/ONBOARD-4.4-DESIGN-INTERVIEW.md; bootstrap/ONBOARD-4.5-DESIGN-ARTIFACT.md; bootstrap/ONBOARD-5-HOOKS.md; bootstrap/ONBOARD-6-LOG.md

## Prerequisites

Establish the owner's intended outcome before initialization. Keep the technical approach open for Step 3 research unless the project already has an accepted commitment.

## Step 1: Initialize Project
Read: bootstrap/REPOSITORIES.md
Produces: the project folder with the engine in it (AGENTS.md, CLAUDE.md, Conventions.md, the conventions and playbook folders, unmodified); PROGRESS.md at the project root
Check: evidence: where the engine sits (the project root, or which subfolder), and the repository decision with its reason

Read [REPOSITORIES.md](REPOSITORIES.md) before creating a repository or installing the framework. Preserve an existing repository's history and local guidance; use the injection path when the project already exists.

Choose the installation path that fits the repository facts established from `bootstrap/REPOSITORIES.md`. Preserve repository history and existing guidance. The commands below are implementation examples; resolve current source locations before running them.

### For a NEW project (engine folder in an empty project folder):

Create the project folder and install the engine into it, the same way an existing project is installed. The project root stays the project's own (its README, its license, its scripts); the framework lives in `archetype/`, and the two root entry files are managed copies.

```bash
git clone https://github.com/d3r3nic/archetype.git /tmp/archetype-framework
mkdir my-project-name
/tmp/archetype-framework/inject.sh "$PWD/my-project-name"

# Separate frontend and backend units, each with its own engine folder:
mkdir -p my-project/frontend my-project/backend
/tmp/archetype-framework/inject.sh "$PWD/my-project/frontend"
/tmp/archetype-framework/inject.sh "$PWD/my-project/backend"
```

A clone of the framework used as the project itself (the full-clone layout) is an older layout: the framework's own files and folders sit at the project root, so each update replaces them. Existing full-clone installs keep working; development/UPDATE.md says what an update does there.

### For an EXISTING project (inject as subfolder):

Use the inject script to install the framework as a subfolder. It replaces the managed root instruction files: existing guidance is backed up before replacement. A backup collision stops injection. Read and incorporate the preserved guidance into project-owned files during onboarding.

```bash
# Clone the framework somewhere if you don't have it locally
git clone https://github.com/d3r3nic/archetype.git /tmp/archetype-framework

# Inject into your existing project
cd /tmp/archetype-framework
./inject.sh /path/to/your/existing-project

# Default subfolder name is "archetype". To customize:
./inject.sh /path/to/your/existing-project archetype-migration
```

After injection, your existing project has a new subfolder (default `archetype/`) containing the framework. Root instruction files are managed copies; original guidance is preserved in .pre-archetype files. Other project files are preserved. The existing-project migration is Step 4.1 in the bootstrap sequence, after discovery and research; initialization continues below.

Then create the ledger: copy `templates/progress.md` to `PROGRESS.md` at the project root and write `bootstrap` on its Playbooks line. This step is the first one the ledger closes.

For separate frontend/backend units, preserve their project context and choose repository boundaries from bootstrap/REPOSITORIES.md. Separate runtime units do not by themselves require separate Git repositories.

## The steps

| Step | What it settles | File |
|---|---|---|
| 1 | The engine and the ledger are in place | this file |
| 2.1 to 2.6 | Discovery, one question group each, closed on the owner's words | bootstrap/ONBOARD-2.1-WHAT-IS-IT.md to bootstrap/ONBOARD-2.6-CARE-AND-AUTHORITY.md, each read with bootstrap/ONBOARD-DISCOVERY.md |
| 2.7 | The answers read together: needs, knowledge level, red-flag combinations | bootstrap/ONBOARD-2.7-READ-TOGETHER.md |
| 3 | Research, one recommendation, the build approach | bootstrap/ONBOARD-3-RESEARCH.md |
| 4.1 | An existing project's rules migrated (skipped for a new one) | bootstrap/ONBOARD-4.1-EXISTING-PROJECT.md |
| 4.2 | References.md and feature-tree.md | bootstrap/ONBOARD-4.2-REFERENCES.md |
| 4.3 | PROFILE.md | bootstrap/ONBOARD-4.3-PROFILE.md |
| 4.4 | The design interview (a product with a screen) | bootstrap/ONBOARD-4.4-DESIGN-INTERVIEW.md |
| 4.5 | The Design Artifact section | bootstrap/ONBOARD-4.5-DESIGN-ARTIFACT.md |
| 5 | Hooks (may be deferred) | bootstrap/ONBOARD-5-HOOKS.md |
| 6 | The bootstrap logged | bootstrap/ONBOARD-6-LOG.md |

## What Bootstrap Does NOT Do

- Does not create code or foundational systems (Phase 2: Scaffold)
- Does not modify existing code (for existing projects)
- Does not set up CI/CD (part of scaffolding)

Bootstrap generates the map. Scaffolding builds what the map describes.

## Next Step

Proceed to scaffolding/SCAFFOLD.md to build the foundational systems. When the scaffold playbook for this project's shape declares a step ledger, add its id after `bootstrap` on the Playbooks line of PROGRESS.md, and `scripts/next-step.sh` carries on from there.
