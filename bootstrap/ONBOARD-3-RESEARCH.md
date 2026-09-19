# Bootstrap: research before deciding

Part of the bootstrap playbook (bootstrap/ONBOARD.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step: read it when the script names it, with the reading it lists, and close it before opening the next.

## Step 3: Research Before Deciding (DO NOT SKIP)
Read: #0 § Principle; #29; bootstrap/LEARNING-PROJECTS.md (when the owner is building this to learn a technology)
Produces: the researched options with what each costs, one recommendation, and the settled build approach: a platform, or a custom build with its stack
Check: evidence: the recommendation as given, and the owner's decision in their own words (under ai-decides: the recommendation, and that no objection came by the stated time)

After discovery, the AI has the answers. But DO NOT pick a tech stack yet. First, research whether a custom build is even the right approach.

### The AI must consider: does the user actually need a custom app?

Many projects are better served by existing platforms than custom code. The AI must be honest about this, even though the framework exists to scaffold custom projects. Over-engineering is a violation of convention #0 (reusability — don't build what already exists, whether inside the project OR as a market-available platform).

**Exception: learning projects.** If Group 1 revealed this is a project to learn a specific technology (not a product to ship), platform-vs-custom research is bypassed — the technology choice IS the point. Scale-vs-cost still matters: recommend the cheapest way to exercise the target technology (local tooling before cloud). Full flow, detection heuristics, and References.md documentation template in `bootstrap/LEARNING-PROJECTS.md`.

Research and present these options to the user BEFORE committing:

**Option 1: Existing platform (no custom code needed)**

| User wants | Consider instead of custom code |
|---|---|
| Blog / content site | a hosted CMS, or a static site generator plus a headless CMS |
| Online store | a hosted e-commerce platform |
| Portfolio / brochure site | a hosted website builder, or a static site generator |
| Landing pages | a hosted landing-page builder |
| Internal forms / workflows | a no-code database, form, or internal-tool builder |
| Booking / appointments | a hosted scheduling service |
| Documentation site | a docs-site generator, or a hosted docs platform |

Research the current market leader in each category at bootstrap; the leaders change. If an existing platform covers 80%+ of what the user needs, recommend it. Custom code should only be chosen when the user has requirements that platforms genuinely cannot meet.

**Option 2: Hybrid (platform + custom pieces)**

Sometimes the right answer is a platform for the core + custom code for specific features:
- A hosted CMS for content + a custom frontend against its API (headless CMS)
- A hosted e-commerce platform for checkout + a custom dashboard for analytics
- A BaaS (Backend-as-a-Service) platform + custom frontend

**Option 3: Full custom build (what this framework scaffolds)**

Custom code is the right choice when:
- The app has complex business logic that platforms can't handle
- The app needs custom auth flows, HIPAA compliance, or specific security requirements
- The app is a SaaS product, dashboard, or tool with unique workflows
- The user has technical skills or a development team
- No existing platform covers even 50% of the requirements

### How to present the decision:

Research online (if capable) for the latest platform options that match the user's use case. This choice touches recurring cost and the shape of the product, so it goes to the owner under both decision-authority settings (#29): one recommendation first, the reason and the cost with it, the alternatives after it. Then present:

```
Based on what you described, my recommendation is [option] because [reason tied to the discovery answers]; it would cost [monthly cost or "nothing"] and take about [effort]. Doing this unless you object.

The alternatives I weighed:

Option A: [Platform name]
- What it does: [covers X, Y, Z of your requirements]
- What it doesn't do: [missing A, B]
- Cost: [pricing]
- Effort: [timeline]
- Best if: [use case fit]

Option B: [Different platform or hybrid approach]
- ...

Option C: Custom build with [tech stack]
- What it does: exactly what you need, fully customizable
- What it doesn't do: nothing - but you have to build and maintain everything
- Cost: development time + hosting
- Effort: [timeline estimate]
- Best if: you need full control, have complex requirements, or this is a product
```

Under `owner-decides`, wait for the owner's choice before generating anything. Under `ai-decides`, generate the project context for the recommended path if the owner does not object in the session: generating reversible context is preparation, not the decision, and the decision itself stays open; any sign-up, payment, or commitment waits for an explicit yes, because silence is not authorization (#29). Never generate a custom build when the recommendation was a platform and the owner has not chosen it.

If the user chooses a platform (Option A or B), help them set it up. The Archetype framework's scaffolding phase doesn't apply — but the conventions around security (#23), documentation (#16), and git (#2) still do.

Proceed to Step 4 when the build approach is settled: under `owner-decides`, when the owner confirms the custom build; under `ai-decides`, when the recommendation is a custom build and the owner has not objected.
