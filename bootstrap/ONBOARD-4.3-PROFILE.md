# Bootstrap: the operating profile

Part of the bootstrap playbook (bootstrap/ONBOARD.md), walked one step at a time with `scripts/next-step.sh` (development/STEPS.md). This file is one step: read it when the script names it, with the reading it lists, and close it before opening the next.

## Step 4.3: PROFILE.md
Read: #30; templates/profile.md
Produces: PROFILE.md at the repository root (above the endpoint folders in a fullstack layout), every key filled, unknown facts kept unknown
Check: run scripts/validate-profile.sh --declared
Depends on: bootstrap.2.6; bootstrap.4.2

Using templates/profile.md, every key filled: the operating stage you derived and its one-line Stage reason; Audience from Group 1 and Group 4 (who uses it, how many); Data, External effects, Operational reliance, Valuable records, Fallback, Contributors, and Customer commitments from Group 6; Regulated data from Group 5 (unknown when vague); the cost ceilings; the decision-authority setting with its source (owner-stated or defaulted); today's date as Observed-on; and a Review condition (a date or the first trigger you expect). A placeholder left in any key fails the check. Per #30. One PROFILE.md per repository, at its root, never one per endpoint: in a fullstack layout it sits above the endpoint folders, and the check finds it there from either endpoint.
