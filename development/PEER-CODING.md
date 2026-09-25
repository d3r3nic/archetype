# Peer coding

Two AI assistants, each in its own chat, work on a branch of this project in turns. The one holding the writing turn implements or repairs within the agreed scope; the other reviews every new change independently. The owner passes one short line between the two chats at each hand-over. This playbook is the rule for both assistants. The owner's instructions and the decision authority in PROFILE.md still govern (#29).

The framework owns these rules: an assistant working in a project never edits them. A project tailors them in one settings file, `peer-coding/SETTINGS.md`, and a defect in the rules goes upstream to the framework as a proposal, like any shared change.

## When it applies

- Peer coding is on when the repository has `peer-coding/SETTINGS.md`; References.md § Project records it on its `Peer coding` line. Without the file it is off, and the line says `none`. `check` warns when the two disagree.
- While it is on, each branch of work runs under this playbook unless the owner says a piece of work is solo.
- A relayed line that begins `READY FOR`, `NEEDS USER` or `SCOPE CLOSED` is a peer-coding cue: go to the branch it names and resume there.
- Your name is the short name the settings' Peers line gives your tool. When both assistants run the same tool, the owner tells each chat its name.

## Setting it up

When the owner chooses peer coding, at setup (bootstrap/ONBOARD-2.6-CARE-AND-AUTHORITY.md) or later, run `setup` in the project's git repository. It creates `peer-coding/SETTINGS.md` to fill in:

- Peers: the two assistants, each as its short name with its tool. The owner's decision.
- Who writes: who writes new work and who reviews it, in the owner's words. The owner's decision.
- Merge: what a merge needs besides the other assistant's acceptance and passing checks. The owner's decision, within PROFILE.md's decision authority.
- Checks each turn: what runs before every hand-over, from References.md § Commands and the applicable framework gates.
- Branch names: the project's naming for peer branches.
- Push: whether each hand-over pushes the branch (yes when the project has a remote both assistants can reach).
- Project rules: anything this project adds, such as an extra independent review before merge.

The owner's lines change only on the owner's decision. The other lines are technical choices: they follow PROFILE.md's decision authority, and a change to one is recorded at the decision location (#29). Record `Peer coding: peer-coding/SETTINGS.md` in References.md § Project and commit both like any project record. The second assistant reads the project's code and records, so bringing it in is the owner's decision, and PROFILE.md's regulated-data facts apply to it as to any service that sees the data. While the owner has not answered yet, record `none (asked, awaiting the owner)`: peer coding stays off, and the rest of the work continues.

## Who writes and who reviews

Both assistants can implement, review, repair and hand back. The settings' Who writes line says who writes new work: one writes and the other reviews, they take turns, or the owner names the writer each time. The owner can change it for any piece of work by saying so; record those words in the branch folder's CURRENT.md before acting on them.

The loop: the writer implements and hands over. The reviewer audits that exact range, repairs the supported findings within scope itself unless the owner's preference says otherwise, and hands the repairs back for review. This repeats until a review accepts with no new commits, which closes that scope. The next scope starts with the writer the preference names.

## The record

`peer-coding/` at the top of the repository holds the settings file and one folder per branch, committed and pushed with the branch:

- `peer-coding/<branch>/`, the branch name with slashes and other unusual characters turned into dashes, and a short code added when another branch already uses that name; `which` prints it, so never guess it.
- `CURRENT.md`: the branch's state. Its Alignment line holds the handshake's status and, until CONFIRMED, whose move it is; after CONFIRMED the Product writing turn line says whose move it is. Its Next action says what that move is, or NEEDS USER or SCOPE CLOSED. It also holds the heads, the accepted head, and the owner's words for this branch. Replace in place; never a diary.
- `ALIGNMENT.md`: the context handshake for this piece of work.
- `FINDINGS.md`: unresolved items, one row each.
- `rounds/R<n>/<name>.md`: the packets; `rounds/R<n>/evidence/<name>/`: saved command output.
- `peer-coding/<branch>--done/`: the same folder once it closed for its merge, or its work was abandoned. It is history; new work gets a new branch.

Each branch has its own folder, so parallel branches never edit the same file. The engine's `scripts/peer-coding.py` does the mechanical parts; run it with python3 from anywhere in the worktree: `setup`, `start`, `which`, `packet`, `check`, `cue`, `close`, the ones that act for an assistant with `--as <your name>`.

## Resume from a relay line

