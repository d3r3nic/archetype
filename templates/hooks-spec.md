# Hooks Specification

Hooks enforce rules that must be followed 100% of the time. CLAUDE.md rules are ~80% compliance. Hooks are deterministic.

## Recommended Hooks

### PostToolUse: After File Write/Edit

Purpose: verify documentation stays current after code changes.

Trigger: after any Write, Edit, or MultiEdit tool use.

Actions:
1. Check if the changed file belongs to a feature
2. If yes: verify the feature's README/doc exists
3. If the feature doc doesn't exist: remind to create it
4. If a new feature directory was created: remind to add it to feature-tree.md

### PostToolUse: After Task Completion

Purpose: verify work before marking complete.

Trigger: after TaskComplete.

Actions:
1. Remind to run build/typecheck/tests
2. Check if feature-tree.md needs updating
3. Check if References.md needs updating (new system or path change)

### PreToolUse: Before Bash (destructive)

Purpose: catch destructive commands.

Trigger: before Bash commands matching rm -rf, git reset --hard, DROP TABLE, etc.

Actions:
1. Warn about the destructive operation
2. Suggest safer alternative if one exists

## Feature Tree Audit Hook

Purpose: periodic audit of feature tree accuracy.

When to run: manually after major changes, or on a schedule.

Implementation (bash):
```bash
#!/bin/bash
# Scan src/features/ for directories
# Compare against feature-tree.md entries
# Report: features in code but not in tree (missing)
# Report: features in tree but not in code (stale)
# Report: features without docs/features/{name}.md (undocumented)

echo "=== Feature Tree Audit ==="

FEATURES_DIR="src/features"
TREE_FILE="feature-tree.md"

# Find all feature directories
for dir in "$FEATURES_DIR"/*/; do
  feature=$(basename "$dir")

  # Check if in feature tree
  if ! grep -q "$feature" "$TREE_FILE" 2>/dev/null; then
    echo "MISSING from tree: $feature"
  fi

  # Check if documented
  if [ ! -f "docs/features/$feature.md" ]; then
    echo "UNDOCUMENTED: $feature"
  fi
done

echo "=== Audit Complete ==="
```

## Documentation Freshness Hook

Purpose: flag stale documentation.

Implementation concept:
- After modifying files in a feature directory
- Check if the feature's doc was also modified in the same session
- If not: remind "Feature [name] was modified but docs/features/[name].md was not updated"

## Notes

- Hooks should be advisory (echo reminders), not blocking, unless the rule is absolutely critical
- Blocking hooks: only for verification (build/test must pass before completion)
- Advisory hooks: documentation updates, feature tree updates, audit reminders
- Hooks are configured in .claude/settings.json (for Claude Code) or equivalent for other AI tools

## How to Set Up Hooks

Hooks are tool-specific. The AI assistant can help you set them up if you ask.

For Claude Code: tell the AI "Set up the hooks from archetype/templates/hooks-spec.md. Create .claude/settings.json with the hook configuration." The AI will create the settings file and any hook scripts needed.

For Cursor: tell the AI "Set up automated checks based on archetype/templates/hooks-spec.md using Cursor's hook system."

For other tools: tell the AI "I want automated reminders after code changes to update docs and feature-tree. What does my AI tool support?"

If your AI tool doesn't support hooks, skip this step. The conventions still work through the CLAUDE.md enforcer (~80% compliance). Hooks add deterministic enforcement but are not required.

Setting up hooks is optional during bootstrap. You can add them at any time by asking the AI to read this spec and wire it up.
