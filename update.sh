#!/bin/bash
# Archetype Framework Update Script
# Pulls the latest framework from the repo and applies non-destructive updates.
# Universal files (conventions, templates, phase docs) are overwritten.
# Project-specific files (References.md, feature-tree.md, overrides, protocols, catalogs) are NEVER touched.

set -e

# Find the engine without assuming every installation lives below the project.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
EXPLICIT_ROOT=""
if [ "$#" -gt 0 ]; then
  if [ "$#" -ne 2 ] || [ "$1" != --project-root ] || [ ! -d "$2" ]; then
    echo "Usage: update.sh [--project-root existing-project-directory]"
    exit 1
  fi
  EXPLICIT_ROOT="$(cd "$2" && pwd -P)"
fi

# Detect if we're running from inside archetype/ or from project root
if [ -f "$SCRIPT_DIR/Conventions.md" ] && [ -d "$SCRIPT_DIR/conventions" ]; then
  ARCHETYPE_DIR="$SCRIPT_DIR"
elif [ -f "$SCRIPT_DIR/archetype/Conventions.md" ] && [ ! -L "$SCRIPT_DIR/archetype" ]; then
  ARCHETYPE_DIR="$SCRIPT_DIR/archetype"
else
  echo "Error: Cannot find archetype/ folder."
  echo "Run this script from the project root or from inside the archetype/ folder."
  exit 1
fi

ENGINE_PARENT="$(dirname "$ARCHETYPE_DIR")"
GIT_ROOT="$(git -C "$ARCHETYPE_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "$EXPLICIT_ROOT" ]; then
  if [ "$EXPLICIT_ROOT" != "$ARCHETYPE_DIR" ] && [ "$EXPLICIT_ROOT" != "$ENGINE_PARENT" ]; then
    echo "Error: project root must contain the engine directly, or be the engine for a full-clone installation."
    exit 1
  fi
  PROJECT_ROOT="$EXPLICIT_ROOT"
elif [ "$ARCHETYPE_DIR" != "$SCRIPT_DIR" ]; then
  PROJECT_ROOT="$SCRIPT_DIR"
elif [ "$GIT_ROOT" = "$ARCHETYPE_DIR" ]; then
  PROJECT_ROOT="$ARCHETYPE_DIR"
elif { [ -f "$ENGINE_PARENT/CLAUDE.md" ] || [ -f "$ENGINE_PARENT/AGENTS.md" ]; } && [ -f "$ENGINE_PARENT/VERSION-LOG.md" ]; then
  # Either entry file marks the project; step 5 recreates the other when it is missing.
  PROJECT_ROOT="$ENGINE_PARENT"
else
  echo "Error: installation layout is ambiguous. Specify --project-root explicitly."
  exit 1
fi

# Validate destinations before network access, prompts, or writes.
UNIVERSAL_FILES="AGENTS.md CLAUDE.md Conventions.md README.md inject.sh"
UNIVERSAL_DIRS="conventions backend frontend bootstrap scaffolding development templates scripts"
# The engine's own license and notice. Installed only when BOTH are missing, so a
# project-owned license never gains a notice that contradicts it, and never
# overwritten, whatever shape the existing path has. In a full-clone layout the
# engine folder IS the project root, so they are installed under engine-specific
# names there and the project's own LICENSE and NOTICE are left alone.
LICENSE_FILES="LICENSE NOTICE"
if [ "$PROJECT_ROOT" = "$ARCHETYPE_DIR" ]; then
  LICENSE_SUFFIX="-ARCHETYPE"
else
  LICENSE_SUFFIX=""
fi
license_target() {
  echo "$ARCHETYPE_DIR/$1$LICENSE_SUFFIX"
}
license_display() {
  target="$(license_target "$1")"
  printf '%s\n' "${target#"$PROJECT_ROOT"/}"
}
for file in $UNIVERSAL_FILES update.sh; do
  if [ -L "$ARCHETYPE_DIR/$file" ] || { [ -e "$ARCHETYPE_DIR/$file" ] && [ ! -f "$ARCHETYPE_DIR/$file" ]; }; then
    echo "Error: engine $file must be a regular file."
    exit 1
  fi