Go to the worktree the line names (or your own checkout of its branch) and read the AGENTS.md the line names, then the branch folder's CURRENT.md and ALIGNMENT.md. The line names `<branch>@<commit>`: make sure your checkout contains that commit (pull when it is clean; otherwise stop and tell the owner). Run `check`. Then take the first case that applies:

1. ALIGNMENT.md is not CONFIRMED: your move in the Alignment section below when its Status is REQUESTED and you are the Context holder, or BRIEFED and you are the Receiver; when its roles are still placeholders, `start` was interrupted and the Start section's step 3 is yours. Nobody changes product files in this state.
2. CURRENT.md's Next action says NEEDS USER or SCOPE CLOSED: see Waiting on the owner, below.
3. CURRENT.md gives you the writing turn: Each turn, below.
4. Otherwise it is the other assistant's move, and the line may have reached the wrong chat: tell the owner so in one line, and stop.

## Start a branch

1. Work on a branch of its own, never the default branch, named as the settings say; a separate worktree per branch keeps parallel work apart.
2. `start` creates the folder and records the commit the branch stands at and the framework revision it follows. It refuses the default branch, a branch whose folder is open (resume it) or closed, a repository without complete settings, and a location the repository's ignore rules would keep out of commits.
3. Decide honestly whether you hold the context for this work. You hold it only if you can state with evidence, from this conversation or files you read: what the product is and who it serves; the goal and scope of this work; the decisions already made and why; the constraints and holds. Code shows where things stand, not intent, decisions or holds; never infer those from code. The project's records (References.md, PROFILE.md, feature-tree.md, the decision location, PROGRESS.md) are evidence when current: the brief links them and covers only what they do not hold for this piece of work.
   - You hold it: you are the Context holder, and you brief (next section).
   - You do not: you are the Receiver. List in ALIGNMENT.md §2 what you verified yourself, then numbered, specific questions, and set Status REQUESTED.
4. A closed folder whose alignment was CONFIRMED can seed the new one: carry forward only what you re-verify, and name that folder.
5. Hand over (below).

## Alignment

- Holder: fill §1 and answer each §2 question. Tag every claim `[verified: command or file]`, `[decision: who, date]` or `[unverified]`. Link only files inside the repository; copy in, with source and date, anything from notes the other assistant cannot read. A decision that exists only in conversation is tagged and recorded at the decision location in the first round (#29). Propose the first round: writer (per the settings' Who writes), bounded scope, acceptance checks. Set Status BRIEFED and hand over. When something only the owner can answer blocks the brief, leave that row open and wait on the owner instead.
- Receiver: check every §1 claim against the repository and record each in §3 as CONFIRMED, DISCREPANCY or UNVERIFIABLE. A discrepancy, an unanswered question, or an unverifiable fact the first round depends on blocks: add numbered follow-ups, set Status REQUESTED, and hand over. An attributed decision that code cannot prove is accepted as attributed; an honest `[unverified]` stays a caveat. Otherwise write the Receiver verdict, set Status CONFIRMED, and give the first round's writer the writing turn: when that is you, go straight to Each turn; otherwise hand over.
- Only the receiver confirms. Neither assistant changes product files before CONFIRMED.
- When scope or direction changes mid-branch, the holder updates §1, notes the change at the top, sets Status BRIEFED, sets the writing turn to none, and hands over; the receiver re-verifies what changed.

## Each turn

1. Having resumed as above, read the incoming packet, and only the findings and evidence it links. Read the project's rules files before editing.
2. `packet` opens your packet for this turn, marked WIP, and names your evidence folder.
3. Review the incoming range: each finding with severity, location, the case that triggers it, the wrong result and the evidence. Give the verdict for that exact range: ACCEPTED, CHANGES REQUESTED, or BLOCKED with the reason. Self-review is not independent review. Accepted work stays closed unless new evidence contradicts it, and no number of rounds turns an unresolved finding into acceptance.
4. Repair the supported findings and implement the agreed scope, keeping agreed behavior. Widening the scope needs the owner's words recorded in CURRENT.md. After your final edit, run the settings' Checks each turn and anything the change calls for, and save the exact commands, exit codes and output in your evidence folder, in files the repository does not ignore. Commit the product work.
5. Fill your packet: the verdict, the new commits awaiting review, the evidence and its limits, the next action. In CURRENT.md record the last product commit, the latest round, and the accepted head when you accepted the other's final range with no new commits of your own. Update only the affected rows of FINDINGS.md.
6. Hand over; or, when a clean verdict closed the scope and nothing more is in scope, wait on the owner with SCOPE CLOSED rather than inventing a change to keep the loop going.

## Hand over

After every alignment move and every turn:

1. In CURRENT.md, give the move to the other assistant: before CONFIRMED on the Alignment line (its status and `Next move: <name>`), after CONFIRMED on the Product writing turn line (every hand-over passes the turn). Write in Next action what that move is.
2. Remove the WIP line from your packet. Run the project's format and documentation checks over the record, then `check`, and fix what they report.
3. Commit the record alone: `git add -- peer-coding && git commit -m "<message>" -- peer-coding`, so nothing else staged is swept in. When the settings say Push: yes, push the branch to its own remote branch, and open a draft pull request if the project uses them and none exists. Never make a push that itself deploys.
4. `cue` prints the relay line. Give the owner only that, plus anything only the owner can decide, numbered, one line each. Then stop changing product files.

## Waiting on the owner

- NEEDS USER: a question only the owner can answer blocks the next move. Write it in Next action as `NEEDS USER: <the questions>`, then hand over steps 2 and 3, and `cue` prints `NEEDS USER · <folder> · <branch>@<commit>`. Give the owner that line and the numbered questions, one line each.
- SCOPE CLOSED: a clean verdict closed the scope and no next scope is recorded. Write `SCOPE CLOSED: awaiting the owner` in Next action, commit and push the same way, and `cue` prints the line.
- Whichever assistant receives the owner's answer records it as `[decision: owner, date]` (in ALIGNMENT.md §2 for a brief, otherwise in CURRENT.md with the owner's words), replaces the Next action, and continues when the move is its own; otherwise it hands over.

