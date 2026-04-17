# Phase 4: Maintain

Audit, update, and evolve the project over time. Run periodically and after major changes.

## Feature Tree Audit

Run after major changes or periodically (every 2-4 weeks).

### What the Audit Checks

1. Features in code but not in feature-tree.md (missing from tree)
2. Features in tree but not in code (stale entries)
3. Features without docs/features/{name}.md (undocumented)
4. Systems documentation that doesn't match current code (stale system docs)
5. References.md paths that no longer exist (broken references)

### Audit Prompt

Use this prompt with your AI assistant:

---

Audit the project against its documentation:

1. Scan the feature directories and compare against feature-tree.md
   - Report features in code but missing from the tree
   - Report tree entries that no longer exist in code
   - Report features without a doc in docs/features/

2. Scan foundational system locations in References.md
   - Verify each path still exists
   - Verify docs/systems/ matches actual systems

3. Check for convention violations:
   - Hardcoded values that should use the theme/config system
   - Direct third-party imports bypassing wrappers
   - Scattered error handling outside the error system
   - Ad-hoc API calls outside the API layer

4. Update feature-tree.md with findings
5. Update the audit log in feature-tree.md with date and findings

---

### Audit Script

Run to get a quick automated check:

```bash
#!/bin/bash
echo "=== Feature Tree Audit ==="

FEATURES_DIR="src/features"
TREE_FILE="feature-tree.md"

# Features in code but not in tree
for dir in "$FEATURES_DIR"/*/; do
  feature=$(basename "$dir")
  if ! grep -q "$feature" "$TREE_FILE" 2>/dev/null; then
    echo "MISSING from tree: $feature"
  fi
  if [ ! -f "docs/features/$feature.md" ]; then
    echo "UNDOCUMENTED: $feature"
  fi
done

# Check References.md paths
echo ""
echo "=== References.md Path Check ==="
grep -o 'src/[^ ]*' References.md 2>/dev/null | while read path; do
  if [ ! -e "$path" ]; then
    echo "BROKEN PATH in References.md: $path"
  fi
done

echo ""
echo "=== Audit Complete ==="
```

## Documentation Maintenance

### When to Update Documentation

- After implementing a feature → create docs/features/{name}.md
- After modifying a feature → update its doc
- After modifying a foundational system → update docs/systems/{name}.md
- After changing project structure → update References.md
- After any of the above → update feature-tree.md

### Hooks Handle This Automatically

Hooks (configured during bootstrap) remind the AI to:
- Update feature docs after file changes in a feature directory
- Update feature-tree.md after creating new features
- Run verification before marking tasks complete

## Technical Debt Tracking

Maintain a TECHNICAL-DEBT.md file in the project root. This is a living document that tracks known issues, type shortcuts, and convention violations that were deferred rather than fixed immediately.

### What Goes in Technical Debt

- Type assertions (`as any`, `as unknown`) that should be properly typed
- Convention violations discovered during feature work that weren't fixed because they were out of scope
- Missing error handling, loading states, or accessibility on existing features
- Direct third-party imports that should use wrappers
- Hardcoded values that should be config-driven
- Components that should be reusable but were built as one-offs

### Rules

- When you encounter tech debt while working on a feature, fix it if it's in the same feature you're touching. If it's in a different feature, log it in TECHNICAL-DEBT.md instead.
- Each entry has: what the issue is, where it is (file path), which convention it violates, and severity (high/medium/low).
- When starting work on a feature, check TECHNICAL-DEBT.md first. If the feature you're about to work on has logged debt, fix it as part of your work.
- Review and reduce technical debt periodically. Do not let it accumulate indefinitely.
- When you fix a debt item, remove it from TECHNICAL-DEBT.md.

## Convention Evolution

### Adding a New Convention

1. Create the convention doc in conventions/ following templates/convention-template.md
2. Add entry to Conventions.md
3. Update References.md with how the convention applies to this project
4. If the convention produces a foundational system, build it and document in docs/systems/

### Updating a Convention

1. Update the convention doc
2. Check if the project's implementation still matches
3. If not, plan the migration and update References.md

### When New Techniques Emerge

1. Evaluate against existing conventions
2. If the technique improves a convention, update the convention doc
3. If it's entirely new, consider adding a new convention
4. Document the decision in References.md under "Convention Overrides"

## Session Reviews

Periodic audit of how well the AI followed the framework. Run after every 3-5 AI coding sessions, or after any session where something went notably wrong or right.

### When to run

- Every 3-5 sessions on an active project
- After a session with visible drift (AI skipped conventions, modified enforcement files, repeated the same mistake)
- After a session with an unexpectedly good result worth understanding
- Before a convention revision — gather evidence from recent reviews

### How to run

1. Open `templates/session-review.md`
2. Copy it to `docs/reviews/YYYY-MM-DD-topic.md` (create `docs/reviews/` if needed)
3. Fill in the 5 review questions and the Drift section
4. Capture any action items as concrete framework changes: convention wording, lookup table rows, new CLAUDE.md rules, new hooks

### How findings feed back

- Convention wording problems → update the convention doc (record in CHANGELOG.md)
- Missing task-type routing → add a row to Conventions.md lookup table
- Recurring drift on a specific pattern → consider a new CLAUDE.md rule or an automated hook
- Accumulating suggestions → batch into a framework revision step

Reviews are an evidence stream, not a bureaucratic step. Skip them on lightweight sessions; run them when the outcome surprised you.

## Framework Self-Test

Run the framework's own validator periodically:

```bash
./archetype/scripts/validate-framework.sh
```

Checks that file paths in CLAUDE.md resolve, the convention count in intro text matches actual files, every `#N` reference resolves, every convention doc has its required sections, and no duplicate convention numbers exist.

Run it after any change to the framework (update.sh, manual edits to conventions, adding a new convention). A failing self-test means the framework is internally inconsistent and the AI will produce confused output.
