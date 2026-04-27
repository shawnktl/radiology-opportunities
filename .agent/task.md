# Agent Spec — Radiology Opportunities Tracker (Round 2: UX + Refresh Infra)

## Objective

Round 2 of the tracker. Round 1 bootstrap is merged (47 entries across 5 categories). This round has three deliverables:

1. **UX overhaul** — source markdown structure + rendered HTML dashboard, both optimized for at-a-glance scanning of upcoming deadlines.
2. **Weekly refresh infrastructure** — automated verification (broken-link + deadline checks) on a weekly cron, plus a documented manual playbook for the search-for-new flow.
3. **One-time refresh run NOW** — run the verifier against current entries, then search the web for 5–10 new opportunities and add them.

Goal of (3) is to test the search flow in this same dispatch so the user can see results immediately, not weeks from now.

## Scope

**SHOULD touch:**
- `categories/*.md` (restructure entries)
- `urgent.md` (new digest file at repo root)
- `build.py` and `templates/` (rendered HTML improvements)
- `docs/index.html` (regenerate)
- `scripts/verify_links.py` (new)
- `scripts/check_deadlines.py` (new)
- `prompts/refresh-agent.md` (new — manual playbook)
- `.github/workflows/weekly-refresh.yml` (new)
- `README.md`, `PROJECT_SUMMARY.md`, `MAINTENANCE.md` (update to reflect new structure)

**MUST NOT touch:**
- `BOOTSTRAP.md`, `CLAUDE.md` (leave alone unless additive append is genuinely needed)
- Anything outside the repo

## Tasks

### 1. Source structure for at-a-glance clarity

- Add a `verified:` field (ISO date) to every existing entry's frontmatter. Default to `2026-04-27` for entries you don't actually re-verify.
- Within each `categories/*.md`, sort entries: verified deadlines (soonest first), then "verify annually" entries.
- Create `urgent.md` at repo root: a single digest listing all opportunities with verified deadlines in the next 90 days, grouped into 30 / 60 / 90 day buckets, soonest first. Each row links to the source category file.

### 2. Rendered HTML overhaul

Improve `build.py` + `templates/` so `docs/index.html` has:

- **Dashboard header** with counts: total opportunities, upcoming-30d, upcoming-60d, upcoming-90d. Make these visually prominent — they're the at-a-glance value.
- **Deadline color coding** per entry: red (≤30 days), amber (31–60), green (61–90), gray (>90 or "verify annually").
- **Filter chips** for category (pure-JS, no backend, no build step). User clicks a chip → shows only that category. "All" chip resets.
- **Sort selector** — by deadline (default) vs alphabetical.
- Preserve existing accessibility (semantic landmarks, skip link, dark mode, print stylesheet).

Keep the build pipeline simple — single-file output, no JS framework, plain Python build. The current build.py is the right baseline; extend it, don't replace it.

### 3. Weekly refresh infrastructure

