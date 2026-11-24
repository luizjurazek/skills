#!/usr/bin/env bash
# Per-skill dependency installer, called by the repository's root install.sh.
set -euo pipefail
bash "$(dirname "$0")/scripts/ensure-plugin.sh"
# Screenshot helper (PNG per screen). Optional: skip quietly when Node or Chrome are missing.
if command -v npm >/dev/null 2>&1; then
  bash "$(dirname "$0")/scripts/ensure-screenshot.sh" || echo "warn: PNG export unavailable (no Chrome found)" >&2
fi
