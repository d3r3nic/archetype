# Convention #18: Verification-Driven Development

## Principle

Code is not done until it is verified. Every change is followed by running tests, building, and type-checking. Tests are written before implementation, serving as executable specifications that define what success looks like. The AI implements against these specifications. Verification is the bottleneck in AI development, not code generation. This is the single highest-leverage practice for AI-assisted development.

## Reusable System

The test infrastructure from convention #12 serves this convention. Additionally:
- Verification commands documented in References.md so the AI knows exactly what to run
- Build gates (hooks or scripts) that block marking work complete until all checks pass
- A visual verification step for UI changes: describe or capture what the result looks like and compare to the expected outcome

## Rules

- Write failing tests BEFORE asking the AI to implement. The test defines what correct behavior looks like. Then the AI implements until the test passes. This prevents AI from writing tests that confirm broken behavior.
- Run tests after every significant change. Not at the end of the session. After every change.
- Type-check after every change. Type errors caught early prevent cascading issues.
- Build after every change. Import errors, missing dependencies, and configuration issues show up in the build.
- For UI changes, verify the visual output. Describe what the screen looks like or compare to a design. The code compiling doesn't mean the UI looks right.
- Work is not done until all verification passes. If tests fail, fix them. If the build fails, fix it. Do not move on with failing checks.
- If no test exists for the code being changed, write one before making the change.

## Violations

- Implementing a feature and writing tests after (or not at all)
- Making multiple changes without running verification between them
- Calling work done without running the build
- A change that compiles and passes tests but looks wrong visually (UI regression)
- Moving on to the next task while tests or build are failing
- Tests written after implementation that simply confirm whatever the implementation does (even if it's wrong)

## Wrong vs Right

- WRONG: AI writes the feature code. It looks reasonable. Developer ships it. Bugs found in production because nobody verified.
- RIGHT: developer writes a failing test that defines the expected behavior. AI implements code. Test runs. If it fails, AI adjusts. If it passes, move to the next test. Every piece of behavior is verified before moving on.
- WRONG: AI makes 10 changes across 5 files. At the end, runs the tests. 3 tests fail. Now debugging is hard because any of the 10 changes could have caused the failures.
- RIGHT: AI makes 1 change, runs verification. Pass. Makes the next change, runs verification. Pass. If a test fails, the cause is obvious - it's the change that was just made.
- WRONG: tests exist, but they were written by AI after the implementation. The test checks that the function returns exactly what the implementation returns. If the implementation is wrong, the test passes anyway.
- RIGHT: tests written first define what SHOULD happen. The implementation must match the test, not the other way around.

## Research Notes

This convention is about development workflow, not framework-specific implementation. The test infrastructure details are in convention #12 and its research notes. For this convention, ensure:
- Verification commands are documented clearly in References.md (exact command to run tests, type-check, build)
- Build gates are configured (hooks or CI that blocks incomplete work)
- The team agrees on test-first workflow for AI-assisted development