- `scripts/verify_links.py` — iterates every URL in `categories/*.md`, does HEAD requests, reports 4xx/5xx/timeouts to stdout in markdown table form. Use `requests` library (add to a `requirements.txt` if needed). Should exit 0 even on failures (it's a reporter, not a gate).
- `scripts/check_deadlines.py` — parses `deadline:` fields, flags ones that have passed and ones within 30 days, outputs markdown report.
- `prompts/refresh-agent.md` — manual playbook for the search-for-new agent (i.e., a future Claude Code dispatch). Should list:
  - Source domains to check (RSNA.org, ARRS.org, ACR.org, ASNR.org, NIH NRSA pages, HHMI medical research fellows, RSNA R&E Foundation, AAR, SIIM, society career boards)
  - Search queries to use
  - Target categories
  - Cap: 10 new entries per run, 2 per category max
  - Verification expectations (must include a working URL; mark `verified: <today>`)
- `.github/workflows/weekly-refresh.yml` — cron `0 9 * * 0` (Sunday 9am UTC). Runs both scripts, captures stdout, opens a PR titled `weekly-refresh: <date>` with the combined report as the PR body and any auto-fixable changes (none expected by default — this is a reporter workflow). Use `peter-evans/create-pull-request@v6` action. Do NOT auto-merge.

The search-for-new step is **not automated** in the workflow — it requires an LLM call. Document that in `prompts/refresh-agent.md` as a manual dispatch step. The workflow alone does verification + reporting; the human (or a Claude Code agent invoked manually) handles the search.

### 4. One-time refresh run (in this same PR)

After (1)–(3) are in place:

a. Run `python scripts/verify_links.py` on the current entries. For any 4xx/5xx links found, fix them (either find the correct URL via a quick web search and update, or mark the entry `link_status: broken` and leave a TODO comment).

b. Run `python scripts/check_deadlines.py`. For passed deadlines, either update to next year's deadline (if you can find it via a quick web search) or mark `(verify annually)`.

c. **Search for 5–10 new opportunities.** Use WebSearch and WebFetch tools. Stick to the source domains listed in `prompts/refresh-agent.md`. Each new entry MUST include a working URL and `verified: 2026-04-27`. Spread across categories (2 per category max). Commit each addition as `agent: add <opportunity name> to <category>`.

d. Regenerate `docs/index.html` and `urgent.md` to reflect all changes.

### 5. Documentation pass

- Update `README.md` to mention the dashboard, filter UI, and weekly-refresh cadence.
- Update `MAINTENANCE.md` to document the new flow: weekly automated verifier + monthly (or as-needed) manual search-for-new dispatch.
- Update `PROJECT_SUMMARY.md` if scope/audience framing has shifted.

## Constraints

- Work on branch `agent/radiology-opportunities-repo` (will be cleanly recreated from `master` by the dispatch script — old merged branch was deleted before re-dispatch).
- Commit with prefix `agent:`. Logical groups (one commit per task section is fine; finer-grained for new entries is better).
- Cap new opportunities at 10 per run, 2 per category max. **Real opportunities only** — must include a working URL you actually fetched. If you can't find a working URL, don't add it.
- Public content only. No PII, no Downstate-specific information.
- Do not modify `CLAUDE.md` or `BOOTSTRAP.md` unless additive append is essential.
- The PR should be reviewable in one sitting — if the diff balloons past ~2000 lines, stop and split.

## Acceptance Criteria

- [ ] `urgent.md` exists at repo root with deadline-sorted 30/60/90 digest
- [ ] Every entry in `categories/*.md` has a `verified:` field
- [ ] `docs/index.html` shows the dashboard header (counts), filter chips, deadline color coding, and sort selector
- [ ] `scripts/verify_links.py` and `scripts/check_deadlines.py` exist and run cleanly (`python scripts/verify_links.py` returns 0)
- [ ] `.github/workflows/weekly-refresh.yml` exists and is syntactically valid (`actionlint` clean if you can verify)
- [ ] `prompts/refresh-agent.md` documents the search playbook with explicit source domains and the per-run cap
- [ ] At least 5 new real opportunities added in this run, with verified URLs and accurate deadlines
- [ ] `MAINTENANCE.md` and `README.md` reflect the new flow
- [ ] PR open against `master` titled `agent: round 2 — UX overhaul + weekly refresh + search run`

## Context

Round 1 produced 47 entries across 5 categories (research, AI/informatics, conferences, awards-grants, educational) with mostly `(verify annually)` deadlines. The structure works but the rendered output reads like a long list — there's no visual cue for "what should I act on this week." The user wants this to be at-a-glance scannable for trainees and sustainable to maintain via weekly verification + occasional human-dispatched searches.

The repo is public-facing eventually (currently private; flip to public after this round merges and the user reviews). Default branch is `master`. The user has dispatch access via `~/repos/radiology-opportunities`.
