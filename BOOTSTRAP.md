# KNOWLEDGE BASE — BOOTSTRAP

A structured study and knowledge-tracking system with spaced repetition.

---

## 0. HOW TO USE THIS REPO

1. Populate `study/topics.md` with your subject areas
2. Rate your confidence on each topic (1-5 scale)
3. Use an agent to generate quizzes, identify weak areas, and suggest review schedules
4. Log each study session in `study/sessions.md`
5. Periodically update confidence ratings and review `review/progress.md`

---

## 1. DIRECTORY STRUCTURE

```
project_root/
│
├── study/
│   ├── topics.md          # Master topic list with confidence ratings
│   ├── schedule.md        # Spaced repetition review schedule
│   └── sessions.md        # Study session log
│
├── notes/
│   └── (per-topic notes, created as you study)
│
├── resources/
│   └── sources.md         # Key references, textbooks, question banks
│
├── review/
│   ├── weak_areas.md      # Identified weak areas needing focus
│   └── progress.md        # Progress tracking over time
│
├── BOOTSTRAP.md           # This file
├── CLAUDE.md              # Agent instructions
└── PROJECT_SUMMARY.md     # What you're studying and why
```

---

## 2. CONFIDENCE RATING SYSTEM

Rate each topic on a 1-5 scale:

| Rating | Meaning | Review Interval |
|--------|---------|-----------------|
| 1 | Unfamiliar — haven't studied this | Review within 1 day |
| 2 | Vaguely familiar — can't explain it | Review within 3 days |
| 3 | Understand basics — could explain simply | Review within 7 days |
| 4 | Solid understanding — could answer exam questions | Review within 14 days |
| 5 | Can teach it — deep, reliable knowledge | Review within 30 days |

After each review session, update the rating:
- Got it wrong or struggled → decrease by 1 (min 1)
- Got it right with effort → keep same
- Got it right easily → increase by 1 (max 5)

---

## 3. TOPICS FORMAT

In `study/topics.md`, each topic is a row:

```markdown
| Topic | Category | Confidence | Last Reviewed | Next Review | Notes |
|-------|----------|------------|---------------|-------------|-------|
| Circle of Willis anatomy | Vascular | 3 | 2026-04-15 | 2026-04-22 | Good on anterior, weak on posterior |
```

---

## 4. SESSION LOG FORMAT

In `study/sessions.md`, log each session:

```markdown
## 2026-04-15 — 45 min

**Topics covered:** Vascular anatomy, posterior fossa tumors
**Method:** Flashcard review + case review
**What went well:** Strong on vascular territories
**What was hard:** Posterior fossa tumor DDx — keep confusing epidermoid vs dermoid
**Confidence updates:** Vascular anatomy 3→4, Posterior fossa tumors 2→2
```

---

## 5. SPACED REPETITION SCHEDULE

`study/schedule.md` is auto-generated from topics.md confidence ratings and review dates. Format:

```markdown
## Overdue
- Topic A (was due 2026-04-13, confidence: 2)

## Due Today
- Topic B (confidence: 3)

## Upcoming
- Topic C (due 2026-04-18, confidence: 4)
```

An agent can regenerate this from the current state of topics.md.

---

## 6. WEAK AREA TRACKING

`review/weak_areas.md` tracks persistent trouble spots:

```markdown
## Active Weak Areas

### Posterior Fossa Tumors
- **Pattern:** Consistently scoring 2 after 3 review sessions
- **Specific gap:** Epidermoid vs dermoid imaging features
- **Action:** Find 5 comparison cases, create focused note
```

---

## 7. AGENT WORKFLOWS

### Quiz Generation
"Generate 10 quiz questions targeting my lowest-confidence topics. Mix recall, application, and image-interpretation questions."

### Weak Area Analysis
"Review my session logs and identify topics where confidence isn't improving. Suggest targeted study strategies."

### Schedule Update
"Regenerate schedule.md based on current confidence ratings and review dates in topics.md."

### Progress Report
"Compare my confidence ratings from 2 weeks ago to now. What improved? What's stuck?"

---

## 8. SCRIPTS

Three scripts in `scripts/` to keep the study system running:

### scripts/update_schedule.py
Regenerates `study/schedule.md` with guilt-free suggestions ranked by what would benefit most from review. No deadlines, no "overdue" — just "if you have 10 minutes, here's what's most valuable."

```
python3 scripts/update_schedule.py
```

### scripts/progress_report.py
Appends a dated snapshot to `review/progress.md` with per-category breakdown and comparison to the last snapshot. Run periodically to track improvement.

```
python3 scripts/progress_report.py
```

### scripts/generate_quiz.py
Generates quiz questions targeting low-confidence topics. Outputs markdown stubs that an agent can enhance with real content.

```
python3 scripts/generate_quiz.py           # 10 questions to stdout
python3 scripts/generate_quiz.py -n 20     # 20 questions
python3 scripts/generate_quiz.py -o quiz.md  # Write to file
```

---

## 9. FUTURE ENHANCEMENTS

- Question bank integration (import existing questions, track per-question performance)
- Case library linking (reference specific imaging cases per topic)
- Exam simulation mode (timed question sets mimicking exam format)
- Cross-repo linking (connect study topics to research projects)
