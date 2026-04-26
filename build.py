#!/usr/bin/env python3
"""Generate a static HTML page from the categories/*.md content.

Parses each entry (### Name + bulleted fields) and renders an accessible
single-page site to docs/index.html. CSS is at docs/style.css (hand-edited).

Usage:
    python build.py
"""

import html
import os
import re
from datetime import date

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
CATEGORIES_DIR = os.path.join(REPO_ROOT, "categories")
DOCS_DIR = os.path.join(REPO_ROOT, "docs")

CATEGORY_ORDER = [
    ("research-opportunities", "Research Opportunities"),
    ("ai-informatics-fellowships", "AI / Informatics Fellowships"),
    ("conferences", "Conferences"),
    ("awards-grants", "Awards & Grants"),
    ("educational-courses", "Educational Courses"),
]

FIELD_ORDER = ["Sponsor", "Eligibility", "Deadline", "Recurrence", "Link", "Description", "Notes"]

ENTRY_FIELD_RE = re.compile(r"^\s*-\s*\*\*(?P<key>[^*]+):\*\*\s*(?P<value>.+?)\s*$", re.MULTILINE)
URL_RE = re.compile(r"https?://\S+")


def slugify(text):
    s = re.sub(r"[^\w\s-]", "", text.lower())
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s


def parse_category(path):
    """Return (intro_text, [entry_dict, ...]) for a category file."""
    with open(path, encoding="utf-8") as f:
        text = f.read()

    # Split by horizontal rules; first chunk is preamble (title + intro).
    chunks = re.split(r"\n---\n", text)
    preamble = chunks[0]
    entry_chunks = chunks[1:]

    # Find the first non-empty, non-heading, non-blockquote paragraph after the H1.
    intro = ""
    in_intro = False
    intro_lines = []
    for line in preamble.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            in_intro = True
            continue
        if not in_intro:
            continue
        if stripped.startswith(">") or stripped.startswith("---"):
            if intro_lines:
                break
            continue
        if not stripped:
            if intro_lines:
                break
            continue
        intro_lines.append(stripped)
    intro = " ".join(intro_lines)

    entries = []
    for chunk in entry_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        name_match = re.search(r"^###\s+(.+?)$", chunk, re.MULTILINE)
        if not name_match:
            continue
        name = name_match.group(1).strip()

        fields = {}
        for fm in ENTRY_FIELD_RE.finditer(chunk):
            fields[fm.group("key").strip()] = fm.group("value").strip()

        if name and fields:
            entries.append({"name": name, "fields": fields})

    return intro, entries


def linkify(value):
    """Wrap any URL in the value with an <a> tag (escapes everything else)."""
    parts = []
    last = 0
    for m in URL_RE.finditer(value):
        if m.start() > last:
            parts.append(html.escape(value[last:m.start()]))
        url = m.group(0).rstrip(".,;:)")
        trailing = m.group(0)[len(url):]
        parts.append(
            f'<a href="{html.escape(url)}" rel="noopener noreferrer" '
            f'target="_blank" aria-label="{html.escape(url)} (opens in new tab)">'
            f'{html.escape(url)}</a>'
        )
        if trailing:
            parts.append(html.escape(trailing))
        last = m.end()
    if last < len(value):
        parts.append(html.escape(value[last:]))
    return "".join(parts)


def render_entry(entry, category_slug):
    name = entry["name"]
    entry_id = f"{category_slug}--{slugify(name)}"
    field_rows = []
    for key in FIELD_ORDER:
        if key in entry["fields"]:
            value_html = linkify(entry["fields"][key])
            field_rows.append(
                f'      <div class="field"><dt>{html.escape(key)}</dt>'
                f'<dd>{value_html}</dd></div>'
            )
    fields_html = "\n".join(field_rows)
    return f"""    <article class="entry" id="{html.escape(entry_id)}" aria-labelledby="{html.escape(entry_id)}-title">
      <h3 id="{html.escape(entry_id)}-title">{html.escape(name)}</h3>
      <dl class="fields">
{fields_html}
      </dl>
    </article>"""


def render_category(slug, title, intro, entries):
    section_id = f"category-{slug}"
    entries_html = "\n".join(render_entry(e, slug) for e in entries)
    intro_html = f'    <p class="category-intro">{html.escape(intro)}</p>\n' if intro else ""
    count = len(entries)
    return f"""  <section class="category" id="{section_id}" aria-labelledby="{section_id}-title">
    <h2 id="{section_id}-title">{html.escape(title)} <span class="count" aria-label="{count} entries">({count})</span></h2>
{intro_html}{entries_html}
  </section>"""


def render_toc(categories):
    items = []
    for slug, title, count in categories:
        items.append(
            f'      <li><a href="#category-{slug}">{html.escape(title)} '
            f'<span class="count">({count})</span></a></li>'
        )
    return "\n".join(items)


def render_page(categories_data):
    """categories_data: list of (slug, title, intro, entries) tuples."""
    today = date.today().isoformat()
    toc_categories = [(slug, title, len(entries)) for slug, title, _, entries in categories_data]
    toc = render_toc(toc_categories)
    sections = "\n\n".join(
        render_category(slug, title, intro, entries) for slug, title, intro, entries in categories_data
    )
    total = sum(len(entries) for _, _, _, entries in categories_data)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Radiology Opportunities Tracker</title>
  <meta name="description" content="Curated tracker of research, AI/informatics, conference, award, grant, and educational opportunities for radiology trainees.">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>
  <header role="banner">
    <h1>Radiology Opportunities Tracker</h1>
    <p class="tagline">Research, AI/informatics, conferences, awards, and education for radiology trainees.</p>
    <p class="meta">
      <span>{total} entries across {len(categories_data)} categories</span>
      <span aria-hidden="true"> · </span>
      <span>Last built {today}</span>
    </p>
  </header>

  <nav aria-label="Categories" class="toc">
    <h2>Categories</h2>
    <ul>
{toc}
    </ul>
  </nav>

  <main id="main" tabindex="-1">
{sections}
  </main>

  <footer role="contentinfo">
    <p>
      Most deadlines are marked <em>(verify annually)</em> — confirm current cycles on the sponsor's site before applying.
      See <a href="https://github.com/shawnktl/radiology-opportunities/blob/main/MAINTENANCE.md">MAINTENANCE.md</a>
      for refresh expectations, and <a href="https://github.com/shawnktl/radiology-opportunities/blob/main/templates/opportunity-entry.md">the entry template</a>
      to add new opportunities.
    </p>
  </footer>
</body>
</html>
"""


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)

    categories_data = []
    for slug, title in CATEGORY_ORDER:
        path = os.path.join(CATEGORIES_DIR, f"{slug}.md")
        if not os.path.isfile(path):
            print(f"Warning: missing {path}")
            continue
        intro, entries = parse_category(path)
        categories_data.append((slug, title, intro, entries))

    html_out = render_page(categories_data)
    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    total = sum(len(entries) for _, _, _, entries in categories_data)
    print(f"Built {out_path}: {total} entries across {len(categories_data)} categories")


if __name__ == "__main__":
    main()
