#!/usr/bin/env bash
# Installs skills from this repository into ~/.claude/skills (symlinks, so edits here apply everywhere)
# and runs each skill's own install.sh for external dependencies (plugins, CLIs).
#
# Usage:
#   ./install.sh                 # every skill folder that has a SKILL.md
#   ./install.sh ui-prototype    # only the named skills
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$TARGET_DIR"

if [[ $# -gt 0 ]]; then
  skills=("$@")
else
  skills=()
  for dir in "$REPO_DIR"/*/; do
    [[ -f "$dir/SKILL.md" ]] && skills+=("$(basename "$dir")")
  done
fi

status=0
for name in "${skills[@]}"; do
  src="$REPO_DIR/$name"
  dest="$TARGET_DIR/$name"

  if [[ ! -f "$src/SKILL.md" ]]; then
    echo "✗ $name: no SKILL.md in $src" >&2
    status=1
    continue
  fi

  if [[ -L "$dest" ]]; then
    current="$(readlink -f "$dest")"
    if [[ "$current" == "$(readlink -f "$src")" ]]; then
      echo "✓ $name: already linked"
    else
      # Never overwrite a link to another copy of the skill; the user decides which one wins.
      echo "! $name: $dest points to $current — skipped (remove it to use this repo's version)" >&2
      continue
    fi
  elif [[ -e "$dest" ]]; then
    echo "! $name: $dest exists and is not a symlink — skipped" >&2
    continue
  else
    ln -s "$src" "$dest"
    echo "+ $name: linked $dest -> $src"
  fi

  if [[ -x "$src/install.sh" || -f "$src/install.sh" ]]; then
    echo "  running $name/install.sh"
    bash "$src/install.sh" || { echo "✗ $name: install.sh failed" >&2; status=1; }
  fi
done

exit $status