done
for file in AGENTS.md CLAUDE.md VERSION-LOG.md; do
  if [ -L "$PROJECT_ROOT/$file" ] || { [ -e "$PROJECT_ROOT/$file" ] && [ ! -f "$PROJECT_ROOT/$file" ]; }; then
    echo "Error: project $file must be a regular file."
    exit 1
  fi
done
for dir in $UNIVERSAL_DIRS; do
  if [ -L "$ARCHETYPE_DIR/$dir" ] || { [ -e "$ARCHETYPE_DIR/$dir" ] && [ ! -d "$ARCHETYPE_DIR/$dir" ]; }; then
    echo "Error: engine $dir must be a local directory."
    exit 1
  fi
done
if [ -L "$PROJECT_ROOT/conventions" ]; then
  echo "Error: project conventions must be a local directory."
  exit 1
fi

FRAMEWORK_REPO="https://github.com/d3r3nic/archetype.git"
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "Archetype Framework Update"
echo "=========================="
echo "Project: $PROJECT_ROOT"
echo "Engine:  $ARCHETYPE_DIR"
echo ""

# Step 1: Clone latest framework to temp
echo "Pulling latest framework..."
if ! git clone --quiet --depth 1 "$FRAMEWORK_REPO" "$TEMP_DIR"; then
  echo "Error: Could not clone framework repo. Check your internet connection."
  rm -rf "$TEMP_DIR"
  exit 1
fi
echo "  Latest framework pulled."
echo ""

# An update never deletes a project's words. Each root entry file is compared with a
# baseline: the engine's copy from before this update, or, where the engine folder is the
# project root (a full clone) or never carried the file, the file at the framework
# revision VERSION-LOG.md records. Lines the project added are carried into
# CLAUDE.md.additions for audit and the previous file is kept beside it. A file with
# nothing new to carry whose framework lines were removed, reordered or repeated is kept
# too, and the additions file asks for a review of that change. With no baseline, or a
# root AGENTS.md without the managed marker, the previous file is kept whole and the
# additions file points at it. Comparison ignores a trailing carriage return, and blank
# lines when looking for removed or reordered lines; the kept copy keeps the original
# bytes. Nothing is written until the prompt is answered.
ADD="$PROJECT_ROOT/CLAUDE.md.additions"
if [ -L "$ADD" ] || { [ -e "$ADD" ] && [ ! -f "$ADD" ]; }; then
  echo "Error: project CLAUDE.md.additions must be a regular file."
  exit 1
fi
CARRY_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR" "$CARRY_DIR"' EXIT
RECORDED=""
[ -f "$PROJECT_ROOT/VERSION-LOG.md" ] && RECORDED=$(sed -n 's/^Commit: *\([0-9a-f]\{7,40\}\).*/\1/p' "$PROJECT_ROOT/VERSION-LOG.md" | tail -1)
strip_cr() { sed 's/\r$//' "$1"; }
# The recorded revision is fetched once, on first need; call this outside a subshell.
RECORDED_FETCH=""
recorded_available() {
  if [ -z "$RECORDED_FETCH" ]; then
    RECORDED_FETCH=no
    if [ "${#RECORDED}" -eq 40 ] && git -C "$TEMP_DIR" fetch --quiet --depth 1 origin "$RECORDED" 2>/dev/null; then
      RECORDED_FETCH=yes
    fi
  fi
  [ "$RECORDED_FETCH" = yes ]
}
recorded_file() {
  recorded_available && git -C "$TEMP_DIR" show "$RECORDED:$1" > "$2" 2>/dev/null
}

