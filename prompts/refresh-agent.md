# Refresh Agent Playbook

This is a **manual playbook** for an LLM-driven agent (Claude Code, Codex, etc.) tasked with finding new radiology trainee opportunities and adding them to this repo.

The weekly GitHub Action (`.github/workflows/weekly-refresh.yml`) only verifies links and flags deadlines. It does **not** call any LLM. The "search for new opportunities" step is dispatched manually by a human inviting an agent into the repo.

---

## When to dispatch

- Monthly, or when a verifier run flags many `(verify annually)` entries that should be checked.
- Whenever a maintainer encounters a society newsletter, mentor email, or conference flyer mentioning programs that aren't yet in the tracker.

## Per-run cap

Hard limits enforced by the maintainer at PR review:

- **At most 10 new entries per run.**
- **At most 2 new entries per category per run.**
- Each new entry MUST include a working URL the agent actually fetched (`WebFetch` succeeded with HTTP 200).
- Each new entry MUST include `**Verified:** YYYY-MM-DD` set to the run date.

If a candidate opportunity has no working URL, **do not add it.** Report it in the PR description as a "couldn't verify" line for the human to investigate.

## Source domains (start here)

These are the canonical sources for trainee opportunities. Stick to these — do not crawl the open web indiscriminately.

| Domain | What's there |
|--------|--------------|
| https://www.rsna.org | RSNA Annual Meeting, R&E Foundation grants, AI certificate program, awards |
| https://www.rsna.org/research/funding-opportunities | Resident, Fellow, Medical Student grants; RRAF |
| https://www.arrs.org | ARRS Annual Meeting, scholarship and roentgen awards |
| https://www.acr.org | ACR Annual Meeting, RFS, Rutherford-Lavanty, RLI |
| https://www.asnr.org | ASNR Annual Meeting, trainee research awards |
| https://www.sirweb.org | SIR Annual Scientific Meeting, SIR Foundation grants |
| https://abdominalradiology.org | SAR Annual Meeting, trainee awards, DFDIs |
| https://www.sbi-online.org | SBI/ACR Breast Imaging Symposium, resident/fellow awards |
| https://siim.org | SIIM Annual Meeting, CIIP, fellowship listings |
| https://miccai.org | MICCAI proceedings, tutorials |
| https://spie.org/conferences-and-exhibitions/medical-imaging | SPIE Medical Imaging |
| https://www.aur.org | AUR Annual Meeting, educator programs |
| https://www.hhmi.org/science-education/programs/medical-research-fellows-program | HHMI Medical Research Fellows |
| https://www.lrp.nih.gov | NIH Loan Repayment Program |
| https://www.nibib.nih.gov | NIBIB training mechanisms |
| https://www.theabr.org | ABR (Holman Pathway, etc.) |
| https://cdmrp.health.mil | DoD CDMRP trainee awards |
| https://www.dorisduke.org | Doris Duke Foundation programs |
| https://www.sarnofffoundation.org | Sarnoff Cardiovascular Research Fellowship |

If a society publishes opportunities at a different URL than listed above, follow the link from the canonical society homepage rather than guessing.

## Suggested search queries

Use these as starting points (substitute society names as needed):

- `"radiology resident" research grant 2026`
- `"radiology trainee" award 2026 site:rsna.org`
- `"medical student" radiology research fellowship deadline`
- `imaging informatics fellowship 2026-2027`
- `<society acronym> trainee award deadline`
- `RSNA Research Resident Grant deadline`
- `ASNR trainee award application`
- `SIR Foundation resident research grant deadline`

## Target categories

Spread additions across the existing five categories:

| Category file | What fits |
|---------------|-----------|
| `categories/research-opportunities.md` | T32 slots, Doris Duke / HHMI / Sarnoff style fellowships, society research grants for trainees |
| `categories/ai-informatics-fellowships.md` | Imaging-informatics fellowships, AI/ML post-residency tracks, NIBIB training mechanisms |
| `categories/conferences.md` | Society annual meetings, abstract deadlines |
| `categories/awards-grants.md` | Roentgen-style awards, Rutherford-Lavanty-style fellowships, society research awards |
| `categories/educational-courses.md` | AI courses, statistics workshops, leadership programs, RSNA AI Certificate |

If the agent identifies a meaningful new category (e.g., "global health rotations"), it should propose it in the PR description rather than creating a new category file unilaterally.

## Workflow per candidate

For each candidate opportunity:

1. **Find a candidate** via WebSearch, restricted to the source domains above.
2. **Fetch the canonical page** with WebFetch. If the URL doesn't return 200, discard and move on.
3. **Confirm it's trainee-relevant** — must explicitly include residents, fellows, or medical students in eligibility, OR be a meeting/course directly useful to trainees.
4. **Extract** sponsor, eligibility, deadline (ISO date if known; else `(verify annually)`), recurrence, link, 1-sentence description, optional notes.
5. **Avoid duplicates** — `grep -i` the candidate name and sponsor across `categories/*.md` before adding.
6. **Append using the template** at `templates/opportunity-entry.md`. Set `**Verified:** <today>`.
7. **Commit** with `agent: add <name> to <category>`.

## Verification expectations

The automated weekly verifier (`scripts/verify_links.py`) will catch broken links on the next Sunday cron run. The agent is responsible for ensuring:

- The URL is canonical (society root or stable subpage), not a year-specific marketing page that will rot.
- The `**Verified:**` date is the date the agent actually fetched the page.
- Deadlines marked with an ISO date (`2026-09-15`) MUST be confirmed on the sponsor's page in the run; otherwise prefer `(verify annually) — typically <month>`.

## Outputs

When done, the agent should:

- Open a PR titled `agent: refresh — <date>` with the new entries grouped by category in the body.
- Note in the PR body any candidates that were found but couldn't be verified (no working URL, ambiguous eligibility, etc.).
- Run `python build.py` and include the regenerated `docs/index.html` and `urgent.md` in the PR.
