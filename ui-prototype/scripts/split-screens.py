#!/usr/bin/env python3
"""Split a grouped ui-prototype HTML into one standalone file per screen.

Usage:
    python3 split-screens.py <grouped.html> [out_dir]

Each top-level <section class="spec" id="..."> inside <main> becomes <out_dir>/<name>.html, where
<name> is "<data-task>-<id>" when the section has data-task="NN", else just "<id>". Everything
outside <main> (head, styles, SVG sprite, templates, theme switcher, scripts) is copied as is, so
each file opens on its own. Scripts must therefore skip work when their section is absent.

The grouped file stays the source of truth: re-run this after every edit. Files in out_dir that no
longer match a section are removed. Prints one line per written file.
"""
import html
import pathlib
import re
import sys


def section_title(section: str, fallback: str) -> str:
    m = re.search(r"<h2[^>]*>(.*?)</h2>", section, re.S)
    if not m:
        return fallback
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() or fallback


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    src = pathlib.Path(sys.argv[1]).resolve()
    out_dir = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.with_suffix("")
    doc = src.read_text(encoding="utf-8")

    main_open = re.search(r"<main\b[^>]*>", doc)
    main_close = doc.rfind("</main>")
    if not main_open or main_close == -1:
        print("error: no <main> element found", file=sys.stderr)
        return 1
    before, inner, after = doc[: main_open.end()], doc[main_open.end() : main_close], doc[main_close:]

    sections = list(re.finditer(r'<section\b(?=[^>]*\bclass="spec")[^>]*\bid="([^"]+)"[^>]*>.*?</section>', inner, re.S))
    if not sections:
        print('error: no <section class="spec" id="..."> found inside <main>', file=sys.stderr)
        return 1

    page_title = re.search(r"<title>(.*?)</title>", doc, re.S)
    base_title = html.unescape(page_title.group(1)).strip() if page_title else src.stem
    eyebrow = re.search(r'<span class="eyebrow">(.*?)</span>', inner, re.S)
    eyebrow_text = eyebrow.group(1).strip() if eyebrow else html.escape(base_title)

    out_dir.mkdir(parents=True, exist_ok=True)
    rel_back = pathlib.Path("..") / src.name
    written = set()
    for m in sections:
        section, sec_id = m.group(0), m.group(1)
        task = re.search(r'\bdata-task="([^"]+)"', section[: section.index(">")])
        name = f"{task.group(1)}-{sec_id}" if task else sec_id
        title = section_title(section, sec_id)
        header = (
            '\n  <header class="intro">\n'
            f'    <span class="eyebrow">{eyebrow_text}</span>\n'
            f'    <p><a href="{rel_back.as_posix()}#{sec_id}">← Todas as telas</a></p>\n'
            "  </header>\n\n  "
        )
        page = before + header + section + "\n" + after
        page = re.sub(
            r"<title>.*?</title>",
            lambda _: f"<title>{html.escape(base_title)} · {html.escape(title)}</title>",
            page,
            count=1,
            flags=re.S,
        )
        target = out_dir / f"{name}.html"
        target.write_text(page, encoding="utf-8")
        written.add(target.name)
        print(target)

    # Drop files from sections that were renamed or removed, so links never point at stale screens.
    for old in out_dir.glob("*.html"):
        if old.name not in written:
            old.unlink()
            print(f"removed {old}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
