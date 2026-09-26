#!/bin/bash
# Archetype hook: PreToolUse (Bash matcher)
# Blocks destructive shell commands by matching the proposed command against
# known-dangerous patterns. Exits 2 to block with an explanation visible to Claude.
#
# Claude Code contract (2026):
#   - Event JSON arrives on stdin
#   - Exit 0: allow silently
#   - Exit 2: block the tool call; stderr is passed back to Claude as context
#   - Other non-zero: advisory warning, does not block

# Text is read as bytes, the same on every system: in a UTF-8 locale the macOS awk exits on a
# character that substr cut in two, and the macOS grep, sed and tr fail on bytes that are not UTF-8.
export LC_ALL=C

INPUT=$(cat)

NL='
'
# Parse the tool name and command with a JSON reader: jq, else python3. When neither reads it
# (neither is installed, or one fails), sed does, and it stops at the first escaped quote or
# newline inside the command.
READER=""
if command -v jq >/dev/null 2>&1 && TOOL=$(printf '%s' "$INPUT" | jq -r '.tool_name // ""' 2>/dev/null) \
   && COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null); then
  READER="jq"
fi
if [ -z "$READER" ] && command -v python3 >/dev/null 2>&1 && PARSED=$(printf '%s' "$INPUT" | python3 -c 'import json, sys
d = json.load(sys.stdin)
i = d.get("tool_input") if isinstance(d, dict) else None
c = i.get("command") if isinstance(i, dict) else None
sys.stdout.write(str(d.get("tool_name") or "") + "\n" + (c if isinstance(c, str) else ""))' 2>/dev/null); then
  READER="python3"
  TOOL="${PARSED%%"$NL"*}"
  COMMAND=""; case "$PARSED" in *"$NL"*) COMMAND="${PARSED#*"$NL"}" ;; esac
fi
if [ -z "$READER" ]; then
  TOOL=$(printf '%s' "$INPUT" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
  COMMAND=$(printf '%s' "$INPUT" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
fi

# Only inspect Bash tool calls
[ "$TOOL" = "Bash" ] || exit 0
[ -n "$COMMAND" ] || exit 0

# A line the shell continues with a trailing backslash is read as one line. Other lines stay apart:
# each is matched on its own, as the shell runs it.
MATCHED="${COMMAND//\\$NL/ }"

# A git push, with git's own options before the word push: a short flag (-P), a long one
# (--no-pager, --git-dir=x), or one that takes a separate value (-C, -c, --git-dir, --work-tree,
# --namespace, --config-env, --exec-path, --super-prefix, --attr-source). A value is a run of
# parts, each bare with backslash escapes (work\ dir), in double or single quotes (either quote
# inside the other), or a command substitution without nested parentheses: ~/"My Project",
# $(...)/app. The push's own arguments before the flag may hold the same quoted text and
# substitutions, a separator inside them included. A flag ends where no letter, digit or hyphen follows: a space, a
# quote, a closing parenthesis, a backtick, a redirection or the end of the line.
QUOTE='['"'"'"]'
QUOTED='("[^"]*"|'"'[^']*'"')'
SUBST='\$\([^)]*\)|`[^`]*`'
NOT_SEPARATOR_OR_QUOTE='[^;&|'"'"'"]'
VALUE="($QUOTED|$SUBST|"'[^[:space:]\\]|\\.)+'
GIT_OPTION="[[:space:]]+((-C|-c|--git-dir|--work-tree|--namespace|--config-env|--exec-path|--super-prefix|--attr-source)[[:space:]]+$VALUE|--[a-z][a-z-]*(=$VALUE)?|-[A-Za-z]+)"
GIT_PUSH="(^|[^[:alnum:]_-])git($GIT_OPTION)*[[:space:]]+push[[:space:]](($NOT_SEPARATOR_OR_QUOTE|$QUOTED|$SUBST)*[[:space:]])?$QUOTE?"
FLAG_END='([^-[:alnum:]]|$)'

# Destructive patterns. Order matters — most specific first.
PATTERNS=(
  'rm[[:space:]]+-[rRfd]*[rR][rRfd]*f[rRfd]*[[:space:]]+/($|[^a-zA-Z])'
  'rm[[:space:]]+-[rRfd]*[rR][rRfd]*f[rRfd]*[[:space:]]+~'
  'rm[[:space:]]+-[rRfd]*[rR][rRfd]*f[rRfd]*[[:space:]]+\*'
  'rm[[:space:]]+-[rRfd]*[rR][rRfd]*f[rRfd]*[[:space:]]+\.\*'
  'git[[:space:]]+reset[[:space:]]+--hard'
  # A push that overwrites remote history: --force, --mirror or any abbreviation git takes for it
  # (--m to --mirro), -f alone or with other short options (-uf, -f4), or a refspec that opens with +.
  # --force-with-lease, which refuses when the remote moved since the last fetch, is the safer
  # form and is not matched.
  "$GIT_PUSH--(force|m(i(r(r(o(r)?)?)?)?)?)$FLAG_END"
  "$GIT_PUSH-[[:alnum:]]*f[[:alnum:]]*$FLAG_END"
  "$GIT_PUSH[+][^[:space:]]"
  'git[[:space:]]+clean[[:space:]]+-[fdx]+'
  'git[[:space:]]+branch[[:space:]]+-D'
  'git[[:space:]]+checkout[[:space:]]+--[[:space:]]+\.'
  'DROP[[:space:]]+TABLE'
  'DROP[[:space:]]+DATABASE'
  'DROP[[:space:]]+SCHEMA'
  'TRUNCATE[[:space:]]+TABLE'
  'DELETE[[:space:]]+FROM[[:space:]]+[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*;'
  'chmod[[:space:]]+-R[[:space:]]+777'
  'dd[[:space:]]+if='
  'mkfs\.'
  '>[[:space:]]*/dev/sd[a-z]'
  ':[[:space:]]*\(\)[[:space:]]*\{[[:space:]]*:[[:space:]]*\|'
)

for pattern in "${PATTERNS[@]}"; do
  if printf '%s' "$MATCHED" | grep -qE "$pattern"; then
    {
      echo "archetype hook blocked destructive command."
      echo "Pattern matched: $pattern"
      echo "Command: $COMMAND"
      echo ""
      echo "Do not reword the command to get past this guard. Use a safer form, or ask the owner"
      echo "to run the command when it is truly needed (it is irreversible, and theirs to decide):"
      echo "  - rm -rf X          → move it to the trash, or name a narrower path"
      echo "  - git reset --hard  → git stash, or a new branch from HEAD"
      echo "  - git push --force  → git push --force-with-lease, on a branch only you push to"
      echo "  - DROP / TRUNCATE   → a reversible migration or a soft delete"
    } >&2
    exit 2
  fi
done

exit 0
