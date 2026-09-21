# Bootstrap: discovery, group 5

## Step 2.5: Group 5 - Infrastructure and sensitivity
Read: bootstrap/ONBOARD-DISCOVERY.md; bootstrap/RED-FLAGS.md § Discovery Turn Budget; bootstrap/RED-FLAGS.md § Vague-Answer Rules; bootstrap/RED-FLAGS.md § Deploy Gate
Produces: the regulated-data answer (or the default with the open gate it creates), the infrastructure experience, and the ownership preference
Check: evidence: the owner's answers to this group in their own words, quoted; a question an earlier answer settled is recorded as inferred, with the inference; a question the owner declined is recorded as declined, with what was assumed

- Does this app handle sensitive data that has legal requirements? (health records, financial data, personal information with privacy laws)
- Do you or your team have experience managing servers and cloud infrastructure? Or would you prefer something that handles that for you?
- How important is it that you own and control all the infrastructure vs getting something live quickly?

If the user answers vaguely ("I dunno", "not sure", "I guess not"), DEFAULT TO ASSUMING REGULATED DATA. A wrong "no" generates a non-compliant stack caught only at audit; a wrong "yes" generates overkill-but-safe. Disambiguation question + full rule in `bootstrap/RED-FLAGS.md` "Vague-Answer Rules" section.

**Deploy gate:** if regulated-data is default-assumed-yes and never affirmatively answered, scaffolding and deploy (Phase 2+) must halt. Record in `VERSION-LOG.md` as open pre-production gate. Deflections do not resolve. See RED-FLAGS.md "Deploy Gate" section.

**Budget-vague:** parallels regulated-vague. See RED-FLAGS.md "Vague budget answer" section.

**Vague stack preference** ("use whatever", "I don't care"): treat this as delegated technical recommendation, not evidence for a stack. Step 3 researches viable approaches against the recorded goal and constraints. See RED-FLAGS.md.
