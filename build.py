#!/usr/bin/env python3
"""Generate a static HTML dashboard from categories/*.md content.

Renders an accessible single-page site to docs/index.html with:
  - Header dashboard (counts: total, 30d, 60d, 90d)
  - Per-entry deadline color coding (red/amber/green/gray)
  - Filter chips by category (pure JS, no framework)
  - Sort selector (by deadline / alphabetical)
  - Semantic landmarks, skip link, dark mode, print stylesheet preserved

Also regenerates urgent.md — a digest of opportunities with verified deadlines
in the next 90 days.

Usage:
    python build.py
"""

import html
import os
import re
from datetime import date, datetime, timedelta

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
CATEGORIES_DIR = os.path.join(REPO_ROOT, "categories")
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
URGENT_PATH = os.path.join(REPO_ROOT, "urgent.md")

CATEGORY_ORDER = [
    ("research-opportunities", "Research Opportunities"),
    ("ai-informatics-fellowships", "AI / Informatics Fellowships"),
    ("conferences", "Conferences"),
    ("awards-grants", "Awards & Grants"),
    ("educational-courses", "Educational Courses"),
]

FIELD_ORDER = [
    "Sponsor",
    "Eligibility",
    "Deadline",
    "Recurrence",
    "Link",
    "Description",
    "Notes",
    "Verified",
]

ENTRY_FIELD_RE = re.compile(r"^\s*-\s*\*\*(?P<key>[^*]+):\*\*\s*(?P<value>.+?)\s*$", re.MULTILINE)
URL_RE = re.compile(r"https?://\S+")
ISO_DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")


def slugify(text):
    s = re.sub(r"[^\w\s-]", "", text.lower())
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s


def parse_iso(value):
    """Return first ISO date in value as a date, or None."""
    if not value:
        return None
    m = ISO_DATE_RE.search(value)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(0), "%Y-%m-%d").date()
    except ValueError:
        return None


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


def deadline_class(deadline_date, today):
    """Return CSS class + label based on days-until-deadline."""
    if deadline_date is None:
        return "deadline-unknown", "verify annually"
    delta = (deadline_date - today).days
    if delta < 0:
        return "deadline-passed", f"passed {abs(delta)}d ago"
    if delta <= 30:
        return "deadline-red", f"in {delta}d"
    if delta <= 60:
        return "deadline-amber", f"in {delta}d"
    if delta <= 90:
        return "deadline-green", f"in {delta}d"
    return "deadline-far", f"in {delta}d"


def render_entry(entry, category_slug, today):
    name = entry["name"]
    entry_id = f"{category_slug}--{slugify(name)}"
    deadline_value = entry["fields"].get("Deadline", "")
    deadline_date = parse_iso(deadline_value)
    klass, label = deadline_class(deadline_date, today)

    badge_html = (
        f'<span class="deadline-badge {klass}" '
        f'aria-label="Deadline status: {html.escape(label)}">'
        f'{html.escape(label)}</span>'
    )

    field_rows = []
    for key in FIELD_ORDER:
        if key in entry["fields"]:
            value_html = linkify(entry["fields"][key])
            field_rows.append(
                f'      <div class="field"><dt>{html.escape(key)}</dt>'
                f'<dd>{value_html}</dd></div>'
            )
    fields_html = "\n".join(field_rows)

    sort_iso = deadline_date.isoformat() if deadline_date else "9999-99-99"
    sort_name = name.lower()
    return f"""    <article class="entry {klass}" id="{html.escape(entry_id)}" data-category="{html.escape(category_slug)}" data-deadline-iso="{sort_iso}" data-name="{html.escape(sort_name)}" aria-labelledby="{html.escape(entry_id)}-title">
      <header class="entry-header">
        <h3 id="{html.escape(entry_id)}-title">{html.escape(name)}</h3>
        {badge_html}
      </header>
      <dl class="fields">
{fields_html}
      </dl>
    </article>"""


def render_category(slug, title, intro, entries, today):
    section_id = f"category-{slug}"
    entries_html = "\n".join(render_entry(e, slug, today) for e in entries)
    intro_html = (
        f'    <p class="category-intro">{html.escape(intro)}</p>\n' if intro else ""
    )
    count = len(entries)
    return f"""  <section class="category" id="{section_id}" data-category="{slug}" aria-labelledby="{section_id}-title">
    <h2 id="{section_id}-title">{html.escape(title)} <span class="count" aria-label="{count} entries">({count})</span></h2>
{intro_html}{entries_html}
  </section>"""


