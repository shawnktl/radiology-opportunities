# Agent Spec — Radiology Opportunities Tracker

## Objective

Bootstrap a structured tracking repo for academic, AI/informatics, research, and award/grant opportunities relevant to radiology trainees (residents and fellows). The repo should be browsable by category, easy to update, and seeded with a representative set of real opportunities so it's immediately useful.

## Scope

Files/dirs the agent SHOULD touch:
- `PROJECT_SUMMARY.md` (create — brief overview, audience, intended use)
- `README.md` (create — how to browse, how to add entries)
- `categories/` (create — one markdown file per category, listing entries)
- `templates/opportunity-entry.md` (create — template for new entries)
- `MAINTENANCE.md` (create — how/when to refresh)

Files/dirs the agent MUST NOT touch:
- `BOOTSTRAP.md`, `CLAUDE.md` (already from bootstrap)
- Anything outside the repo

## Tasks

1. Create `PROJECT_SUMMARY.md` describing the repo's purpose: tracking academic/AI/informatics/research opportunities for radiology trainees.
2. Create `README.md` with: audience (trainees), how to browse (by category), how to add an entry (template), how the deadline/eligibility fields work.
3. Create `categories/` directory with one markdown file per category:
   - `research-opportunities.md` (research fellowships, summer programs, T32 slots, RSUNA-style awards)
   - `ai-informatics-fellowships.md` (AI/imaging informatics fellowships, post-residency tracks)
   - `conferences.md` (RSNA, SIIM, ACR, ARRS, society annual meetings — abstract deadlines, registration, trainee discounts)
   - `awards-grants.md` (RSNA Research Resident Grant, ARRS scholar award, society-specific trainee awards)
   - `educational-courses.md` (AI courses, statistics workshops, leadership programs)
4. Seed each category with 5–10 representative real opportunities. Each entry uses the template and includes: name, sponsor, eligibility, deadline (or recurrence), link, brief description.
5. Create `templates/opportunity-entry.md` with the standard fields.
6. Create `MAINTENANCE.md` describing manual refresh expectations (deadlines drift annually; sponsors change).

## Constraints

- Work on branch `agent/radiology-opportunities-repo`
- Commit with prefix `agent:`
- Use accurate, real opportunities — verify society names and deadlines where possible. If unsure of a specific deadline, mark it `(verify annually)` rather than inventing a date.
- Public content only — no PII, no internal Downstate-specific information.
- Keep formatting consistent across categories.

## Acceptance Criteria

- [ ] `PROJECT_SUMMARY.md` and `README.md` clearly describe purpose and use
- [ ] At least 5 category files, each with ≥5 real opportunity entries
- [ ] Entry template exists at `templates/opportunity-entry.md`
- [ ] All entries follow the template format
- [ ] `MAINTENANCE.md` describes refresh approach
- [ ] No fabricated organizations or deadlines

## Context

Audience: radiology residents and fellows looking to find research, AI/informatics, and career-development opportunities they might otherwise miss. Owner is faculty (the user); maintenance is manual. The repo is a *living document* — completeness matters less than consistency and ease of updating. Seed the structure well; entries will accumulate over time.
