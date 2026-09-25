# {{FOLDER}} R{{ROUND}}: {{BY}} to {{OTHER}}

Status: WIP. Remove this line when the packet is ready to hand over.

## Incoming review

- Incoming packet: {{INCOMING}}
- Reviewed range and worktree state: <base..head on `{{BRANCH}}`, and clean or what is uncommitted>
- Verdict: <ACCEPTED | CHANGES REQUESTED | BLOCKED, for this exact range; or none, when there was nothing to review>
- Findings: <ID, severity, location, triggering case, wrong result, evidence; or no findings>
- What the evidence establishes, and its limits: <...>

## New commits

- Range awaiting review: <base..head, or none>
- Changes and reasons: <each supported finding with its repair, and the scope implemented>
- Self-review: <what was checked, what was corrected, what still concerns you>

## Evidence

| Command | Exit or result | Saved output | Scope and limits |
|---|---|---|---|
| <exact command> | <exit code and result> | <file under evidence/{{BY}}/, linked once committed> | <executed now, saved earlier, or reasoning only> |

Keep failed runs with their diagnosis. A larger test count alone is not proof. No secrets.

## Hand-over

- Findings updated: <IDs, or none>
- Last product commit: <full commit id>; hand-over commits touch only this folder.
- Next: <who moves next, and the bounded action>
- Current state: {{CURRENT}}
