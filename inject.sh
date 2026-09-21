#!/bin/bash
# Archetype Framework Injection Script
# Injects the framework into a target project.
# AGENTS.md and CLAUDE.md go to project root (agent entry points).
# Everything else goes in a subfolder.
# Existing instruction files are preserved before managed entry points replace them.

set -e

# Defaults
TARGET_DIR="${1:-.}"
SUBFOLDER_NAME="${2:-archetype}"

# Get the directory where this script lives (the framework root)
FRAMEWORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Resolve target to absolute path
TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd || echo "$TARGET_DIR")"

if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: Target directory does not exist: $TARGET_DIR"
  echo ""
  echo "Usage: ./inject.sh [target-directory] [subfolder-name]"
  echo "  target-directory: where to inject the framework (default: current directory)"
  echo "  subfolder-name: name of the subfolder (default: archetype)"
  exit 1
fi

case "$SUBFOLDER_NAME" in
  ''|.|..|*/*)
    echo "Error: subfolder-name must be one directory name within the target project."
    exit 1
    ;;
esac

DEST="$TARGET_DIR/$SUBFOLDER_NAME"

if [ -e "$DEST" ] || [ -L "$DEST" ]; then
  echo "Error: $DEST already exists."
  echo "Remove it first or choose a different subfolder name:"
  echo "  ./inject.sh \"$TARGET_DIR\" archetype-v2"
  exit 1
fi

# Refuse unsafe destinations before any writes, including dangling symlinks.
for entry in AGENTS.md CLAUDE.md Claude.md AGENTS.md.pre-archetype CLAUDE.md.pre-archetype VERSION-LOG.md; do
  if [ -L "$TARGET_DIR/$entry" ] || { [ -e "$TARGET_DIR/$entry" ] && [ ! -f "$TARGET_DIR/$entry" ]; }; then
    echo "Error: $entry must be a regular file, not a symlink or other file type."
    exit 1
  fi
done
for entry in docs docs/systems docs/features; do
  if [ -L "$TARGET_DIR/$entry" ] || { [ -e "$TARGET_DIR/$entry" ] && [ ! -d "$TARGET_DIR/$entry" ]; }; then
    echo "Error: $entry must be a local directory before injection."
    exit 1
  fi
done
for entry in AGENTS.md CLAUDE.md; do
  original="$TARGET_DIR/$entry"
  if [ "$entry" = CLAUDE.md ] && [ ! -f "$original" ]; then
    original="$TARGET_DIR/Claude.md"
  fi
  if [ -f "$original" ] && [ -e "$TARGET_DIR/$entry.pre-archetype" ]; then
    echo "Error: $entry.pre-archetype already exists. Preserve and reconcile that guidance before injection."
    exit 1
  fi
done
if [ -f "$TARGET_DIR/CLAUDE.md" ] && [ -f "$TARGET_DIR/Claude.md" ] && \
   [ ! "$TARGET_DIR/CLAUDE.md" -ef "$TARGET_DIR/Claude.md" ]; then
  echo "Error: distinct CLAUDE.md and Claude.md files exist. Reconcile their guidance before injection."
  exit 1
fi

echo "Archetype Framework Injection"
echo "============================="
echo "Source: $FRAMEWORK_DIR"
echo "Target: $TARGET_DIR"
echo "Subfolder: $SUBFOLDER_NAME/"
echo ""

# Step 1: CLAUDE.md goes to PROJECT ROOT (Claude Code auto-reads it from here)
if [ -f "$FRAMEWORK_DIR/AGENTS.md" ]; then
  if [ -f "$TARGET_DIR/AGENTS.md" ]; then
    cp "$TARGET_DIR/AGENTS.md" "$TARGET_DIR/AGENTS.md.pre-archetype"
  fi
  cp "$FRAMEWORK_DIR/AGENTS.md" "$TARGET_DIR/AGENTS.md"
  echo "  copied: AGENTS.md → project root (original guidance preserved)"
fi
if [ -f "$TARGET_DIR/CLAUDE.md" ] || [ -f "$TARGET_DIR/Claude.md" ]; then
  echo "  CLAUDE.md already exists at project root."
  echo "  Archiving existing as CLAUDE.md.pre-archetype"
  cp "$TARGET_DIR/CLAUDE.md" "$TARGET_DIR/CLAUDE.md.pre-archetype" 2>/dev/null || \
  cp "$TARGET_DIR/Claude.md" "$TARGET_DIR/CLAUDE.md.pre-archetype" 2>/dev/null
fi
cp "$FRAMEWORK_DIR/CLAUDE.md" "$TARGET_DIR/CLAUDE.md"
echo "  copied: CLAUDE.md → project root (auto-loaded by Claude Code)"

# Step 2: Everything else goes in the subfolder
mkdir -p "$DEST"

for item in AGENTS.md CLAUDE.md Conventions.md README.md LICENSE NOTICE conventions backend bootstrap scaffolding development templates scripts; do
  if [ -e "$FRAMEWORK_DIR/$item" ]; then
    cp -R "$FRAMEWORK_DIR/$item" "$DEST/"
    echo "  copied: $item → $SUBFOLDER_NAME/"
  fi
done

# Copy inject.sh and update.sh so the project can update later
cp "$FRAMEWORK_DIR/inject.sh" "$DEST/inject.sh" 2>/dev/null || true
cp "$FRAMEWORK_DIR/update.sh" "$DEST/update.sh" 2>/dev/null || true
chmod +x "$DEST/inject.sh" "$DEST/update.sh" 2>/dev/null || true

# Create VERSION-LOG.md at PROJECT ROOT (not inside archetype/).
# The framework folder stays read-only; all per-project artifacts live at the project.
LATEST_HASH=$(git -C "$FRAMEWORK_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")
if [ ! -f "$TARGET_DIR/VERSION-LOG.md" ]; then
  cat > "$TARGET_DIR/VERSION-LOG.md" << VEOF
# Version Log

Records which framework version was used and when updates were applied.
This file is managed by update.sh. Do not edit manually.

## Bootstrap

Date: $(date +%Y-%m-%d)
Source: https://github.com/d3r3nic/archetype
Commit: $LATEST_HASH
Method: inject.sh

## Updates

(none yet — run ./$SUBFOLDER_NAME/update.sh to pull the latest framework)
VEOF
  echo "  created: VERSION-LOG.md (project root)"
else
  echo "  SAFE: VERSION-LOG.md already exists at project root (not overwritten)"
fi

# Create empty docs directories at PROJECT ROOT (they hold project content, not framework content).
if [ ! -d "$TARGET_DIR/docs/systems" ]; then
  mkdir -p "$TARGET_DIR/docs/systems"
  echo "  created: docs/systems/ (project root)"
fi
if [ ! -d "$TARGET_DIR/docs/features" ]; then
  mkdir -p "$TARGET_DIR/docs/features"
  echo "  created: docs/features/ (project root)"
fi

echo ""
echo "Done. AGENTS.md (the rules) and CLAUDE.md (a pointer to it) are at the project root. Framework files are in $SUBFOLDER_NAME/."
echo ""
echo "Next steps:"
echo "  1. cd $TARGET_DIR"
echo "  2. Tell your AI assistant:"
echo ""
echo "     Read AGENTS.md, then read $SUBFOLDER_NAME/bootstrap/ONBOARD.md."
echo "     Follow the bootstrap process for this project."
echo ""
echo "  3. The AI will generate References.md and feature-tree.md."
echo "     For existing projects it will also extract rules from any"
echo "     existing instruction files."
