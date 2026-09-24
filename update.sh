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
# Messages show engine paths relative to the project root: the engine folder's own name,
# or nothing where the engine folder is the project root (a full clone).
if [ "$PROJECT_ROOT" = "$ARCHETYPE_DIR" ]; then
  ENGINE_REL=""
else
  ENGINE_REL="${ARCHETYPE_DIR#"$PROJECT_ROOT"/}/"
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
# The recorded revision is fetched once, on first need; call this outside a subshell. In a
# full clone the framework's history is already here, so it is only looked up.
RECORDED_FETCH=""
recorded_available() {
  if [ -z "$RECORDED_FETCH" ]; then
    RECORDED_FETCH=no
    if [ "${#RECORDED}" -eq 40 ]; then
      if git -C "$TEMP_DIR" cat-file -e "$RECORDED^{commit}" 2>/dev/null || \
         git -C "$TEMP_DIR" fetch --quiet --depth 1 origin "$RECORDED" 2>/dev/null; then
        RECORDED_FETCH=yes
      fi
    fi
  fi
  [ "$RECORDED_FETCH" = yes ]
}
recorded_file() {
  recorded_available && git -C "$TEMP_DIR" show "$RECORDED:$1" > "$2" 2>/dev/null
}

# In a full clone the framework's folders sit at the project root and each is replaced
# whole, and the root Conventions.md and inject.sh are replaced too. A file there is the
# framework's only if the framework shipped exactly that content (the same git blob) at
# that path in some revision of its history. Anything else (a project file, a file at a
# path the framework has started shipping, an edited framework file, shipped or retired)
# would be overwritten or deleted, so the update stops here, before anything is written,
# and names it. conventions/overrides/ survives the replacement; .DS_Store files and
# __pycache__ folders are caches. README.md and the entry files have their own handling.
# Every step's exit status is checked: a step that fails stops the update instead of
# leaving the list of files incomplete.
not_verified() {
  echo "Error: $1 Nothing was changed."
  exit 1
}
if [ "$PROJECT_ROOT" = "$ARCHETYPE_DIR" ]; then
  HISTORY_ERROR="could not fetch the framework's history, which this layout needs to tell the framework's files from the project's. Check the connection and run the update again."
  if [ "$(git -C "$TEMP_DIR" rev-parse --is-shallow-repository 2>/dev/null)" = true ] && \
     ! git -C "$TEMP_DIR" fetch --quiet --unshallow origin; then
    not_verified "$HISTORY_ERROR"
  fi
  if ! git -C "$TEMP_DIR" fetch --quiet --tags origin '+refs/heads/*:refs/remotes/origin/*' || \
     [ "$(git -C "$TEMP_DIR" rev-parse --is-shallow-repository 2>/dev/null)" != false ]; then
    not_verified "$HISTORY_ERROR"
  fi
  # The recorded revision may sit on no branch; its files count when it can be fetched.
  # Optional: if it cannot be fetched, the branch and tag history stands and unmatched files still stop.
  HISTORY_REVS="--all"
  if [ "${#RECORDED}" -eq 40 ]; then
    git -C "$TEMP_DIR" cat-file -e "$RECORDED^{commit}" 2>/dev/null || \
      git -C "$TEMP_DIR" fetch --quiet origin "$RECORDED" 2>/dev/null || true
    if git -C "$TEMP_DIR" cat-file -e "$RECORDED^{commit}" 2>/dev/null; then HISTORY_REVS="--all $RECORDED"; fi
  fi
  if ! git -C "$TEMP_DIR" -c core.quotePath=false log $HISTORY_REVS --no-renames -m --root --raw --no-abbrev --format= \
       > "$CARRY_DIR/history.raw" || \
     ! awk -F'\t' '/^:/ { split($1, f, " "); if (f[4] !~ /^0+$/) print $2 "\t" f[4] }' "$CARRY_DIR/history.raw" \
       > "$CARRY_DIR/history.unsorted" || \
     ! LC_ALL=C sort -u "$CARRY_DIR/history.unsorted" > "$CARRY_DIR/history.pairs" || \
     [ ! -s "$CARRY_DIR/history.pairs" ] || \
     ! cut -f1 "$CARRY_DIR/history.pairs" > "$CARRY_DIR/history.paths"; then
    not_verified "could not read the framework's history."
  fi
  EXEMPT='(^|/)\.DS_Store$|(^|/)__pycache__/'
  [ -d "$ARCHETYPE_DIR/conventions/overrides" ] && EXEMPT="^conventions/overrides(/|\$)|$EXEMPT"
  : > "$CARRY_DIR/local.files"
  : > "$CARRY_DIR/local.other"
  for dir in $UNIVERSAL_DIRS; do
    [ -d "$TEMP_DIR/$dir" ] && [ -d "$ARCHETYPE_DIR/$dir" ] || continue
    if ! (cd "$ARCHETYPE_DIR" && find "$dir" -type f) > "$CARRY_DIR/found.files" || \
       ! (cd "$ARCHETYPE_DIR" && find "$dir" ! -type d ! -type f) > "$CARRY_DIR/found.other"; then
      not_verified "could not list every file in $dir/, so the update cannot tell the framework's files from the project's there."
    fi
    for kind in files other; do
      status=0
      grep -Ev "$EXEMPT" "$CARRY_DIR/found.$kind" >> "$CARRY_DIR/local.$kind" || status=$?
      [ "$status" -le 1 ] || not_verified "could not filter the list of files in $dir/."
    done
  done
  for file in Conventions.md inject.sh; do
    if [ -f "$TEMP_DIR/$file" ] && [ -f "$ARCHETYPE_DIR/$file" ]; then
      printf '%s\n' "$file" >> "$CARRY_DIR/local.files"
    fi
  done
  # Each file's bytes are hashed as they are, in the framework clone's repository with
  # filters off, so no git configuration, attribute or filter of the project is read or run.
  # hash_list reads absolute paths (file $1) and writes each path relative to the project
  # root with its blob, sorted (file $3); $2 holds those relative paths in the same order.
  hash_list() {
    git -C "$TEMP_DIR" hash-object --no-filters --stdin-paths < "$1" > "$CARRY_DIR/hashed.blobs" && \
      [ "$(wc -l < "$CARRY_DIR/hashed.blobs")" -eq "$(wc -l < "$2")" ] && \
      paste "$2" "$CARRY_DIR/hashed.blobs" > "$CARRY_DIR/hashed.unsorted" && \
      LC_ALL=C sort "$CARRY_DIR/hashed.unsorted" > "$3"
  }
  : > "$CARRY_DIR/local.pairs"
  if [ -s "$CARRY_DIR/local.files" ]; then
    while IFS= read -r path; do printf '%s/%s\n' "$ARCHETYPE_DIR" "$path"; done < "$CARRY_DIR/local.files" > "$CARRY_DIR/local.absolute"
    hash_list "$CARRY_DIR/local.absolute" "$CARRY_DIR/local.files" "$CARRY_DIR/local.pairs" || \
      not_verified "could not read every file in the framework's folders."
  fi
  if ! LC_ALL=C comm -23 "$CARRY_DIR/local.pairs" "$CARRY_DIR/history.pairs" > "$CARRY_DIR/local.unmatched" || \
     ! cut -f1 "$CARRY_DIR/local.unmatched" > "$CARRY_DIR/unmatched.files"; then
    not_verified "could not compare the files with the framework's history."
  fi
  # A checkout that converted line endings: the same bytes with each carriage return that
  # comes before a line feed removed, by a plain text tool, may match too. Nothing else does.
  : > "$CARRY_DIR/unverified"
  if [ -s "$CARRY_DIR/unmatched.files" ]; then
    mkdir "$CARRY_DIR/lf"
    n=0
    : > "$CARRY_DIR/lf.absolute"
    while IFS= read -r path; do
      n=$((n + 1))
      if [ -z "$(tail -c 1 "$ARCHETYPE_DIR/$path")" ]; then script='s/\r$//'; else script='$!s/\r$//'; fi
      LC_ALL=C sed "$script" "$ARCHETYPE_DIR/$path" > "$CARRY_DIR/lf/$n" || \
        not_verified "could not read every file in the framework's folders."
      printf '%s\n' "$CARRY_DIR/lf/$n" >> "$CARRY_DIR/lf.absolute"
    done < "$CARRY_DIR/unmatched.files"
    hash_list "$CARRY_DIR/lf.absolute" "$CARRY_DIR/unmatched.files" "$CARRY_DIR/lf.pairs" || \
      not_verified "could not read every file in the framework's folders."
    if ! LC_ALL=C comm -23 "$CARRY_DIR/lf.pairs" "$CARRY_DIR/history.pairs" > "$CARRY_DIR/lf.unmatched" || \
       ! cut -f1 "$CARRY_DIR/lf.unmatched" > "$CARRY_DIR/unverified"; then
      not_verified "could not compare the files with the framework's history."
    fi
  fi
  cat "$CARRY_DIR/local.other" >> "$CARRY_DIR/unverified" || \
    not_verified "could not compare the files with the framework's history."
  if [ -s "$CARRY_DIR/unverified" ]; then
    echo "Error: in this layout the update replaces the framework's files and folders at the project root. These files there are not the framework's as it shipped them, so the update would overwrite or delete them:"
    LC_ALL=C sort -u "$CARRY_DIR/unverified" | awk 'NR == FNR { shipped[$0] = 1; next } { print "  " $0 (($0 in shipped) ? " (differs from every version the framework shipped at this path)" : " (the framework never shipped this path)") }' "$CARRY_DIR/history.paths" -
    echo "Move each project file out of the framework folders. For an edited framework file, move the edit into conventions/overrides/, CLAUDE.md.additions, or a file the project owns, then undo the edit (a file inside a framework folder may be deleted instead; the update restores it). Or move this project to the engine-folder layout, where the framework has a folder of its own. Then run the update again. Nothing was changed."
    exit 1
  fi
