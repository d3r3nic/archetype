# Bootstrap: example conversations

Read once, with the first discovery step. Two owners, two very different openings, the same steps.

**Vibe coder with a vague idea:**

User: "I want to build an app for my restaurant"

AI: "Great! Let me ask a few questions to understand what you need..."
- "What should the app do? Take orders? Show the menu? Let people book tables?"
- "Should customers use it in a browser or as a phone app?"
- "Do customers need to create accounts?"
- ...

User: "I just want people to see our menu and book a table online"

AI: "Got it. This is a web app with a frontend for customers and a backend to store menu items and bookings. Users don't need accounts for viewing the menu, but bookings need a simple form. No file uploads, no real-time, no offline needed. I'd recommend a standard web stack: a component UI framework for the pages and a small typed API behind it. Let me set it up..."

**Developer who knows what they want:**

User: "I'm building a healthcare SaaS. Component-framework frontend, cloud-hosted backend, managed relational database, cloud-managed auth. I know the stack."

AI: "Stack noted. Before I generate files, Step 3 still applies — even with a declared stack. For healthcare SaaS specifically, HIPAA-compliant vertical platforms often cover most typical use cases (patient portals, intake, scheduling, notes) with BAAs included. Let me confirm: is the core of your product something those platforms already do, or is it unique logic on top of that (AI analysis, custom workflows, proprietary algorithms)? If it's the latter, your stack is a reasonable fit. If it's the former, start from the platform and build only the unique layer. Research current HIPAA vertical-SaaS options to make sure the recommendation is up-to-date."

User: "Custom — the core is our AI analysis pipeline, no platform does that."

AI: "Confirmed custom build is correct. Generating References.md with the declared stack, and I'll flag HIPAA-specific requirements inline (BAA with the cloud provider, encryption at rest, MFA on auth, audit logging, PII log-scrubbing)."

**Key takeaway:** even for a confident user with a declared stack, Step 3 still runs. A 30-second confirmation ("is this custom logic or platform-served?") prevents scaffolding weeks of infra for a use case a platform already solves.
