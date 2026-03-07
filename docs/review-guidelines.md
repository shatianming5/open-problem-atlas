# Review Guidelines

## Roles

### Maintainer
- Can approve any PR
- Required for `open → solved/disproved` status changes
- Manages project direction and scope

### Domain Reviewer
- Expert in a specific domain (math, TCS, physics)
- Can approve new problems and status changes within their domain
- At least one domain reviewer must approve each verified problem

### Contributor
- Anyone who submits issues, PRs, or data

## Review Checklist for New Problems

- [ ] `id` follows naming convention: `opa.<domain>.<subdomain>.<slug>`
- [ ] `title` is canonical and unambiguous
- [ ] `statement.canonical` is precise and self-contained
- [ ] `status.label` is correct and supported by evidence
- [ ] At least one Tier 1 source with locator
- [ ] At least one status evidence entry
- [ ] `domain` and `subdomains` are from the approved taxonomy
- [ ] `last_reviewed_at` is set
- [ ] Machine-generated fields (if any) have `disclaimer: unverified`
- [ ] No duplicate of existing entry (check aliases)
- [ ] All referenced `source_id` values exist
- [ ] All relation references point to valid problem IDs

## Review Checklist for Status Changes

- [ ] Primary evidence provided (paper link, DOI, proof reference)
- [ ] Status history note added
- [ ] At least one domain reviewer approval
- [ ] For `open → solved/disproved`: maintainer approval required
- [ ] Original entry preserved (status evolution, not deletion)

## Review Checklist for Attempts

- [ ] `problem_id` references a valid verified problem
- [ ] `actor` or `model` with version specified
- [ ] Method description or prompt summary present
- [ ] Tools and environment documented
- [ ] Marked as `verified` or `unverified`
- [ ] No unverified claims mixed into the problem's truth layer

## Review Checklist for Leads

- [ ] Has at least one source reference
- [ ] Includes a rough problem statement
- [ ] Not an obvious duplicate
- [ ] Domain classification provided

## Common Mistakes to Watch For

1. **Confusing "future work" with "open problem"** — Future work suggestions in papers are not necessarily well-defined open problems
2. **Stale status** — A problem listed as open in a 2010 survey may have been solved since
3. **Missing precision** — "Is X true?" without defining X precisely
4. **Alias confusion** — The same problem under different names
5. **AI hallucination in machine fields** — LLM-generated summaries that invent results