fi

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

# In a full clone README.md at the project root is the project's own page. One that
# differs from the recorded revision's copy (with none, from the incoming copy) is kept
# beside the replacement; it is not a rule, so nothing goes to CLAUDE.md.additions.
plan_keep_readme() {
  root="$PROJECT_ROOT/README.md"
  [ "$PROJECT_ROOT" = "$ARCHETYPE_DIR" ] && [ -f "$root" ] && [ -f "$TEMP_DIR/README.md" ] || return 0
  cmp -s "$root" "$TEMP_DIR/README.md" && return 0
  base="$CARRY_DIR/README.md.base"
  recorded_file README.md "$base" || cp "$TEMP_DIR/README.md" "$base"
  strip_cr "$root" > "$CARRY_DIR/README.md.lf"
  strip_cr "$base" > "$CARRY_DIR/README.md.base.lf"
  cmp -s "$CARRY_DIR/README.md.lf" "$CARRY_DIR/README.md.base.lf" && return 0
  cp "$root" "$CARRY_DIR/README.md.previous"
}
plan_keep_readme

# In the engine-folder layout the project-root conventions/ folder is the project's own: it
# holds conventions/overrides/. Earlier updates copied the framework's conventions into it,
# where nothing reads them (sessions read the engine's). A file there with a framework
# convention's name is removed when its content matches the engine's copy from before this
# update or the incoming copy. With other content it looks like a project edit: it stays,
# and CLAUDE.md.additions names it once. Every other file, and all of overrides/, stays.
: > "$CARRY_DIR/conventions.remove"
: > "$CARRY_DIR/conventions.kept"
if [ "$PROJECT_ROOT" != "$ARCHETYPE_DIR" ] && [ -d "$PROJECT_ROOT/conventions" ]; then
  for copy in "$PROJECT_ROOT"/conventions/*.md; do
    if [ ! -f "$copy" ] || [ -L "$copy" ]; then continue; fi
    name="$(basename "$copy")"
    if [ ! -f "$ARCHETYPE_DIR/conventions/$name" ] && [ ! -f "$TEMP_DIR/conventions/$name" ]; then continue; fi
    strip_cr "$copy" > "$CARRY_DIR/convention.lf"
    matched=0
    for framework in "$ARCHETYPE_DIR/conventions/$name" "$TEMP_DIR/conventions/$name"; do
      if [ -f "$framework" ]; then
        strip_cr "$framework" > "$CARRY_DIR/framework.lf"
        if cmp -s "$CARRY_DIR/convention.lf" "$CARRY_DIR/framework.lf"; then matched=1; fi
      fi
    done
    if [ "$matched" -eq 1 ]; then
      echo "$name" >> "$CARRY_DIR/conventions.remove"
    elif [ -f "$ADD" ] && strip_cr "$ADD" | grep -qxF -e "- conventions/$name"; then
      :  # already named in CLAUDE.md.additions by an earlier update
    else
      echo "$name" >> "$CARRY_DIR/conventions.kept"
    fi
  done
fi

# In the engine-folder layout, records older installs kept inside the engine move to the
# project root. An engine copy is removed only when the project root already holds the same
# text (carriage returns ignored); otherwise its text is kept at the project root first: a
# different engine VERSION-LOG.md is added to the project's log under a dated heading, and
# FRAMEWORK-SOURCE.md is kept as a dated .pre-update copy.
same_text() {
  strip_cr "$1" > "$CARRY_DIR/same.a" && strip_cr "$2" > "$CARRY_DIR/same.b" && cmp -s "$CARRY_DIR/same.a" "$CARRY_DIR/same.b"
}
LEGACY_LOG=""
LEGACY_SOURCE=""
if [ "$PROJECT_ROOT" != "$ARCHETYPE_DIR" ]; then
  if [ -f "$ARCHETYPE_DIR/VERSION-LOG.md" ]; then
    if [ ! -f "$PROJECT_ROOT/VERSION-LOG.md" ]; then
      LEGACY_LOG=move
    elif same_text "$ARCHETYPE_DIR/VERSION-LOG.md" "$PROJECT_ROOT/VERSION-LOG.md"; then
      LEGACY_LOG=duplicate
    else
      LEGACY_LOG=append
      if ! {
        echo ""
        echo "## Kept from ${ENGINE_REL}VERSION-LOG.md by the framework update of $(date +%Y-%m-%d)"
        echo ""
        echo "The engine folder held a version log of its own that differed from this one. Its text follows, each line indented four spaces so its entries are not read as this log's."
        echo ""
        LC_ALL=C sed 's/^/    /' "$ARCHETYPE_DIR/VERSION-LOG.md"
      } > "$CARRY_DIR/version-log.block"; then
        not_verified "could not read ${ENGINE_REL}VERSION-LOG.md."
      fi
    fi
  fi
  if [ -f "$ARCHETYPE_DIR/FRAMEWORK-SOURCE.md" ]; then
    LEGACY_SOURCE=keep
    for other in "$PROJECT_ROOT/FRAMEWORK-SOURCE.md" "$PROJECT_ROOT"/FRAMEWORK-SOURCE.md.pre-update-*; do
      if [ -f "$other" ] && same_text "$ARCHETYPE_DIR/FRAMEWORK-SOURCE.md" "$other"; then LEGACY_SOURCE=duplicate; fi
    done
    if [ "$LEGACY_SOURCE" = keep ] && ! cp "$ARCHETYPE_DIR/FRAMEWORK-SOURCE.md" "$CARRY_DIR/FRAMEWORK-SOURCE.md.previous"; then
      not_verified "could not read ${ENGINE_REL}FRAMEWORK-SOURCE.md."
    fi
  fi
fi

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
        echo "  CHANGED: ${ENGINE_REL}$file"
        CHANGES=$((CHANGES + 1))
      fi
    else
      echo "  NEW: ${ENGINE_REL}$file"
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
    echo "  CHANGED: ${ENGINE_REL}update.sh (self-replace at end)"
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
          echo "  CHANGED: ${ENGINE_REL}$rel_path"
        fi
      else
        echo "  NEW: ${ENGINE_REL}$rel_path"
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
if [ -f "$CARRY_DIR/README.md.previous" ]; then
  CARRY_SHOWN=1
  echo "  KEPT: README.md is this project's own version; it is kept as a dated README.md.pre-update copy beside the framework's (a README is not a rule, so nothing goes to CLAUDE.md.additions)"
fi
if [ -s "$CARRY_DIR/conventions.remove" ]; then
  CARRY_SHOWN=1
  echo "  REMOVE: $(wc -l < "$CARRY_DIR/conventions.remove" | tr -d ' ') unchanged copies of framework conventions from conventions/ at the project root; ${ENGINE_REL}conventions/ holds the framework's conventions, and overrides/ and every other file there stay"
fi
while IFS= read -r name; do
  CARRY_SHOWN=1
  echo "  KEPT: conventions/$name at the project root has a framework convention's name but other content, so it looks like a project edit; it stays and is named in CLAUDE.md.additions (it belongs in conventions/overrides/)"
done < "$CARRY_DIR/conventions.kept"
case "$LEGACY_LOG" in
  move) CARRY_SHOWN=1; echo "  MOVE: ${ENGINE_REL}VERSION-LOG.md goes to the project root, where the version log lives" ;;
  duplicate) CARRY_SHOWN=1; echo "  REMOVE: ${ENGINE_REL}VERSION-LOG.md (the project's VERSION-LOG.md holds the same text)" ;;
  append) CARRY_SHOWN=1; echo "  KEPT: ${ENGINE_REL}VERSION-LOG.md differs from the project's VERSION-LOG.md; its text is added there under a dated heading, then it leaves the engine" ;;
esac
case "$LEGACY_SOURCE" in
  duplicate) CARRY_SHOWN=1; echo "  REMOVE: ${ENGINE_REL}FRAMEWORK-SOURCE.md (a copy at the project root holds the same text)" ;;
  keep) CARRY_SHOWN=1; echo "  KEPT: ${ENGINE_REL}FRAMEWORK-SOURCE.md is kept as a dated FRAMEWORK-SOURCE.md.pre-update copy at the project root, then it leaves the engine" ;;
esac
[ "$CARRY_SHOWN" -eq 1 ] && echo ""

# Files that are NEVER touched (project-specific)
echo "--- Project-specific files (will NOT be touched) ---"
for skip in References.md feature-tree.md INDEX.md MIGRATION-NOTES.md CLAUDE.md.additions; do
  if [ -f "$ARCHETYPE_DIR/$skip" ]; then
    echo "  SAFE: ${ENGINE_REL}$skip"
    SKIPPED=$((SKIPPED + 1))
  fi
done
for skip_dir in conventions/overrides protocols catalogs todo docs; do
  if [ -d "$ARCHETYPE_DIR/$skip_dir" ]; then
    echo "  SAFE: ${ENGINE_REL}$skip_dir/ (entire directory)"
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
if [ -f "$CARRY_DIR/README.md.previous" ]; then
  kept="$(kept_path README.md)"
  if ! cp "$CARRY_DIR/README.md.previous" "$kept"; then
    echo "Error: could not keep the previous README.md. Nothing was replaced."
    exit 1
  fi
  echo "  kept: README.md as $(basename "$kept")"
fi
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
if [ -s "$CARRY_DIR/conventions.kept" ]; then
  {
    if [ -s "$ADD" ]; then
      [ -n "$(tail -c 1 "$ADD")" ] && echo ""
      echo ""
    fi
    echo "## Framework conventions edited in the project-root conventions/ folder, found by the framework update of $(date +%Y-%m-%d): move them to conventions/overrides/"
    echo ""
    echo "Each file below has a framework convention's name but other content, so it looks like this project's edit of that convention. Sessions read the framework's conventions from ${ENGINE_REL}conventions/, not from this folder, so the edit has no effect where it is. Move what this project still needs into conventions/overrides/ with the reason, then delete the file. Remove this heading when done."
    echo ""
    sed 's|^|- conventions/|' "$CARRY_DIR/conventions.kept"
  } > "$CARRY_DIR/conventions.block"
  if ! cat "$CARRY_DIR/conventions.block" >> "$ADD"; then
    echo "Error: could not write CLAUDE.md.additions. Nothing was replaced."
    exit 1
  fi
  echo "  named: $(wc -l < "$CARRY_DIR/conventions.kept" | tr -d ' ') edited framework convention(s) in conventions/ at the project root → CLAUDE.md.additions"
fi
case "$LEGACY_LOG" in
  move)
    if ! mv "$ARCHETYPE_DIR/VERSION-LOG.md" "$PROJECT_ROOT/VERSION-LOG.md"; then
      echo "Error: could not move ${ENGINE_REL}VERSION-LOG.md to the project root. Nothing was replaced."
      exit 1
    fi
    echo "  moved: ${ENGINE_REL}VERSION-LOG.md → project root" ;;
  duplicate)
    rm -f "$ARCHETYPE_DIR/VERSION-LOG.md"
    echo "  removed: ${ENGINE_REL}VERSION-LOG.md (the same text as the project's)" ;;
  append)
    if ! cat "$CARRY_DIR/version-log.block" >> "$PROJECT_ROOT/VERSION-LOG.md"; then
      echo "Error: could not add ${ENGINE_REL}VERSION-LOG.md to the project's VERSION-LOG.md. Nothing was replaced."
      exit 1
    fi
    rm -f "$ARCHETYPE_DIR/VERSION-LOG.md"
    echo "  kept: ${ENGINE_REL}VERSION-LOG.md in the project's VERSION-LOG.md, under a dated heading" ;;
esac
case "$LEGACY_SOURCE" in
  duplicate)
    rm -f "$ARCHETYPE_DIR/FRAMEWORK-SOURCE.md"
    echo "  removed: ${ENGINE_REL}FRAMEWORK-SOURCE.md (the same text is at the project root)" ;;
  keep)
    kept="$(kept_path FRAMEWORK-SOURCE.md)"
    if ! cp "$CARRY_DIR/FRAMEWORK-SOURCE.md.previous" "$kept"; then
      echo "Error: could not keep ${ENGINE_REL}FRAMEWORK-SOURCE.md at the project root. Nothing was replaced."
      exit 1
    fi
    rm -f "$ARCHETYPE_DIR/FRAMEWORK-SOURCE.md"
    echo "  kept: ${ENGINE_REL}FRAMEWORK-SOURCE.md as $(basename "$kept") at the project root" ;;
esac

# Step 4: Apply updates
echo ""
echo "Applying updates..."

# Update universal files in the engine
for file in $UNIVERSAL_FILES; do
  if [ -f "$TEMP_DIR/$file" ]; then
    cp "$TEMP_DIR/$file" "$ARCHETYPE_DIR/$file"
    echo "  updated: ${ENGINE_REL}$file"
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
      echo "  updated: ${ENGINE_REL}conventions/ (overrides preserved)"
    else
      rm -rf "$ARCHETYPE_DIR/$dir"
      cp -R "$TEMP_DIR/$dir" "$ARCHETYPE_DIR/$dir"
      echo "  updated: ${ENGINE_REL}$dir/"
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

# Step 6: Remove the framework convention copies that earlier updates put in the
# project-root conventions/ folder, as planned before the prompt. The framework's
# conventions are never copied there, and nothing else there is touched.
if [ -s "$CARRY_DIR/conventions.remove" ]; then
  while IFS= read -r name; do
    if [ -f "$PROJECT_ROOT/conventions/$name" ] && [ ! -L "$PROJECT_ROOT/conventions/$name" ]; then
      rm -f "$PROJECT_ROOT/conventions/$name"
    fi
  done < "$CARRY_DIR/conventions.remove"
  echo "  removed: $(wc -l < "$CARRY_DIR/conventions.remove" | tr -d ' ') framework convention copies from conventions/ (project root)"
fi

# Step 7: Remove the empty docs folders older installs left inside the engine (their
# VERSION-LOG.md and FRAMEWORK-SOURCE.md were handled with the project's words in step 3b).
# Keeps the framework folder read-only. Safe to run repeatedly.
if [ "$ARCHETYPE_DIR" != "$PROJECT_ROOT" ]; then
  if [ -d "$ARCHETYPE_DIR/docs" ]; then
    rmdir "$ARCHETYPE_DIR/docs/systems" "$ARCHETYPE_DIR/docs/features" "$ARCHETYPE_DIR/docs" 2>/dev/null && \
      echo "  removed: ${ENGINE_REL}docs/ (empty; project docs live at project root)"
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
    echo "  updated: ${ENGINE_REL}update.sh (self, atomic replace)"
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
echo "Next: follow ${ENGINE_REL}development/UPDATE.md, section After (audit what the update added to CLAUDE.md.additions, run the checks, commit as one change)."
