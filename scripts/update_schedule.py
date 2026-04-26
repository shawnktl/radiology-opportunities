#!/usr/bin/env python3
"""Regenerate study/schedule.md from study/topics.md confidence ratings.

Designed to be guilt-free: no "overdue" labels, just ranked suggestions
for what would be most valuable if you have time. The system works for you,
not the other way around.

Usage: python3 scripts/update_schedule.py
"""

import os
import re
from datetime import date, timedelta

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS_PATH = os.path.join(REPO_ROOT, "study", "topics.md")
SCHEDULE_PATH = os.path.join(REPO_ROOT, "study", "schedule.md")

# Spaced repetition intervals by confidence level
INTERVALS = {
    1: 1,    # Review within 1 day
    2: 3,    # Review within 3 days
    3: 7,    # Review within 7 days
    4: 14,   # Review within 14 days
    5: 30,   # Review within 30 days
}


def parse_topics(path):
    """Parse the markdown topic table. Returns list of dicts."""
    topics = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header_found = False
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("<!--"):
            continue
        if line.startswith("| Topic"):
            header_found = True
            continue
        if line.startswith("|---") or line.startswith("**"):
            continue
        if not header_found or not line.startswith("|"):
            continue

        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 3 or not cells[0]:
            continue

        topic = cells[0]
        category = cells[1]
        try:
            confidence = int(cells[2])
        except (ValueError, IndexError):
            confidence = 1

        last_reviewed = cells[3] if len(cells) > 3 else "—"
        notes = cells[5] if len(cells) > 5 else ""

        topics.append({
            "topic": topic,
            "category": category,
            "confidence": confidence,
            "last_reviewed": last_reviewed,
            "notes": notes,
        })

    return topics


def calculate_value(topic):
    """Calculate how valuable reviewing this topic would be right now.

    Higher value = more benefit from reviewing. Considers:
    - Lower confidence topics benefit more from review
    - Topics not reviewed recently benefit more
    - But NO guilt — this is opportunity, not obligation
    """
    conf = topic["confidence"]
    # Base value from confidence (lower = more valuable to review)
    value = (6 - conf) * 10

    lr = topic["last_reviewed"]
    if lr == "—" or not lr:
        value += 15  # Never reviewed — good opportunity
    else:
        try:
            last_date = date.fromisoformat(lr)
            days_since = (date.today() - last_date).days
            interval = INTERVALS.get(conf, 7)
            # Bonus proportional to how long since last review vs ideal interval
            if days_since > interval:
                value += min((days_since - interval), 20)
        except ValueError:
            value += 5

    return value


def main():
    if not os.path.isfile(TOPICS_PATH):
        print(f"Error: {TOPICS_PATH} not found")
        return

    topics = parse_topics(TOPICS_PATH)
    if not topics:
        print("No topics found in topics.md")
        return

    today = date.today()

    # Calculate value for each topic
    for t in topics:
        t["_value"] = calculate_value(t)

    # Sort by value (highest first)
    ranked = sorted(topics, key=lambda t: t["_value"], reverse=True)

    # Group into tiers
    top_5 = ranked[:5]
    next_10 = ranked[5:15]
    rest = ranked[15:]

    # Category summary
    from collections import defaultdict
    by_cat = defaultdict(list)
    for t in topics:
        by_cat[t["category"]].append(t["confidence"])

    def format_items(items):
        if not items:
            return "(none)\n"
        lines = []
        for t in items:
            conf = t["confidence"]
            cat = t["category"]
            lines.append(f"- **{t['topic']}** [{cat}] — confidence: {conf}/5")
        return "\n".join(lines) + "\n"

    avg_conf = sum(t["confidence"] for t in topics) / len(topics)

    content = f"""# What to Study Next

*Updated {today.isoformat()} by update_schedule.py*
*No deadlines, no guilt — just ranked suggestions for when you have time.*

## If You Have 10 Minutes

Pick any one of these — they'd benefit most from a quick review:

{format_items(top_5)}
## If You Have More Time

Good candidates for a deeper session:

{format_items(next_10)}
## By Category

| Category | Topics | Avg Confidence | Weakest Area? |
|----------|--------|----------------|---------------|
"""

    for cat in sorted(by_cat.keys()):
        confs = by_cat[cat]
        cat_avg = sum(confs) / len(confs)
        weak = "←" if cat_avg <= avg_conf else ""
        content += f"| {cat} | {len(confs)} | {cat_avg:.1f}/5 | {weak} |\n"

    content += f"""
## Stats

- **{len(topics)} total topics** | **Avg confidence: {avg_conf:.1f}/5**
- {sum(1 for t in topics if t['confidence'] == 1)} untouched | {sum(1 for t in topics if t['confidence'] >= 4)} solid | {sum(1 for t in topics if t['confidence'] == 5)} mastered

---
*Regenerate anytime: `python3 scripts/update_schedule.py`*
"""

    with open(SCHEDULE_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Schedule updated: top 5 suggestions ready, {len(topics)} topics tracked")


if __name__ == "__main__":
    main()
