#!/usr/bin/env bash
# Ensures the ui-ux-pro-max plugin is installed and prints where its pieces live.
# Output contract (last lines, on success):
#   PLUGIN_SKILLS=<dir holding the plugin's sub-skills: ui-ux-pro-max, design, brand, ...>
#   SEARCH=<absolute path to ui-ux-pro-max's search.py>
set -euo pipefail

MARKETPLACE_REPO="nextlevelbuilder/ui-ux-pro-max-skill"
PLUGIN_ID="ui-ux-pro-max@ui-ux-pro-max-skill"
CACHE_GLOB="$HOME/.claude/plugins/cache/ui-ux-pro-max-skill/ui-ux-pro-max/*/.claude/skills"

find_skills_dir() {
  # Newest installed version wins.
  ls -1d $CACHE_GLOB 2>/dev/null | sort -V | tail -n 1
}

skills_dir="$(find_skills_dir || true)"

if [[ -z "$skills_dir" ]]; then
  if ! command -v claude >/dev/null 2>&1; then
    echo "ERROR: 'claude' CLI not found; install the plugin manually:" >&2
    echo "  /plugin marketplace add $MARKETPLACE_REPO" >&2
    echo "  /plugin install $PLUGIN_ID" >&2
    exit 1
  fi
  echo "Installing $PLUGIN_ID ..."
  claude plugin marketplace list 2>/dev/null | grep -q "ui-ux-pro-max-skill" \
    || claude plugin marketplace add "$MARKETPLACE_REPO"
  claude plugin install "$PLUGIN_ID"
  echo "INSTALLED: run /reload-plugins to activate the ui-ux-pro-max sub-skills in the current session."
  skills_dir="$(find_skills_dir || true)"
fi

search_path="$skills_dir/ui-ux-pro-max/scripts/search.py"
if [[ -z "$skills_dir" || ! -f "$search_path" ]]; then
  echo "ERROR: plugin installed but its skills were not found under $CACHE_GLOB" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required by the plugin's scripts." >&2
  exit 1
fi

echo "PLUGIN_SKILLS=$skills_dir"
echo "SEARCH=$search_path"
