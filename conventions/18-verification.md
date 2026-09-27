# Convention #18: Verification-Driven Development

## Applies when

Every change that claims an outcome. What varies is the evidence the outcome needs: tests for behavior, captures and interaction for a screen, a measurement for performance, a source check for prose.

## Principle

Completion requires evidence for the behavior being claimed. Define the expected outcome independently of the implementation, select checks that can expose a wrong result, and verify while changes remain understandable. Test-first development is useful when a behavioral specification can be made executable before implementation; test timing alone does not establish correctness.

## Reusable System

Use the project's test infrastructure (#12) and record its verification commands in References.md. Required gates prevent acceptance of unresolved failures. UI evidence combines current captures with the interactions and access checks that the claim needs (#27). Other domains need evidence appropriate to their actual behavior.

## Rules

- Establish observable success and relevant failure behavior before implementation. For a defect, reproduce it and preserve a regression check where practical.
- Choose tests or observations that distinguish the intended result from plausible wrong results. Do not mirror implementation details and call that proof.
- Verify at coherent change boundaries, early enough to identify the cause of a failure. Select focused checks during iteration, then run all applicable required project checks before claiming completion.
- Run tests, type checks and builds where they verify affected behavior or a declared project gate requires them. A prose-only change needs appropriate source and contract checks; it does not justify inventing a code test or rerunning an unrelated build after every wording edit.
- For screen changes, inspect current visual evidence and exercise relevant interactions. Compilation and screenshots alone cannot establish usable behavior.
- Investigate failures and warnings. Keep real defects and unresolved required checks blocking; never suppress a diagnostic or weaken an assertion merely to pass.
- Reproduce a heuristic mismatch against the accepted project contract and correct the check or use an explicitly supported verification path. Do not label an unsupported approach verified.
- State exactly what ran, what was observed and what remains unverified. Independent review examines the evidence and its limits (#29).

## Violations

- Acceptance based on remembered output, inferred success or a command that was never run.
- Tests that confirm whatever the implementation returns without checking intended behavior.
- A large unverified batch whose failures cannot be localized.
- Repeated checks that add no evidence after unchanged inputs, while relevant risks remain untested.
- Claiming an interface works from compilation or captures alone.
- Calling work complete with a failing or unperformed required gate.

## Wrong vs Right

- WRONG: a defect appears fixed by inspection, so the session reports success. RIGHT: reproduce the original behavior, check the correction and relevant regressions, and retain the result.
- WRONG: run every command after each small edit while ignoring a cross-system failure path. RIGHT: check coherent changes during iteration and run the required integration and project gates before acceptance.
- WRONG: a test copies the function's formula and agrees with the same mistake. RIGHT: derive expected cases from the domain contract, including a case that exposes the suspected mistake.

## Research Notes

Investigate tools and techniques for the project's runtime and risks. Prefer maintained test infrastructure, representative environments and observable outcomes. Revisit the test strategy when behavior, exposure or an uncovered failure changes its assumptions. Keep required commands and their purpose in References.md.