plan_carry() {
  name="$1"
  root="$PROJECT_ROOT/$name"
  [ -f "$root" ] || return 0
  cmp -s "$root" "$TEMP_DIR/$name" && return 0
  base="$CARRY_DIR/$name.base"
  if [ "$PROJECT_ROOT" != "$ARCHETYPE_DIR" ] && [ -f "$ARCHETYPE_DIR/$name" ]; then
    cp "$ARCHETYPE_DIR/$name" "$base"
  elif ! recorded_file "$name" "$base"; then
    rm -f "$base"
  fi
  if [ "$name" = AGENTS.md ] && ! grep -qF '<!-- archetype-managed-entrypoint -->' "$root"; then
    echo unmanaged > "$CARRY_DIR/$name.mode"
  elif [ -s "$base" ]; then
    strip_cr "$base" > "$CARRY_DIR/$name.base.lf"
    strip_cr "$root" | grep -vxFf "$CARRY_DIR/$name.base.lf" | grep -v '^[[:space:]]*$' | awk '!seen[$0]++' > "$CARRY_DIR/$name.added" || true
    if [ -s "$ADD" ]; then
      strip_cr "$ADD" > "$CARRY_DIR/additions.lf"
      grep -vxFf "$CARRY_DIR/additions.lf" "$CARRY_DIR/$name.added" > "$CARRY_DIR/$name.lines" || true
    else
      cp "$CARRY_DIR/$name.added" "$CARRY_DIR/$name.lines"
    fi
    if [ -s "$CARRY_DIR/$name.lines" ]; then
      echo lines > "$CARRY_DIR/$name.mode"
    else
      # Nothing to carry. The framework lines the root file still has, in order and
      # without blank lines, must match the baseline's; otherwise the project removed,
      # reordered or repeated some, and that arrangement is kept for review.
      strip_cr "$root" | grep -xFf "$CARRY_DIR/$name.base.lf" | grep -v '^[[:space:]]*$' > "$CARRY_DIR/$name.order" || true
      grep -v '^[[:space:]]*$' "$CARRY_DIR/$name.base.lf" > "$CARRY_DIR/$name.base.order" || true
      cmp -s "$CARRY_DIR/$name.order" "$CARRY_DIR/$name.base.order" && return 0
      echo reshaped > "$CARRY_DIR/$name.mode"
    fi
  else
    echo whole > "$CARRY_DIR/$name.mode"
  fi
  cp "$root" "$CARRY_DIR/$name.previous"
}
plan_carry CLAUDE.md
plan_carry AGENTS.md

# Step 2: Show what would change
echo "Comparing files..."
echo ""

CHANGES=0
NEW_FILES=0
SKIPPED=0

# Files that get OVERWRITTEN (universal, framework-owned)
# NOTE: update.sh is NOT in this list — it replaces itself atomically at the
# end of the script (see Step 9). Putting it in the main loop caused the
# running bash to read corrupted data from its own rewritten file.

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
if [ "$PROJECT_ROOT" != "$ARCHETYPE_DIR" ]; then
  for file in AGENTS.md CLAUDE.md; do
    if [ -f "$TEMP_DIR/$file" ] && [ ! -e "$PROJECT_ROOT/$file" ]; then
      echo "  NEW: $file (project root)"
      NEW_FILES=$((NEW_FILES + 1))
    fi
  done
fi

# License and notice: decided as a pair, never overwritten.
LICENSE_ACTION="none"
LICENSE_SOURCE_COMPLETE=1
LICENSE_ANY_PRESENT=0
for file in $LICENSE_FILES; do
  [ -f "$TEMP_DIR/$file" ] || LICENSE_SOURCE_COMPLETE=0
  target="$(license_target "$file")"
  if [ -e "$target" ] || [ -L "$target" ]; then
    LICENSE_ANY_PRESENT=1
  fi
