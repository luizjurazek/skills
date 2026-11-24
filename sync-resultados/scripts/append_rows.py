#!/usr/bin/env python3
"""Append result rows to the Google Sheet without touching existing rows.

Input: a JSON file (or stdin with "-") containing a list of objects whose keys
match the sheet's header names (Empresa, Projeto, ...). Unknown keys are
rejected; missing keys are left blank.

Rows whose (Empresa, Projeto) pair already exists are skipped, so the script is
safe to run twice. Use --dry-run to preview without writing.
"""
import argparse
import json
import os
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
KEY_COLUMNS = ("Empresa", "Projeto")


def load_env(path: Path) -> None:
    """Minimal .env loader; real environment variables take precedence."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def norm(value) -> str:
    return " ".join(str(value or "").split()).casefold()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", help="JSON file with a list of rows, or - for stdin")
    parser.add_argument("--dry-run", action="store_true", help="show what would be written")
    args = parser.parse_args()

    load_env(SKILL_DIR / ".env")

    raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
    rows = json.loads(raw)
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        sys.exit("Input must be a JSON list of objects.")

    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    sheet_name = os.environ.get("SHEET_NAME", "Resultados")
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "credentials/service-account.json")
    creds_path = Path(creds) if os.path.isabs(creds) else SKILL_DIR / creds
    if not spreadsheet_id:
        sys.exit("SPREADSHEET_ID is not set (see .env.example).")
    if not creds_path.exists():
        sys.exit(f"Service account key not found: {creds_path}")

    import gspread  # imported late so --help works without the dependency

    client = gspread.service_account(filename=str(creds_path))
    ws = client.open_by_key(spreadsheet_id).worksheet(sheet_name)

    values = ws.get_all_values()
    if not values:
        sys.exit("The sheet is empty; expected a header row.")
    header = values[0]
    named = {h.strip() for h in header if h.strip()}

    missing = [c for c in KEY_COLUMNS if c not in named]
    if missing:
        sys.exit(f"Header is missing required columns: {missing}")

    idx = {h.strip(): i for i, h in enumerate(header) if h.strip()}
    existing = {
        tuple(norm(r[idx[c]]) if idx[c] < len(r) else "" for c in KEY_COLUMNS)
        for r in values[1:]
    }

    to_write, skipped = [], []
    for row in rows:
        unknown = set(row) - named
        if unknown:
            sys.exit(f"Unknown columns in input: {sorted(unknown)}. Sheet has: {sorted(named)}")
        key = tuple(norm(row.get(c)) for c in KEY_COLUMNS)
        if key in existing:
            skipped.append(row)
            continue
        existing.add(key)
        line = [""] * len(header)
        for col, i in idx.items():
            v = row.get(col)
            line[i] = "" if v is None else v
        to_write.append(line)

    for row in skipped:
        print(f"SKIP (already in sheet): {row.get('Empresa')} / {row.get('Projeto')}")
    next_row = len(values) + 1
    for n, line in enumerate(to_write):
        # "row" is the sheet row the line lands on, so callers can record it.
        print(f"{'WOULD ADD' if args.dry_run else 'ADD'} (row {next_row + n}): "
              f"{line[idx['Empresa']]} / {line[idx['Projeto']]}")

    if to_write and not args.dry_run:
        # Write to an explicit range right after the last non-empty row. The
        # API's append auto-detection fails when column A is empty and then
        # overwrites row 1 (the header), so it is deliberately not used.
        # RAW keeps text literal, so a value starting with "=" is never a formula.
        first_row = len(values) + 1
        last_row = first_row + len(to_write) - 1
        if last_row > ws.row_count:
            ws.add_rows(last_row - ws.row_count)
        end_col = gspread.utils.rowcol_to_a1(1, len(header)).rstrip("1")
        ws.update(
            values=to_write,
            range_name=f"A{first_row}:{end_col}{last_row}",
            value_input_option="RAW",
        )
    print(f"Done: {len(to_write)} added, {len(skipped)} skipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
