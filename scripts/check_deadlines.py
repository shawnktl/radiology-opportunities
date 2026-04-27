#!/usr/bin/env python3
"""Parse Deadline fields in categories/*.md and report on freshness.

Outputs a markdown report covering:
  - Passed deadlines (need attention — bump to next cycle or mark verify annually)
  - Upcoming deadlines within 30 days
  - Upcoming deadlines within 60 days
  - Upcoming deadlines within 90 days

Exits 0 always — reporter, not a gate.

Usage:
    python scripts/check_deadlines.py
"""

from __future__ import annotations

import os
import re
import sys
from datetime import date, datetime, timedelta


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORIES_DIR = os.path.join(REPO_ROOT, "categories")

ENTRY_HEADER_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^\s*-\s*\*\*(?P<key>[^*]+):\*\*\s*(?P<value>.+?)\s*$", re.MULTILINE)
ISO_DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")


def parse_deadline(value: str):
    """Return (date_obj, raw) or (None, raw) if no parseable ISO date."""
    if not value:
        return None, value
    match = ISO_DATE_RE.search(value)
    if not match:
        return None, value
    try:
        return datetime.strptime(match.group(0), "%Y-%m-%d").date(), value
    except ValueError:
        return None, value


def collect_entries():
    """Yield dicts: {category_file, name, deadline_raw, deadline_date}."""
    if not os.path.isdir(CATEGORIES_DIR):
        return
    for fname in sorted(os.listdir(CATEGORIES_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(CATEGORIES_DIR, fname)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        chunks = re.split(r"\n---\n", text)
        for chunk in chunks[1:]:
            name_match = ENTRY_HEADER_RE.search(chunk)
            if not name_match:
                continue
            name = name_match.group(1).strip()
            fields = {}
            for fm in FIELD_RE.finditer(chunk):
                fields[fm.group("key").strip()] = fm.group("value").strip()
            deadline_raw = fields.get("Deadline", "")
            deadline_date, _ = parse_deadline(deadline_raw)
            yield {
                "category_file": fname,
                "name": name,
                "deadline_raw": deadline_raw,
                "deadline_date": deadline_date,
            }


def main():
    today = date.today()
    in_30 = today + timedelta(days=30)
    in_60 = today + timedelta(days=60)
    in_90 = today + timedelta(days=90)

    entries = list(collect_entries())
    passed = []
    upcoming_30 = []
    upcoming_60 = []
    upcoming_90 = []
    no_date = 0

    for entry in entries:
        d = entry["deadline_date"]
        if d is None:
            no_date += 1
            continue
        if d < today:
            passed.append(entry)
        elif d <= in_30:
            upcoming_30.append(entry)
        elif d <= in_60:
            upcoming_60.append(entry)
        elif d <= in_90:
            upcoming_90.append(entry)

    for bucket in (passed, upcoming_30, upcoming_60, upcoming_90):
        bucket.sort(key=lambda e: (e["deadline_date"], e["name"]))

    print(f"# Deadline Report — {today.isoformat()}")
    print()
    print(
        f"Scanned {len(entries)} entries. "
        f"{no_date} have no parseable ISO deadline (`(verify annually)` or freeform)."
    )
    print()

    def render(title, bucket):
        print(f"## {title} ({len(bucket)})")
        print()
        if not bucket:
            print("_None._")
            print()
            return
        print("| Deadline | Days | Entry | File |")
        print("|----------|------|-------|------|")
        for e in bucket:
            delta = (e["deadline_date"] - today).days
            print(
                f"| {e['deadline_date'].isoformat()} | {delta:+d} | "
                f"{e['name']} | `categories/{e['category_file']}` |"
            )
        print()

    render("Passed deadlines (need attention)", passed)
    render("Upcoming within 30 days", upcoming_30)
    render("Upcoming 31-60 days", upcoming_60)
    render("Upcoming 61-90 days", upcoming_90)

    return 0


if __name__ == "__main__":
    sys.exit(main())
