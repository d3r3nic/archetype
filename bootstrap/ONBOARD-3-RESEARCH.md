# Bootstrap: research before deciding

## Step 3: Research before deciding
Read: #0 § Principle; #29; bootstrap/LEARNING-PROJECTS.md (when learning a technology is part of the owner's purpose)
Produces: the researched options with what each costs, one recommendation, and the settled build approach: a platform, or a custom build with its stack
Check: evidence: the recommendation as given, and the owner's authorization of the build approach in their own words, or where an authorization already recorded says so (it is not asked again)
Depends on: bootstrap.2.7
Skip by: owner

Research the current ways to achieve the owner's goal before selecting a build approach or stack. Existing platforms, extensions to an existing system, hybrid approaches and custom work are candidates when they can satisfy the important requirements. The framework scaffolds custom projects, but that is not evidence that custom is right.

Start from the brief produced by Step 2.7. Identify the requirements that decide the choice, especially the primary task, missing capability, ownership needs, integrations, data and external effects, accessibility, operating burden, time and recurring cost. For a learning project, include what the chosen path actually teaches. A missing capability central to the purpose can outweigh broad feature coverage. Popularity and market position are evidence about support and risk, not selection rules.

For each viable option, verify current primary sources and record:

- which important requirements it satisfies and which it does not;
- the work needed to close material gaps;
- current price and terms that affect the project;
- ownership, export, integration and migration limits;
- security, privacy and operating obligations relevant to the recorded profile;
- implementation and maintenance effort, with uncertainty named;
- why it remains viable or why it was rejected.

Research only to the depth the decision needs. Do not repeat current project research without a relevant change, expired evidence or unresolved question. Never label remembered knowledge as verified research.

Recommend one approach because its tradeoffs best serve the owner's purpose and constraints. Present the recommendation first in plain language, with cost and material limitations, then the credible alternatives. Do not use a coverage percentage, the owner's technical vocabulary, or a fixed platform/custom preference as the deciding rule.

This choice changes the product shape and may create recurring cost, so it remains the owner's decision under both authority settings (#29). Under `owner-decides`, wait for the choice. Under `ai-decides`, reversible project context may be prepared after the recommendation and stated objection window, but sign-up, payment, external commitment and the product-shape decision require the owner's authorization. Do not generate a custom project while a different build approach is still the recommendation and the owner has not chosen custom.

In Step 4.2, route by responsibility: use platform context for provider-owned capabilities and custom context for code the project owns, including integrations or extensions within a hybrid. Record the researched stack and applicable verification for owned code. A platform choice does not remove the project's testing, security or maintenance obligations at those boundaries.

## Record the settled basis

Carry consequential build and scope choices into the single decision location selected in Step 4.2 (#16). Give stable IDs to choices later work depends on, including the build approach and committed contexts. Keep owner requirements as the grounds of the design brief; delegating a look never replaces them. Do not create a second record when the project already uses one.
