#!/usr/bin/env bash
# Installs playwright-core next to this script (once) and checks that a Chrome/Chromium is available.
# Prints CHROME=<path> on success. playwright-core never downloads browsers: it drives the system one.
set -euo pipefail
dir="$(cd "$(dirname "$0")" && pwd)"
if [ ! -d "$dir/node_modules/playwright-core" ]; then
  (cd "$dir" && npm install --silent --no-audit --no-fund >/dev/null)
fi
chrome="${CHROME_PATH:-}"
if [ -z "$chrome" ]; then
  for c in google-chrome google-chrome-stable chromium chromium-browser \
           "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; do
    if command -v "$c" >/dev/null 2>&1 || [ -x "$c" ]; then chrome="$(command -v "$c" || echo "$c")"; break; fi
  done
fi
if [ -z "$chrome" ]; then
  chrome="$(ls -d "$HOME"/.cache/ms-playwright/chromium-*/chrome-linux*/chrome 2>/dev/null | tail -1 || true)"
fi
if [ -z "$chrome" ]; then
  echo "error: no Chrome/Chromium found; set CHROME_PATH" >&2
  exit 1
fi
echo "CHROME=$chrome"