## Closing the branch

- A merge needs the other assistant's ACCEPTED verdict on the final product head, recorded on CURRENT.md's Accepted head line; passing checks; what the settings' Merge line requires; and the authorization PROFILE.md and #29 require (the owner's when it deploys or touches a live environment).
- Carry every unresolved finding to the project's own records first (the canonical task source development/TASKS.md names, or TECHNICAL-DEBT.md) and note in your packet where each went; the folder closes only with FINDINGS.md empty.
- The merging assistant runs `close --merged <pull request or ref>`: the folder becomes `<branch>--done`, marked closed for that merge. Commit it as the branch's last change, push, merge, and tell the owner in one line that the branch merged; no relay line is needed. The record says "closed for merge", never that the merge happened.
- If the merge then does not happen (a check fails, the merge is refused), `close --reopen "<reason>"` renames the folder back, and the work continues. A branch that merged stays closed.
- Work the owner abandons: `close --abandoned "<reason>"`.
- A folder left open by a merge: `check` reports one whose branch was merged by a merge commit or no longer exists. After a merge that squashed the branch's commits, delete the branch, here and on the remote, and the next `check` names the folder. Close it from the branch at hand with `close --folder <folder> --merged <ref>` (or `--abandoned`) and commit that.

## Rules for every turn

- One writer. Only the assistant holding the writing turn changes product files. The folder files you own (your packet, your ALIGNMENT.md sections, CURRENT.md at hand-over) are yours to edit in any move of yours. Re-read a shared file before changing it; if it changed since you read it, reconcile rather than overwrite.
- Never state that something works, passed, exists or was deployed unless you verified it in this session. Saved evidence is dated history, not fresh proof.
- The relay stays between the two chats and the owner: no automatic messages, watchers, or extra sessions standing in for either assistant. An extra independent review the settings' Project rules ask for is not a stand-in.
- If your tool cannot write the worktree, commit or push without the owner's approval, ask for that approval; never hand over uncommitted work or claim a write you could not make.
- Links in the folder go to files in the same folder, to project records, or to closed folders; never into another branch's open folder, which closing renames, never to files the repository ignores, and never to paths outside the repository. A line number goes after a link, never inside its target. No secrets in packets or evidence.

Dated example: a settings file with `Peers: claude (Claude Code), codex (Codex)` and `Who writes: claude writes new work; codex reviews it and fixes what it finds`. Claude Code loads CLAUDE.md, which imports AGENTS.md; Codex reads AGENTS.md from the repository root down to its working folder; Codex's default sandbox keeps git data read-only and the network off, so its commit and push ask the owner for approval (checked 2026-09-24).
