# Repository ownership and adoption

Framework-managed in downstream installations. Local AI must not edit this file; the next framework update overwrites it. Put project choices in References.md and propose shared changes upstream.

Read [ONBOARD.md](ONBOARD.md), [project setup](../conventions/01-project-setup.md), and [Git conventions](../conventions/02-git.md). Resolve these decisions from the owner's request and existing project evidence rather than repeatedly interviewing for known answers.

Before creation, identify the product, repository owner, visibility, lifecycle, and existing source. Check that the intended repository does not already exist and that the authorized actor can create it. A platform code repository holds the platform's implementation; repositories managed by that platform retain their own ownership and history. Repository permission is not implied by a task mentioning its name.

Use separate repositories for independent ownership or release boundaries. Use project/workspace configuration to associate several repositories with one initiative. Branches represent bounded proposed changes within a repository; they do not segregate confidential team knowledge. Prefer short task branches and isolated worktrees for concurrent edits. Do not create a permanent branch or fork merely to give a team its own context.

For an existing project, preserve its Git history and use injection. Never replace its repository with a clone of the framework. Inventory instruction files, overrides, docs, checks, and deploy triggers first. Back up original instructions, extract their full substantive guidance, and route project-specific rules from local files. Do not silently remove guidance or disable checks to make adoption pass.

Install shared instructions from the authoritative framework revision. Keep project facts, credentials, task IDs, platform endpoints, and execution capability declarations outside the managed engine. Record the source and installed revision in the project's version log. Source pointers must be sufficient to refresh the installation without maintaining another copy of the rules by hand.

Create References.md, feature-tree.md, and a project-root protocols/task-context.md binding using [the task template](../templates/task-context.md). State which systems are only planned. A missing task service does not block documentation planning; name the local planning source explicitly. Once a task service is canonical, its outage cannot create a second authority.

Before scaffolding, complete the relevant discovery, project-shape, and design gates from ONBOARD.md. Application name alone does not choose a playbook: a custom management application with frontend/backend code is a custom software product, not the externally hosted platform configuration path.

Verify installed rules, preserved guidance, context routing, version provenance, and a clean startup for a fresh worker. Record any missing runtime enforcement as implementation work. Installing instructions does not implement permission checks, automatic fleet updates, or freshness enforcement.
