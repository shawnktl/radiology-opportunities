# Radiology Opportunities Tracker

## Purpose

A structured, browsable index of academic, AI/informatics, research, and award/grant opportunities relevant to radiology trainees (residents and fellows). The goal is to surface opportunities trainees might otherwise miss and make it easy to track deadlines and eligibility year over year.

## Audience

- Diagnostic radiology residents (PGY-2 to PGY-5)
- Interventional radiology residents and fellows
- Radiology subspecialty fellows (neuroradiology, body, MSK, pediatric, breast, nuclear medicine, etc.)
- Faculty mentors who advise trainees on career development

## What It Tracks

- Research fellowships, T32 slots, and summer research programs
- AI / imaging-informatics fellowships and post-residency tracks
- Conferences and society annual meetings (abstract deadlines, trainee discounts)
- Awards and grants targeted at trainees
- Educational courses (AI, statistics, leadership)

## What It Is Not

- Not a job board for attending positions
- Not a CME tracker
- Not a clinical reference
- Not a list of internal/institution-specific opportunities (this repo is public-safe)

## How It Is Organized

```
categories/                       Source of truth — one file per category
  research-opportunities.md
  ai-informatics-fellowships.md
  conferences.md
  awards-grants.md
  educational-courses.md
templates/
  opportunity-entry.md            Per-entry markdown template
build.py                          Builds docs/index.html and urgent.md
docs/
  index.html                      Rendered dashboard (GitHub Pages)
  style.css                       Hand-edited stylesheet
urgent.md                         Auto-generated 30/60/90-day digest
scripts/
  verify_links.py                 Link checker (HEAD/GET; reports 4xx/5xx)
  check_deadlines.py              Deadline parser/bucketer
prompts/
  refresh-agent.md                Manual search-for-new playbook
.github/workflows/
  weekly-refresh.yml              Sunday cron: link + deadline reporter PR
README.md                         How to browse and add entries
MAINTENANCE.md                    Refresh cadence (weekly auto, monthly LLM)
PROJECT_SUMMARY.md                This file
```

## Maintenance Philosophy

This is a *living document*. Completeness matters less than **consistency** and **ease of updating**. Deadlines drift annually; sponsors rebrand. Entries marked `(verify annually)` are intentional — verify before applying. See `MAINTENANCE.md` for the refresh process.

The repo deliberately separates two refresh activities:

- **Verification** runs weekly via GitHub Actions and is fully automated (no LLM) — link checks plus deadline bucketing produce a reporter PR.
- **Discovery** (search-for-new) is a manual LLM dispatch following `prompts/refresh-agent.md`, capped at 10 entries per run with 2 per category max. Each new entry must include a working URL the agent actually fetched.

Splitting these two activities keeps the automated cron predictable and cheap, while letting humans control when and how aggressively new entries are added.

## Contributions

The intended workflow is faculty-curated: a single owner adds and maintains entries. Trainees consume the list. Pull requests welcome from collaborators with verifiable opportunity details.
