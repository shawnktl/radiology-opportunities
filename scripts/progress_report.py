#!/usr/bin/env python3
"""Generate a progress report comparing current confidence to last snapshot.

Usage: python3 scripts/progress_report.py
"""

import os
import re
from collections import defaultdict
from datetime import date

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS_PATH = os.path.join(REPO_ROOT, "study", "topics.md")
PROGRESS_PATH = os.path.join(REPO_ROOT, "review", "progress.md")


def parse_topics(path):
    """Parse topic table. Returns list of (topic, category, confidence) tuples."""
    topics = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header_found = False
    for line in lines:
        line = line.strip()
        if line.startswith("| Topic"):
            header_found = True
            continue
        if line.startswith("|---") or not header_found or not line.startswith("|"):
            continue
        if line.startswith("**") or line.startswith("<!--"):
            continue

        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 3 or not cells[0]:
            continue

        topic = cells[0]
        category = cells[1]
        try:
            confidence = int(cells[2])
        except ValueError:
            confidence = 1

        topics.append((topic, category, confidence))

    return topics


def parse_last_snapshot(path):
    """Parse the last snapshot from progress.md. Returns dict of topic->confidence or None."""
    if not os.path.isfile(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the last "### Per-Topic" section
    matches = list(re.finditer(r"### Per-Topic Snapshot\n(.*?)(?=\n## |\n### |\Z)", content, re.DOTALL))
    if not matches:
        return None

    last = matches[-1].group(1)
    snapshot = {}
    for line in last.strip().split("\n"):
        # Format: - Topic Name: 3
        match = re.match(r"^- (.+?):\s*(\d+)\s*$", line.strip())
        if match:
            snapshot[match.group(1)] = int(match.group(2))

    return snapshot if snapshot else None


def main():
    if not os.path.isfile(TOPICS_PATH):
        print(f"Error: {TOPICS_PATH} not found")
        return

    topics = parse_topics(TOPICS_PATH)
    if not topics:
        print("No topics found")
        return

    today = date.today()

    # Current stats
    total = len(topics)
    confidences = [c for _, _, c in topics]
    avg_conf = sum(confidences) / total

    # Per-category stats
    by_category = defaultdict(list)
    for topic, cat, conf in topics:
        by_category[cat].append(conf)

    # Compare to last snapshot
    last_snapshot = parse_last_snapshot(PROGRESS_PATH)
    improved = []
    declined = []
    unchanged = 0

    if last_snapshot:
        for topic, _, conf in topics:
            prev = last_snapshot.get(topic)
            if prev is not None:
                if conf > prev:
                    improved.append((topic, prev, conf))
                elif conf < prev:
                    declined.append((topic, prev, conf))
                else:
                    unchanged += 1

    # Build report
    report = f"\n## {today.isoformat()}\n\n"
    report += f"**Total topics:** {total} | **Avg confidence:** {avg_conf:.1f}/5\n\n"

    report += "### By Category\n\n"
    report += "| Category | Topics | Avg Confidence |\n"
    report += "|----------|--------|----------------|\n"
    for cat in sorted(by_category.keys()):
        confs = by_category[cat]
        cat_avg = sum(confs) / len(confs)
        report += f"| {cat} | {len(confs)} | {cat_avg:.1f} |\n"

    if last_snapshot:
        report += f"\n### Changes Since Last Snapshot\n\n"
        report += f"- **Improved:** {len(improved)}\n"
        for topic, prev, curr in improved:
            report += f"  - {topic}: {prev} → {curr}\n"
        report += f"- **Declined:** {len(declined)}\n"
        for topic, prev, curr in declined:
            report += f"  - {topic}: {prev} → {curr}\n"
        report += f"- **Unchanged:** {unchanged}\n"
    else:
        report += "\n*First snapshot — no previous data to compare.*\n"

    report += "\n### Per-Topic Snapshot\n\n"
    for topic, _, conf in sorted(topics, key=lambda t: t[0]):
        report += f"- {topic}: {conf}\n"

    # Append to progress.md
    if os.path.isfile(PROGRESS_PATH):
        with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
            existing = f.read()
    else:
        existing = "# Progress Tracking\n"

    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        f.write(existing.rstrip() + "\n" + report)

    print(f"Progress report appended: {total} topics, avg confidence {avg_conf:.1f}")
    if last_snapshot:
        print(f"  {len(improved)} improved, {len(declined)} declined, {unchanged} unchanged")


if __name__ == "__main__":
    main()
