# Phase 3: Develop

Build or change the behavior the owner needs using the project's researched foundations. Follow the recorded authority and existing contracts; revisit them deliberately when new evidence changes their basis.

## Prerequisites

- The applicable scaffold is complete and References.md records the chosen systems and verification commands.
- feature-tree.md provides a current map; verify relevant paths against source when needed.
- Required checks and profile obligations are resolved before claiming the feature complete.

## Relevant context

Use the root routing in AGENTS.md. Read the task's relevant project facts, contracts, conventions and development/RED-FLAGS.md sections; reuse unchanged context from this session. Tracked work also follows development/TASKS.md, development/FRESHNESS.md and the project-root protocols/task-context.md binding when present. Backend work consults backend/Conventions.md. This playbook currently uses the implementer-plan procedure in development/TASKS.md for sequencing and manual dependency review.

## Feature Development Workflow

### Step 1: Understand the change

Identify the intended behavior, constraints and observable success. Inspect affected code and the existing systems it can reuse; record dependencies that materially affect the plan. Do not enumerate every unrelated system or create an abstraction just to satisfy an inventory (#0, #3).

For screen work, read References.md's Design Artifact and its relevant brand, vocabulary, tokens, catalog and feature entries. If an applicable state or composition is missing, design and record it at decision fidelity before implementing it, using templates/design-artifact-entry.md. The session decides within the recorded direction; the owner decides changes to identity or purpose, or delegates the look explicitly (#27, #29). Preserve supplied access, language, spending and other requirements. A changed basis requires the dependency review in development/TASKS.md and reopening any affected declared ledger records through development/STEPS.md.

### Step 2: Investigate what could change the answer

Use Conventions.md to find the relevant concerns, including cross-cutting risks. There is no document quota. Research uncertain or changing facts that matter to the decision, compare viable alternatives and explain why the chosen approach fits. Reuse verified current evidence; record consequential choices at the existing decision location (#16). Do not make research a search for support for a predetermined answer.

### Step 3: Plan the affected work

Size the plan to uncertainty, coupling and consequence. For an obvious isolated edit the intended change and check may suffice. For a consequential change identify boundaries, affected consumers, verification and recovery. Avoid unrelated capabilities. Follow #19 and the decision authority in PROFILE.md: technical choices under ai-decides proceed within the granted scope; owner-decides plans require the recorded approval (#29).

### Step 4: Implement the chosen approach

Follow the project's accepted structure, lifecycle, error and logging contracts. Reuse a shared capability when it fits; investigate a mismatch before bypassing or replacing it. Select composition, configuration or separation for a concrete reason (#0, #3). Do not silently construct a separate instance when a shared owner controls lifecycle or configuration. Keep user input and external effects within the appropriate trust boundaries.

### Step 5: Verify behavior and relevant failure paths

Choose tests and observations from the promised behavior and risks (#12, #18). For authenticated endpoints, exercise rejection of unauthorized access, invalid input, successful use and relevant domain failures. Public endpoints do not need an invented authentication path. Jobs and internal services need evidence for their meaningful success and failure behavior. Add concurrency, recovery or boundary coverage where the domain needs it.

Use the project's test layout and isolation strategy. Shared test data must not make results depend on unrelated execution order; development/RED-FLAGS.md describes known isolation failures. The number or location of test files is not evidence that behavior is covered.

### Step 6: Run checks and review the result

Run the applicable verification commands in References.md, including the required tests and build checks. Run scripts/validate-profile.sh from the project root. Before increasing exposure, refresh the profile facts and use --strict; an unknown fact or triggered deferral cannot be silently treated as satisfied (#30).

For a screen, run the recorded capture command and retain a capture per applicable state, committed scheme and context. Open the captures and exercise the relevant interactions. Obtain independent review against the current artifact and decision basis (#27, #29). A screenshot alone cannot establish keyboard behavior, timing or task completion.

Investigate failures and warnings. Fix a real defect rather than suppressing the evidence. If a framework heuristic does not recognize a justified project approach, reproduce the mismatch and seek a correction or an explicitly supported path; do not report a failing gate as passed or bypass a protected obligation.

### Step 7: Keep authoritative records current

Use templates/feature-doc-template.md as the single feature format. A new feature gets its record at docs/features/{feature-name}.md and a feature-tree row with its location, status and record link. Keep the record brief when there are few non-obvious facts; update an existing record rather than creating another document for each edit. Link contracts, decisions and evidence instead of duplicating them (#16).

Update References.md when a project command, system entry point or accepted convention changes. Keep the reason at the existing decision location. Historical logs identify what was verified at that revision; they do not become another current inventory.

### Step 8: Preserve a verified recovery point

Within the granted repository authorization, commit a coherent verified change with its reason (#2). Separate independent changes where that improves review and recovery. Do not claim a commit, publication or verification that did not occur.

## Final gate: automated validator

Run scripts/validate-develop.sh before claiming the phase complete. It currently checks fixed shared-client patterns, console output in source feature folders, test-file presence and feature-document links. It warns on raw error construction. Those heuristics cover particular layouts and cannot establish all architectural or testing choices. Review each diagnostic against the project's actual contract; unresolved failures remain visible until corrected. Passing this validator does not replace behavioral evidence or independent review.
