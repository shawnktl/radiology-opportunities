# Maintenance

This repo is a **living document** maintained by hand. Sponsors change names, URLs move, deadlines drift, programs end. Entries are accurate at the time they were added but **should not be trusted blindly** — always verify on the sponsor's site before applying.

## Refresh Cadence

| Cadence | What to Do |
|---------|------------|
| **Annually (recommended: each summer)** | Walk every category file. For every entry, open the link and confirm the program still exists, eligibility hasn't changed, and the deadline window is current. Update or mark stale entries. |
| **Quarterly (light pass)** | Skim category files for entries marked `(verify annually)` whose typical submission window is approaching. Confirm deadlines for those specifically. |
| **Ad hoc** | Whenever a new opportunity is encountered (society email, mentor recommendation, conference flyer), add it immediately while details are fresh. |

## Verification Checklist (per entry, during refresh)

- [ ] Sponsor name still correct (no rebrand or merger)
- [ ] Link still resolves (not 404, not redirected to unrelated page)
- [ ] Eligibility unchanged (PGY level, citizenship, membership requirements)
- [ ] Deadline is current cycle's date (or remains `(verify annually)`)
- [ ] Description still accurate (program scope hasn't materially changed)
- [ ] Award amount / duration / stipend still accurate (if mentioned)

## When to Mark `(verify annually)` vs. a Specific Date

Use `(verify annually)` when:
- The sponsor doesn't publish a stable date (it shifts week-to-week year over year).
- The maintainer hasn't confirmed the current cycle.
- The deadline depends on a rolling submission or selection cycle.

Use a specific date only when:
- It's been confirmed on the sponsor's site for the current cycle.
- The date is known to be stable across years (rare — most aren't).

When in doubt, prefer `(verify annually)`. A vague-but-honest entry is more useful than a confidently wrong one.

## When to Remove an Entry

Generally **don't**. Even discontinued programs are worth keeping with a `Notes: Discontinued YYYY` line, because:
- Trainees searching for the program won't find it elsewhere and end up confused.
- Sometimes programs return under a new name — the historical entry helps connect the dots.

Remove only if:
- The entry was added in error (wrong organization, misattributed sponsor).
- The entry duplicates another.

## Owner

Single faculty maintainer (the repo owner). Pull requests welcome from collaborators who can cite a sponsor URL for any entry they propose.

## Adding a New Category

If a meaningful category emerges (e.g., "global health rotations," "industry research fellowships"):

1. Create `categories/<new-category>.md` using the existing files as a template.
2. Add a row to the README's category table.
3. Seed with at least 3–5 real entries before merging.
4. Update `PROJECT_SUMMARY.md` if the scope materially expands.
