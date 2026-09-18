# {Feature Name}

## What It Does
[One paragraph: what the feature does from the user's perspective]

## Why It Exists
[Business reason this feature was built]

## Systems Used
[Which foundational systems this feature plugs into]
- Error system: [how errors are handled in this feature]
- API layer: [which endpoints this feature uses]
- Theme: [any feature-specific tokens or styles]
- Design: [the artifact entry and revision this feature implements (#27); the purpose sentence; the states it covers; the session-decided entries, if any; where the capture set lives; who reviewed the screen against the artifact and when]
- Auth: [permission requirements]
- Forms: [if applicable - which forms and validation]
- State: [what state this feature manages]

## Structure
[Files and folders this feature contains]
```
src/features/{feature-name}/
├── components/
├── hooks/
├── api/
├── types.ts
└── index.ts
```

## Key Decisions
[Decisions made during implementation that aren't obvious from the code. Why X instead of Y.]
