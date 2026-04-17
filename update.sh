#!/bin/bash
# Archetype Framework Update Script
# Pulls the latest framework from the repo and applies non-destructive updates.
# Universal files (conventions, templates, phase docs) are overwritten.
# Project-specific files (References.md, feature-tree.md, overrides, protocols, catalogs) are NEVER touched.

set -e

# Find the archetype/ subfolder
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect if we're running from inside archetype/ or from project root
if [ -f "$SCRIPT_DIR/Conventions.md" ] && [ -d "$SCRIPT_DIR/conventions" ]; then
  ARCHETYPE_DIR="$SCRIPT_DIR"
elif [ -d "$SCRIPT_DIR/archetype" ]; then
  ARCHETYPE_DIR="$SCRIPT_DIR/archetype"
else
  echo "Error: Cannot find archetype/ folder."
  echo "Run this script from the project root or from inside the archetype/ folder."
  exit 1
fi

PROJECT_ROOT="$(dirname "$ARCHETYPE_DIR")"
if [ "$(basename "$ARCHETYPE_DIR")" = "$(basename "$PROJECT_ROOT")" ]; then
  PROJECT_ROOT="$ARCHETYPE_DIR/.."
fi

# If archetype/ IS the project root (new project clone), adjust
if [ "$ARCHETYPE_DIR" = "$PROJECT_ROOT" ]; then
  PROJECT_ROOT="$ARCHETYPE_DIR"
fi

FRAMEWORK_REPO="https://github.com/d3r3nic/archetype.git"
TEMP_DIR=$(mktemp -d)

echo "Archetype Framework Update"
echo "=========================="
echo "Project: $PROJECT_ROOT"
echo "Engine:  $ARCHETYPE_DIR"
echo ""

# Step 1: Clone latest framework to temp
echo "Pulling latest framework..."
git clone --quiet --depth 1 "$FRAMEWORK_REPO" "$TEMP_DIR" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Error: Could not clone framework repo. Check your internet connection."
  rm -rf "$TEMP_DIR"
  exit 1
fi
echo "  Latest framework pulled."
echo ""

# Step 2: Show what would change
echo "Comparing files..."
echo ""

CHANGES=0
NEW_FILES=0
SKIPPED=0

# Files that get OVERWRITTEN (universal, framework-owned)
UNIVERSAL_FILES="CLAUDE.md Conventions.md README.md inject.sh update.sh"
UNIVERSAL_DIRS="conventions backend frontend bootstrap scaffolding development templates scripts"

echo "--- Universal files (will be updated) ---"
for file in $UNIVERSAL_FILES; do
  if [ -f "$TEMP_DIR/$file" ]; then
    if [ -f "$ARCHETYPE_DIR/$file" ]; then
      if ! diff -q "$TEMP_DIR/$file" "$ARCHETYPE_DIR/$file" > /dev/null 2>&1; then
        echo "  CHANGED: $file"
        CHANGES=$((CHANGES + 1))
      fi
    else
      echo "  NEW: $file"
      NEW_FILES=$((NEW_FILES + 1))
    fi
  fi
done

for dir in $UNIVERSAL_DIRS; do
  if [ -d "$TEMP_DIR/$dir" ]; then
    # Check each file in the directory
    find "$TEMP_DIR/$dir" -type f -name "*.md" -o -name "*.sh" | while read src_file; do
      rel_path="${src_file#$TEMP_DIR/}"
      dest_file="$ARCHETYPE_DIR/$rel_path"
      if [ -f "$dest_file" ]; then
        if ! diff -q "$src_file" "$dest_file" > /dev/null 2>&1; then
          echo "  CHANGED: $rel_path"
        fi
      else
        echo "  NEW: $rel_path"
      fi
    done
  fi
done

echo ""

# Files that are NEVER touched (project-specific)
echo "--- Project-specific files (will NOT be touched) ---"
for skip in References.md feature-tree.md INDEX.md MIGRATION-NOTES.md CLAUDE.md.additions FRAMEWORK-SOURCE.md; do
  if [ -f "$ARCHETYPE_DIR/$skip" ]; then
    echo "  SAFE: $skip"
    SKIPPED=$((SKIPPED + 1))
  fi
done
for skip_dir in conventions/overrides protocols catalogs todo docs; do
  if [ -d "$ARCHETYPE_DIR/$skip_dir" ]; then
    echo "  SAFE: $skip_dir/ (entire directory)"
    SKIPPED=$((SKIPPED + 1))
  fi
done

echo ""

# Step 3: Ask for confirmation
read -p "Apply updates? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Update cancelled."
  rm -rf "$TEMP_DIR"
  exit 0
fi

# Step 4: Apply updates
echo ""
echo "Applying updates..."

# Update universal files in archetype/
for file in $UNIVERSAL_FILES; do
  if [ -f "$TEMP_DIR/$file" ]; then
    cp "$TEMP_DIR/$file" "$ARCHETYPE_DIR/$file"
    echo "  updated: archetype/$file"
  fi
