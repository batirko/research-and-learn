#!/bin/sh
# The guard: run the private-term scan and the secret scan.
# The hooks in this folder call it. Turn them on once per clone:
#
#     git config core.hooksPath .githooks
#
# It reads the private-term list from outside the repository: the PRIVATE_TERMS
# variable, then `git config guard.terms`, then the default path below.
# It fails when the list is missing, so a commit can't skip the scan by accident.

terms="${PRIVATE_TERMS:-$(git config --get guard.terms)}"
[ -n "$terms" ] || terms="$HOME/.config/research-and-learn/private-terms.txt"
case "$terms" in "~"/*) terms="$HOME/${terms#\~/}" ;; esac

if [ ! -f "$terms" ]; then
  echo "guard: the private-term list is missing at $terms." >&2
  echo "guard: set it with \`git config guard.terms <file>\`. The commit stops until the list exists." >&2
  exit 1
fi

# The scan runs on Python 3.9 or later. Prefer a newer one when it exists.
for py in python3.13 python3.12 python3.11 python3; do
  if command -v "$py" >/dev/null 2>&1; then
    exec "$py" "$(git rev-parse --show-toplevel)/tools/scan.py" "$@" --terms "$terms" --secrets
  fi
done
echo "guard: no python3 found, so the scan can't run." >&2
exit 1