def render_filter_chips(categories_data):
    chips = ['<button type="button" class="chip is-active" data-filter="all" aria-pressed="true">All</button>']
    for slug, title, _, entries in categories_data:
        chips.append(
            f'<button type="button" class="chip" data-filter="{html.escape(slug)}" '
            f'aria-pressed="false">{html.escape(title)} '
            f'<span class="chip-count">{len(entries)}</span></button>'
        )
    return "\n      ".join(chips)


def compute_dashboard_counts(categories_data, today):
    in_30 = today + timedelta(days=30)
    in_60 = today + timedelta(days=60)
    in_90 = today + timedelta(days=90)
    total = 0
    c30 = c60 = c90 = 0
    for _, _, _, entries in categories_data:
        for entry in entries:
            total += 1
            d = parse_iso(entry["fields"].get("Deadline", ""))
            if d is None:
                continue
            if today <= d <= in_30:
                c30 += 1
            elif d <= in_60:
                c60 += 1
            elif d <= in_90:
                c90 += 1
    return total, c30, c60, c90


def render_dashboard(total, c30, c60, c90):
    return f"""  <section class="dashboard" aria-label="Opportunity counts">
    <div class="stat stat-total">
      <span class="stat-value">{total}</span>
      <span class="stat-label">Total opportunities</span>
    </div>
    <div class="stat stat-30">
      <span class="stat-value">{c30}</span>
      <span class="stat-label">Due in 30d</span>
    </div>
    <div class="stat stat-60">
      <span class="stat-value">{c60}</span>
      <span class="stat-label">Due in 31&ndash;60d</span>
    </div>
    <div class="stat stat-90">
      <span class="stat-value">{c90}</span>
      <span class="stat-label">Due in 61&ndash;90d</span>
    </div>
  </section>"""


CONTROLS_SCRIPT = """
(function () {
  var chips = document.querySelectorAll('.chip');
  var entries = document.querySelectorAll('.entry');
  var sections = document.querySelectorAll('section.category');
  var sortSelect = document.getElementById('sort-select');

  function applyFilter(filter) {
    chips.forEach(function (c) {
      var active = c.dataset.filter === filter;
      c.classList.toggle('is-active', active);
      c.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    sections.forEach(function (sec) {
      if (filter === 'all') {
        sec.hidden = false;
      } else {
        sec.hidden = sec.dataset.category !== filter;
      }
    });
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      applyFilter(chip.dataset.filter);
    });
  });

  function sortEntries(mode) {
    sections.forEach(function (sec) {
      var nodes = Array.prototype.slice.call(sec.querySelectorAll('.entry'));
      nodes.sort(function (a, b) {
        if (mode === 'alpha') {
          return a.dataset.name.localeCompare(b.dataset.name);
        }
        // default: by deadline ISO ascending; unknowns sort last
        var ad = a.dataset.deadlineIso;
        var bd = b.dataset.deadlineIso;
        if (ad === bd) return a.dataset.name.localeCompare(b.dataset.name);
        return ad < bd ? -1 : 1;
      });
      nodes.forEach(function (n) { sec.appendChild(n); });
    });
  }

  if (sortSelect) {
    sortSelect.addEventListener('change', function () {
      sortEntries(sortSelect.value);
    });
    // Apply default (deadline) on load to ensure consistent order.
    sortEntries(sortSelect.value);
  }
})();
"""


def render_page(categories_data, today):
    today_iso = today.isoformat()
    total, c30, c60, c90 = compute_dashboard_counts(categories_data, today)

    sections = "\n\n".join(
        render_category(slug, title, intro, entries, today)
        for slug, title, intro, entries in categories_data
    )
    chips = render_filter_chips(categories_data)
    dashboard = render_dashboard(total, c30, c60, c90)

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
      <span aria-hidden="true"> &middot; </span>
      <span>Last built {today_iso}</span>
    </p>
  </header>