done
# A full clone already carries the engine license at its root under the plain name.
LICENSE_ALREADY_CARRIED=0
if [ -n "$LICENSE_SUFFIX" ] && [ -f "$TEMP_DIR/LICENSE" ] && [ -f "$ARCHETYPE_DIR/LICENSE" ] && \
   diff -q "$TEMP_DIR/LICENSE" "$ARCHETYPE_DIR/LICENSE" > /dev/null 2>&1; then
  LICENSE_ALREADY_CARRIED=1
fi
if [ "$LICENSE_SOURCE_COMPLETE" = 1 ] && [ "$LICENSE_ALREADY_CARRIED" = 0 ]; then
  if [ "$LICENSE_ANY_PRESENT" = 0 ]; then
    LICENSE_ACTION="install"
  else
    LICENSE_ACTION="keep"
  fi
fi

# Report only what the run will actually do. A copy identical to the source is
# already correct and says nothing.
LICENSE_REPORT=""
for file in $LICENSE_FILES; do
  target="$(license_target "$file")"
  if [ "$LICENSE_ACTION" = "install" ]; then
    LICENSE_REPORT="$LICENSE_REPORT  NEW: $(license_display "$file")
"
    NEW_FILES=$((NEW_FILES + 1))
  elif [ "$LICENSE_ACTION" = "keep" ]; then
    if [ -f "$target" ] && [ ! -L "$target" ] && diff -q "$TEMP_DIR/$file" "$target" > /dev/null 2>&1; then
      continue
    elif [ -e "$target" ] || [ -L "$target" ]; then
      LICENSE_REPORT="$LICENSE_REPORT  KEPT: $(license_display "$file") (your copy, not replaced)
"
    else
      LICENSE_REPORT="$LICENSE_REPORT  SKIPPED: $(license_display "$file") (not added while the other file of the pair is present)
"
    fi
  fi
done
if [ -n "$LICENSE_REPORT" ]; then
  echo ""
  echo "--- License and notice (installed only when missing, never overwritten) ---"
  printf '%s' "$LICENSE_REPORT"
fi

# update.sh is handled separately (atomic self-replace at end)
if [ -f "$TEMP_DIR/update.sh" ] && [ -f "$ARCHETYPE_DIR/update.sh" ]; then
  if ! diff -q "$TEMP_DIR/update.sh" "$ARCHETYPE_DIR/update.sh" > /dev/null 2>&1; then
    echo "  CHANGED: update.sh (self-replace at end)"
    CHANGES=$((CHANGES + 1))
  fi
fi

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

CARRY_SHOWN=0
for name in CLAUDE.md AGENTS.md; do
  [ -f "$CARRY_DIR/$name.mode" ] || continue
  CARRY_SHOWN=1
  case "$(cat "$CARRY_DIR/$name.mode")" in
    lines) echo "  CARRIED: $(wc -l < "$CARRY_DIR/$name.lines" | tr -d ' ') line(s) this project added to root $name go to CLAUDE.md.additions for audit; the previous file is kept" ;;
    reshaped) echo "  KEPT: root $name had framework lines removed, reordered or repeated by this project; it is kept whole beside the managed file and named in CLAUDE.md.additions for review" ;;
    unmanaged) echo "  KEPT: root $name is this project's own guidance; it is kept whole beside the managed file and named in CLAUDE.md.additions" ;;
    whole) echo "  KEPT: root $name differs and no baseline exists to tell this project's lines apart; it is kept whole beside the managed file and named in CLAUDE.md.additions" ;;
  esac
done
[ "$CARRY_SHOWN" -eq 1 ] && echo ""

# Files that are NEVER touched (project-specific)
echo "--- Project-specific files (will NOT be touched) ---"
for skip in References.md feature-tree.md INDEX.md MIGRATION-NOTES.md CLAUDE.md.additions; do
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