done

for dir in $UNIVERSAL_DIRS; do
  if [ -d "$TEMP_DIR/$dir" ]; then
    # Don't delete existing overrides in conventions/
    if [ "$dir" = "conventions" ] && [ -d "$ARCHETYPE_DIR/conventions/overrides" ]; then
      # Save overrides, update conventions, restore overrides
      OVERRIDE_BACKUP=$(mktemp -d)
      cp -R "$ARCHETYPE_DIR/conventions/overrides" "$OVERRIDE_BACKUP/"
      rm -rf "$ARCHETYPE_DIR/conventions"
      cp -R "$TEMP_DIR/conventions" "$ARCHETYPE_DIR/conventions"
      cp -R "$OVERRIDE_BACKUP/overrides" "$ARCHETYPE_DIR/conventions/"
      rm -rf "$OVERRIDE_BACKUP"
      echo "  updated: archetype/conventions/ (overrides preserved)"
    else
      rm -rf "$ARCHETYPE_DIR/$dir"
      cp -R "$TEMP_DIR/$dir" "$ARCHETYPE_DIR/$dir"
      echo "  updated: archetype/$dir/"
    fi
  fi
done

# Step 5: Update CLAUDE.md at project root
if [ -f "$PROJECT_ROOT/CLAUDE.md" ] && [ "$PROJECT_ROOT" != "$ARCHETYPE_DIR" ]; then
  cp "$TEMP_DIR/CLAUDE.md" "$PROJECT_ROOT/CLAUDE.md"
  echo "  updated: CLAUDE.md (project root)"
fi

# Step 6: Update promoted conventions/ at project root if they exist
if [ -d "$PROJECT_ROOT/conventions" ] && [ "$PROJECT_ROOT" != "$ARCHETYPE_DIR" ]; then
  # Same override-safe approach
  if [ -d "$PROJECT_ROOT/conventions/overrides" ]; then
    OVERRIDE_BACKUP=$(mktemp -d)
    cp -R "$PROJECT_ROOT/conventions/overrides" "$OVERRIDE_BACKUP/"
    rm -rf "$PROJECT_ROOT/conventions"
    cp -R "$TEMP_DIR/conventions" "$PROJECT_ROOT/conventions"
    cp -R "$OVERRIDE_BACKUP/overrides" "$PROJECT_ROOT/conventions/"
    rm -rf "$OVERRIDE_BACKUP"
  else
    rm -rf "$PROJECT_ROOT/conventions"
    cp -R "$TEMP_DIR/conventions" "$PROJECT_ROOT/conventions"
  fi
  echo "  updated: conventions/ (project root, overrides preserved)"
fi

# Step 7: Update FRAMEWORK-SOURCE.md
cat > "$ARCHETYPE_DIR/FRAMEWORK-SOURCE.md" << EOF
# Framework Source

This archetype/ folder is powered by the Archetype AI Development Framework.

Source repo: $FRAMEWORK_REPO
Last updated: $(date +%Y-%m-%d)
Update command: cd archetype && ./update.sh

The CLAUDE.md at the project root is the enforcer.
All convention docs, templates, and phase guides live in this subfolder.
References.md and feature-tree.md are project-specific and never overwritten by updates.
EOF

# Step 8: Append to VERSION-LOG.md
VERSION_LOG="$ARCHETYPE_DIR/VERSION-LOG.md"
if [ ! -f "$VERSION_LOG" ]; then
  cat > "$VERSION_LOG" << VEOF
# Version Log

Records which framework version was used and when updates were applied.
This file is managed by update.sh. Do not edit manually.

## Bootstrap

Date: unknown (pre-versioning)
Source: $FRAMEWORK_REPO

## Updates
VEOF
fi

# Get the latest commit hash from the cloned repo
LATEST_HASH=$(git -C "$TEMP_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Append update entry
echo "" >> "$VERSION_LOG"
echo "### $(date +%Y-%m-%d)" >> "$VERSION_LOG"
echo "Commit: $LATEST_HASH" >> "$VERSION_LOG"
echo "Source: $FRAMEWORK_REPO" >> "$VERSION_LOG"
echo "Updated by: update.sh" >> "$VERSION_LOG"
echo "  updated: VERSION-LOG.md"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "Update complete."
echo ""
echo "What was updated:"
echo "  - Universal convention docs (23 files)"
echo "  - CLAUDE.md (enforcer at project root)"
echo "  - Conventions.md (lookup index)"
echo "  - Phase docs (bootstrap, scaffold, develop, maintain)"
echo "  - Templates"
echo ""
echo "What was NOT touched:"
echo "  - References.md (project-specific)"
echo "  - feature-tree.md (project-specific)"
echo "  - conventions/overrides/ (project-specific)"
echo "  - protocols/ (project-specific)"
echo "  - catalogs/ (project-specific)"
echo "  - docs/ (project-specific)"
echo "  - todo/ (project-specific)"
echo ""
echo "Review the changes and commit when satisfied."
