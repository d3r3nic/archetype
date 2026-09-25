# Peer coding settings

This project's choices for peer coding: two AI assistants take turns on its branches, and the owner passes a short line between their chats. The rules are the framework's, in {{PLAYBOOK}}; this file only tailors them. Peers, Who writes and Merge change only on the owner's decision; the other lines are technical choices under PROFILE.md's decision authority, recorded at the decision location when they change. Keep one line per setting, each starting with `- `.

- Peers: [the two AI assistants, each as its short name with its tool in parentheses, separated by a comma]
- Who writes: [the owner's preference, in the owner's words: who writes new work and who reviews it, whether they take turns, or whether the owner names the writer each time]
- Checks each turn: [what runs before every hand-over: the commands in References.md § Commands by their labels, or the commands themselves]
- Branch names: [how peer branches are named here, or: any name except the default branch]
- Push: [yes: each checkpoint and each hand-over pushes the branch; no only when a push to a work branch would itself start a deploy or release build, or the project has no remote, saying which]
- Merge: [what a merge needs besides the other assistant's acceptance and passing checks: the owner's go-ahead each time, or, until the owner decides otherwise, nothing more than PROFILE.md requires]
- Project rules: [what this project adds to the framework's peer rules, or none]