# Step 3b: Keep the project's words before anything is replaced
STAMP=$(date +%Y%m%d)
kept_path() {
  kept="$PROJECT_ROOT/$1.pre-update-$STAMP"
  n=1
  while [ -e "$kept" ] || [ -L "$kept" ]; do n=$((n + 1)); kept="$PROJECT_ROOT/$1.pre-update-$STAMP-$n"; done
  printf '%s\n' "$kept"
}
for name in CLAUDE.md AGENTS.md; do
  [ -f "$CARRY_DIR/$name.mode" ] || continue
  mode="$(cat "$CARRY_DIR/$name.mode")"
  kept="$(kept_path "$name")"
  block="$CARRY_DIR/$name.block"
  {
    if [ -s "$ADD" ]; then
      [ -n "$(tail -c 1 "$ADD")" ] && echo ""
      echo ""
    fi
    if [ "$mode" = reshaped ]; then
      echo "## Root $name kept by the framework update of $(date +%Y-%m-%d): review what this project removed or reordered"
      echo ""
      echo "The update replaced root $name with the managed file. The previous file is kept whole as $(basename "$kept"). In it this project had removed, reordered or repeated framework lines; any line of its own is already in this file. Compare it with the managed file and decide whether that intent still matters: if it does, record it in this file, References.md or conventions/overrides/ with the reason. Remove this heading when the review is done."
    else
      echo "## Carried over from root $name by the framework update of $(date +%Y-%m-%d): audit each line"
      echo ""
      echo "The update replaced root $name with the managed file. The previous file is kept whole as $(basename "$kept"). Audit what follows against the current rules: keep a line here, move it to References.md or conventions/overrides/, or retire it because the current rules cover it, and record the reason. Remove this heading when the audit is done."
      echo ""
      case "$mode" in
        lines) cat "$CARRY_DIR/$name.lines" ;;
        unmanaged) echo "Root $name carried no managed marker, so it was this project's own file: read $(basename "$kept") in full." ;;
        whole) echo "No baseline existed to tell this project's lines from the framework's: read $(basename "$kept") in full." ;;
      esac
    fi
  } > "$block"
  if ! cp "$CARRY_DIR/$name.previous" "$kept"; then
    echo "Error: could not keep the previous root $name. Nothing was replaced."
    exit 1
  fi
  if ! cat "$block" >> "$ADD"; then
    echo "Error: could not write CLAUDE.md.additions. The previous root $name is kept as $(basename "$kept"); nothing was replaced."
    exit 1
  fi
  if [ "$mode" = reshaped ]; then
    echo "  kept: root $name as $(basename "$kept") (named in CLAUDE.md.additions for review)"
  else
    echo "  carried: root $name → CLAUDE.md.additions (previous file kept as $(basename "$kept"))"
  fi
done

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

if [ "$LICENSE_ACTION" = "install" ]; then
  for file in $LICENSE_FILES; do
    cp "$TEMP_DIR/$file" "$(license_target "$file")"
    echo "  installed: $(license_display "$file")"
  done
fi

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

# Step 5: Update the root entry files, creating one that is missing, so the CLAUDE.md
# that imports the rules reaches every installation. In a full clone the engine's copies
# are the root files and step 4 already replaced them.
if [ "$PROJECT_ROOT" != "$ARCHETYPE_DIR" ]; then
  for file in CLAUDE.md AGENTS.md; do
    [ -f "$TEMP_DIR/$file" ] || continue
    if [ -f "$PROJECT_ROOT/$file" ]; then verb=updated; else verb=created; fi
    cp "$TEMP_DIR/$file" "$PROJECT_ROOT/$file"
    echo "  $verb: $file (project root)"
  done
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

