# Reporting framework problems upstream

The framework's maintainers fix what real projects report, so report what goes wrong instead of working around it silently. The session still decides what fits this project (AGENTS.md), and the work never waits for an answer.

## When

- A script, a check or the updater failed, or answered wrongly: a check passed what it should have stopped, or failed a correct project.
- An update broke or lost something of the project's.
- An instruction was unclear, or contradicted another.
- The framework did something other than what its own files say it does.
- It stated one answer where this application needed another, and research or what you know showed why.
- It repeated itself, or asked for paperwork that decided nothing.
- A step did not fit how this kind of application works, and you set it aside (development/STEPS.md).
- A check failed on how something was written, or on a layout or tool the project does not use.
- It named a technology. The framework names none; each project chooses its own.

A gap counts too: something the framework should have reminded you of and did not.

## What to write

- The file and section, or the script and the command you ran.
- What the framework's files say should happen, and what happened instead: the output or the result, with private details removed.
- How to make it happen again, in general terms: the kind of application, not its name.
- Why it matters, with the evidence or the research behind that.
- What you did instead, and how it was verified.
- The change you propose: the words to remove, soften or add. A pull request can carry the exact text.

Keep out the project's name, the names of its owner and its customers, its data, code, paths and credentials, and anything else private. The framework's repository is public.

## Where, and who sends it

The framework's source is the Source line in VERSION-LOG.md. Draft the report as an issue or a pull request there. It publishes outside the project, so it goes out only on the owner's authority (#29):
- show the owner each draft and send it when they approve; or
- send it under a standing instruction the owner gave, recorded at the decision location with its bounds (for example, "framework reports may be sent without asking"), and give the owner its link in one line.

If the owner declines, keep the draft with the project's records and mention it in the session summary.

The reports on the framework's repository are its log of expected against actual behavior. The maintainers work through them, and a fix arrives with an update, which development/CHANGES.md describes. A report does not change this project's obligations: keep working to the decision you recorded.
