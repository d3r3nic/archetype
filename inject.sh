#!/bin/bash
# Archetype Framework Injection Script
# Copies the framework into a target project as a subfolder.
# Does not modify any existing project files.

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
echo "Target: $DEST"
echo ""

mkdir -p "$DEST"

# Copy framework files (skip git, node_modules, libraries, the inject script itself)
for item in CLAUDE.md Conventions.md README.md conventions bootstrap scaffolding development templates; do
  if [ -e "$FRAMEWORK_DIR/$item" ]; then
    cp -R "$FRAMEWORK_DIR/$item" "$DEST/"
    echo "  copied: $item"
  fi
done

# Create empty docs directories the project will populate
mkdir -p "$DEST/docs/systems" "$DEST/docs/features"
echo "  created: docs/systems/"
echo "  created: docs/features/"

echo ""
echo "Framework injected at: $DEST"
echo ""
echo "Next steps:"
echo "  1. cd $TARGET_DIR"
echo "  2. Tell your AI assistant:"
echo ""
echo "     Read $SUBFOLDER_NAME/bootstrap/ONBOARD.md and follow the existing"
echo "     project path. Scan this codebase, generate References.md and"
echo "     feature-tree.md inside $SUBFOLDER_NAME/. Do not modify any existing"
echo "     project files."
echo ""
echo "  3. Once the AI generates the framework files inside $SUBFOLDER_NAME/,"
echo "     review them. When ready to promote them to the project root,"
echo "     archive your old CLAUDE.md and copy the new framework files up."
