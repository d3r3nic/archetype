#!/bin/bash
# Retired: this was a turn-end reminder (a checklist written to stderr, exit 0). The host does not
# give the agent the stderr of a hook that exits 0, so the reminder reached no one, and the
# completion rule in AGENTS.md already carries it. The settings templates no longer register it.
#
# It stays so that settings which still name it do not fail on every turn: it reads the event
# and exits 0 without output. scripts/check-hooks.py reports a registration that names it;
# remove that registration.

cat > /dev/null
exit 0
