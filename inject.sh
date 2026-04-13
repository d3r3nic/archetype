#!/bin/bash
# Archetype Framework Injection Script
# Injects the framework into a target project.
# CLAUDE.md goes to project root (Claude Code auto-reads it).
# Everything else goes in a subfolder.
# Does not overwrite existing files without asking.

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

DEST="$TARGET_DIR/$SUBFOLDER_NAME"

if [ -d "$DEST" ]; then
  echo "Error: $DEST already exists."
  echo "Remove it first or choose a different subfolder name:"
  echo "  ./inject.sh \"$TARGET_DIR\" archetype-v2"
  exit 1
fi

echo "Archetype Framework Injection"
echo "============================="
echo "Source: $FRAMEWORK_DIR"
echo "Target: $TARGET_DIR"
echo "Subfolder: $SUBFOLDER_NAME/"
echo ""

# Step 1: CLAUDE.md goes to PROJECT ROOT (Claude Code auto-reads it from here)
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

for item in Conventions.md README.md conventions bootstrap scaffolding development templates; do
  if [ -e "$FRAMEWORK_DIR/$item" ]; then
    cp -R "$FRAMEWORK_DIR/$item" "$DEST/"
    echo "  copied: $item → $SUBFOLDER_NAME/"
  fi
done

# Copy inject.sh itself so the project can re-inject updates later
cp "$FRAMEWORK_DIR/inject.sh" "$DEST/inject.sh" 2>/dev/null || true

# Create empty docs directories the project will populate
mkdir -p "$DEST/docs/systems" "$DEST/docs/features"
echo "  created: $SUBFOLDER_NAME/docs/systems/"
echo "  created: $SUBFOLDER_NAME/docs/features/"

# Create a pointer file so the project knows where the framework came from
cat > "$DEST/FRAMEWORK-SOURCE.md" << EOF
# Framework Source

This archetype/ folder was injected from the Archetype AI Development Framework.

Source repo: https://github.com/d3r3nic/archetype
Injected on: $(date +%Y-%m-%d)

To update the framework files, re-run the inject script:
  cd /path/to/archetype-repo
  ./inject.sh "$TARGET_DIR" $SUBFOLDER_NAME

The CLAUDE.md at the project root is the enforcer.
All convention docs, templates, and phase guides live in this subfolder.
References.md and feature-tree.md are generated during bootstrap.
EOF
echo "  created: $SUBFOLDER_NAME/FRAMEWORK-SOURCE.md"

echo ""
echo "Done. CLAUDE.md is at the project root. Framework files are in $SUBFOLDER_NAME/."
echo ""
echo "Next steps:"
echo "  1. cd $TARGET_DIR"
echo "  2. Tell your AI assistant:"
echo ""
echo "     Read CLAUDE.md, then read $SUBFOLDER_NAME/bootstrap/ONBOARD.md."
echo "     Follow the bootstrap process for this project."
echo ""
echo "  3. The AI will generate References.md and feature-tree.md."
echo "     For existing projects it will also extract rules from any"
echo "     existing instruction files."
