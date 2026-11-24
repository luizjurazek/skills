#!/usr/bin/env bash
# Per-skill dependency installer, called by the repository's root install.sh.
set -euo pipefail
bash "$(dirname "$0")/scripts/ensure-plugin.sh"