{dashboard}

  <section class="controls" aria-label="Filter and sort">
    <div class="chips" role="group" aria-label="Filter by category">
      {chips}
    </div>
    <div class="sort">
      <label for="sort-select">Sort:</label>
      <select id="sort-select">
        <option value="deadline">By deadline (soonest first)</option>
        <option value="alpha">Alphabetical</option>
      </select>
    </div>
  </section>

  <main id="main" tabindex="-1">
{sections}
  </main>

  <footer role="contentinfo">
    <p>
      Most deadlines are marked <em>(verify annually)</em> &mdash; confirm current cycles on the sponsor's site before applying.
      See <a href="https://github.com/shawnktl/radiology-opportunities/blob/main/MAINTENANCE.md">MAINTENANCE.md</a>
      for refresh expectations, and <a href="https://github.com/shawnktl/radiology-opportunities/blob/main/templates/opportunity-entry.md">the entry template</a>
      to add new opportunities.
    </p>
    <p>
      Color coding: <span class="legend-swatch deadline-red"></span> &le;30d
      <span class="legend-swatch deadline-amber"></span> 31&ndash;60d
      <span class="legend-swatch deadline-green"></span> 61&ndash;90d
      <span class="legend-swatch deadline-far"></span> &gt;90d
      <span class="legend-swatch deadline-unknown"></span> verify annually
      <span class="legend-swatch deadline-passed"></span> passed
    </p>
  </footer>

  <script>
{CONTROLS_SCRIPT}
  </script>
</body>
</html>
"""


def render_urgent(categories_data, today):
    """Render a markdown digest of opportunities with deadlines in next 90d."""
    in_30 = today + timedelta(days=30)
    in_60 = today + timedelta(days=60)
    in_90 = today + timedelta(days=90)

    buckets = {30: [], 60: [], 90: []}
    for slug, title, _, entries in categories_data:
        for entry in entries:
            d = parse_iso(entry["fields"].get("Deadline", ""))
            if d is None or d < today:
                continue
            row = {
                "name": entry["name"],
                "deadline": d,
                "category_slug": slug,
                "category_title": title,
                "deadline_raw": entry["fields"].get("Deadline", ""),
            }
            if d <= in_30:
                buckets[30].append(row)
            elif d <= in_60:
                buckets[60].append(row)
            elif d <= in_90:
                buckets[90].append(row)

    for k in buckets:
        buckets[k].sort(key=lambda r: (r["deadline"], r["name"]))

    lines = []
    lines.append("# Urgent — Upcoming Deadlines")
    lines.append("")
    lines.append(
        f"_Generated by `build.py` on {today.isoformat()}. "
        "Do not edit by hand — re-run `python build.py` after updating any "
        "`categories/*.md` file._"
    )
    lines.append("")
    total_urgent = sum(len(v) for v in buckets.values())
    if total_urgent == 0:
        lines.append(
            "No entries currently have a verified deadline within 90 days. "
            "Most entries in this tracker are marked `(verify annually)` — "
            "see `categories/` for the full list."
        )
        lines.append("")
    else:
        lines.append(
            f"{total_urgent} opportunit"
            f"{'y' if total_urgent == 1 else 'ies'} with verified deadlines "
            f"in the next 90 days, sorted soonest first."
        )
        lines.append("")

    bucket_titles = {
        30: "Within 30 days",
        60: "31–60 days",
        90: "61–90 days",
    }

    for days in (30, 60, 90):
        rows = buckets[days]
        lines.append(f"## {bucket_titles[days]} ({len(rows)})")
        lines.append("")
        if not rows:
            lines.append("_None._")
            lines.append("")
            continue
        lines.append("| Deadline | Days | Opportunity | Category |")
        lines.append("|----------|------|-------------|----------|")
        for r in rows:
            delta = (r["deadline"] - today).days
            link = (
                f"[{r['category_title']}](categories/{r['category_slug']}.md)"
            )
            lines.append(
                f"| {r['deadline'].isoformat()} | +{delta}d | "
                f"{r['name']} | {link} |"
            )
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "See [`docs/index.html`](docs/index.html) for the full dashboard "
        "with filter chips and color-coded deadline status."
    )
    lines.append("")
    return "\n".join(lines)


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)
    today = date.today()

    categories_data = []
    for slug, title in CATEGORY_ORDER:
        path = os.path.join(CATEGORIES_DIR, f"{slug}.md")
        if not os.path.isfile(path):
            print(f"Warning: missing {path}")
            continue
        intro, entries = parse_category(path)
        # Within each category, sort by deadline soonest-first; unknown last.
        entries.sort(
            key=lambda e: (
                parse_iso(e["fields"].get("Deadline", ""))
                or date(9999, 12, 31),
                e["name"].lower(),
            )
        )
        categories_data.append((slug, title, intro, entries))

    html_out = render_page(categories_data, today)
    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    urgent_md = render_urgent(categories_data, today)
    with open(URGENT_PATH, "w", encoding="utf-8") as f:
        f.write(urgent_md)

    total = sum(len(entries) for _, _, _, entries in categories_data)
    print(
        f"Built {out_path}: {total} entries across "
        f"{len(categories_data)} categories"
    )
    print(f"Built {URGENT_PATH}")


if __name__ == "__main__":
    main()
