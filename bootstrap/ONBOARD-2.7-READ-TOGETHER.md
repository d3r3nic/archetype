# Bootstrap: reading the answers together

## Step 2.7: Read the answers together
Read: bootstrap/RED-FLAGS.md § Red Flag Combinations; bootstrap/RED-FLAGS.md § Scope-Change Handler
Produces: the owner's knowledge level as read from the answers, the technical needs the answers translate into, and every red-flag combination found, said to the owner before any research
Check: evidence: the needs the answers translate into, and each red-flag combination found with what the owner said about it, or none found
Depends on: bootstrap.2.1; bootstrap.2.2; bootstrap.2.3; bootstrap.2.4; bootstrap.2.5; bootstrap.2.6

Read the answers as one product brief. Separate requirements from possible implementations:

- State the owner's goal, intended users and primary tasks in their terms.
- Translate access, data, effects, scale, reliability, cost, context and learning goals into capabilities and constraints. Keep unknown facts unknown.
- Preserve technologies the owner has committed to as constraints or preferences with their reasons. Do not turn the owner's apparent expertise into an architecture choice.
- Identify tensions that materially affect feasibility, safety, cost or the product's purpose. Explain the tension without treating one familiar stack or service category as the automatic answer.
- Distinguish a requirement from a proposed solution. Offline work is a requirement; a particular synchronization design is a later researched choice. Team identity is a requirement; a named authentication product is not yet the answer.

The red-flag catalogue supplies questions and failure modes, not a verdict. Multiple flags increase the need for careful research; they do not select a platform or custom build by count. If a new answer changes earlier scope, use the Scope-Change Handler, revisit the affected groups and re-run Step 3.

Do not proceed to Step 3 until the brief is coherent enough to compare real options. Coherent does not mean every uncertainty is resolved. Name the uncertainties that the research must answer.