# Step 7: Migrate legacy project artifacts that used to live inside archetype/.
# Keeps the framework folder read-only. Safe to run repeatedly.
if [ "$ARCHETYPE_DIR" != "$PROJECT_ROOT" ]; then
  if [ -f "$ARCHETYPE_DIR/VERSION-LOG.md" ]; then
    if [ -f "$PROJECT_ROOT/VERSION-LOG.md" ]; then
      echo "  WARN: both archetype/VERSION-LOG.md and project-root VERSION-LOG.md exist; deleting the archetype/ copy"
      rm -f "$ARCHETYPE_DIR/VERSION-LOG.md"
    else
      mv "$ARCHETYPE_DIR/VERSION-LOG.md" "$PROJECT_ROOT/VERSION-LOG.md"
      echo "  migrated: VERSION-LOG.md archetype/ → project root"
    fi
  fi
  if [ -f "$ARCHETYPE_DIR/FRAMEWORK-SOURCE.md" ]; then
    rm -f "$ARCHETYPE_DIR/FRAMEWORK-SOURCE.md"
    echo "  removed: archetype/FRAMEWORK-SOURCE.md (redundant with VERSION-LOG.md)"
  fi
  if [ -d "$ARCHETYPE_DIR/docs" ]; then
    rmdir "$ARCHETYPE_DIR/docs/systems" "$ARCHETYPE_DIR/docs/features" "$ARCHETYPE_DIR/docs" 2>/dev/null && \
      echo "  removed: archetype/docs/ (empty; project docs live at project root)"
  fi
fi

# Step 8: Append to VERSION-LOG.md (project root).
VERSION_LOG="$PROJECT_ROOT/VERSION-LOG.md"
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
LATEST_HASH=$(git -C "$TEMP_DIR" rev-parse HEAD 2>/dev/null || echo "unknown")

# Append update entry
echo "" >> "$VERSION_LOG"
echo "### $(date +%Y-%m-%d)" >> "$VERSION_LOG"
echo "Commit: $LATEST_HASH" >> "$VERSION_LOG"
echo "Source: $FRAMEWORK_REPO" >> "$VERSION_LOG"
echo "Updated by: update.sh" >> "$VERSION_LOG"
echo "  updated: VERSION-LOG.md (project root)"

# Step 9: Atomic self-replace of update.sh (LAST, after all other work)
# cp + mv keeps the running bash safe: mv is a rename, so the old inode stays
# alive as long as bash holds it open. Plain cp would truncate-and-write,
# which corrupts bash's read position mid-execution.
if [ -f "$TEMP_DIR/update.sh" ]; then
  if ! diff -q "$TEMP_DIR/update.sh" "$ARCHETYPE_DIR/update.sh" > /dev/null 2>&1; then
    NEXT_UPDATER=$(mktemp "$ARCHETYPE_DIR/.update.sh.XXXXXX")
    cp "$TEMP_DIR/update.sh" "$NEXT_UPDATER"
    chmod +x "$NEXT_UPDATER"
    mv -f "$NEXT_UPDATER" "$ARCHETYPE_DIR/update.sh"
    echo "  updated: archetype/update.sh (self, atomic replace)"
  fi
fi

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "Update complete."
echo ""
echo "What was updated:"
echo "  - Universal convention docs"
echo "  - AGENTS.md and CLAUDE.md (managed entry points)"
echo "  - Conventions.md (lookup index)"
echo "  - Phase docs (bootstrap, scaffold, develop, maintain)"
echo "  - Templates"
echo ""
echo "What was NOT touched:"
if [ "$LICENSE_ACTION" != "install" ]; then
  echo "  - LICENSE and NOTICE you already had (the engine's own copies are only added when both are missing)"
fi
echo "  - References.md (project-specific)"
echo "  - feature-tree.md (project-specific)"
echo "  - conventions/overrides/ (project-specific)"
echo "  - protocols/ (project-specific)"
echo "  - catalogs/ (project-specific)"
echo "  - docs/ (project-specific)"
echo "  - todo/ (project-specific)"
echo ""
echo "Next: follow archetype/development/UPDATE.md, section After (audit what the update added to CLAUDE.md.additions, run the checks, commit as one change)."
