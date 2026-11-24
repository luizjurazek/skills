#!/usr/bin/env bash
# Creates a private virtualenv for the plugin's AI generation scripts (Gemini) and prints its python.
# A venv avoids touching the system Python (PEP 668 blocks global pip installs on most distros).
# Output contract (last line, on success): PY=<absolute path to the venv's python>
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
VENV="$SKILL_DIR/.venv"

if [[ ! -x "$VENV/bin/python" ]]; then
  python3 -m venv "$VENV"
fi

if ! "$VENV/bin/python" -c "import google.genai, PIL" >/dev/null 2>&1; then
  "$VENV/bin/python" -m pip install --quiet --upgrade pip
  "$VENV/bin/python" -m pip install --quiet google-genai pillow
fi

if [[ -z "${GEMINI_API_KEY:-}" ]] && ! grep -qs '^GEMINI_API_KEY=.\+' "$SKILL_DIR/.env"; then
  echo "WARN: GEMINI_API_KEY not set (env or $SKILL_DIR/.env); AI generation will fail until it is." >&2
fi

echo "PY=$VENV/bin/python"
