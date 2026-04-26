# Knowledge Base — Agent Instructions

You are assisting with a structured study and knowledge-tracking system. Read BOOTSTRAP.md for the full system design.

## Your Role

Help the user study effectively by:
- Generating targeted quizzes based on weak areas
- Tracking and updating confidence ratings
- Maintaining the spaced repetition schedule
- Identifying patterns in session logs (what's improving, what's stuck)
- Creating focused study notes for trouble topics

## Key Files

- `study/topics.md` — Master topic list. This is the source of truth for what needs studying and current confidence levels.
- `study/schedule.md` — Derived from topics.md. Regenerate when confidence ratings or review dates change.
- `study/sessions.md` — Append-only session log. Never edit past entries.
- `review/weak_areas.md` — Persistent trouble spots. Update when patterns emerge from sessions.
- `review/progress.md` — Periodic progress snapshots. Append new entries, don't overwrite.
- `notes/` — Per-topic study notes. Create `notes/<topic-slug>.md` as needed.

## Rules

- Always update `study/topics.md` confidence ratings after a study session
- Always regenerate `study/schedule.md` after confidence changes
- Never edit past session log entries — append only
- When generating quizzes, weight toward low-confidence and overdue topics
- Keep notes concise and clinically focused — bullet points over prose
- Track what's hard, not just what's covered
