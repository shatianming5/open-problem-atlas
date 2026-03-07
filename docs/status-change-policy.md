# Status Change Policy

This document defines the procedures for changing a problem's status in the OpenProblemAtlas.

## Status Labels

| Status | Meaning |
|--------|---------|
| `open` | No solution is known |
| `partially_solved` | Significant progress but not fully resolved |
| `solved` | A complete, accepted solution exists |
| `disproved` | A counterexample or refutation is known |
| `conditional` | Resolved assuming an unproven hypothesis |
| `independent` | Shown independent of standard axioms |
| `ambiguous` | Problem statement is unclear or disputed |
| `retired_duplicate` | Duplicate of another entry |

## Proposing a Status Change

1. **File an issue** using the [Report Status Change](.github/ISSUE_TEMPLATE/report-status-change.yml) template.
2. Provide:
   - The problem ID (e.g., `opa.mathematics.number-theory.twin-prime-conjecture`)
   - Proposed new status label
   - At least one source (paper, preprint, or announcement) supporting the change
   - Brief summary of the claimed result

## Review Process

### Tier 1: Uncontroversial Changes
Changes where the community consensus is clear (e.g., a peer-reviewed journal publication):

- A single domain-expert reviewer can approve.
- The reviewer updates `status.label`, `status.confidence`, `status.last_reviewed_at`, and adds the source to `sources.status_evidence`.

### Tier 2: Recent or Unverified Claims
Changes based on recent preprints or unverified claims:

- Set status to `partially_solved` or the claimed status with `confidence: low`.
- Add `review_state: needs_review`.
- At least two reviewers must independently evaluate before raising confidence.

### Tier 3: Controversial or Disputed
Changes where the result is actively disputed:

- Set `confidence: low` and add both the claim and any rebuttals to `sources.status_evidence`.
- Tag the issue with `status:disputed`.
- Do not change to `solved` or `disproved` until dispute is resolved.

## Required Fields on Status Change

When updating a problem's status, you **must** update:

```yaml
status:
  label: <new_status>
  confidence: <high|medium|low>
  last_reviewed_at: "<YYYY-MM-DD>"
  review_state: human_verified
  reviewer: "<your_github_handle>"
  stale_after: "<YYYY-MM-DD>"  # typically 1 year from review
```

And add the supporting source:

```yaml
sources:
  status_evidence:
    - source_id: src_<author>_<year>
      kind: paper
      title: "<paper title>"
      url: "<doi or arxiv url>"
      year: <year>
```

## Reversion Policy

If a claimed solution is later found to contain errors:

1. Revert the status to its previous value.
2. Keep the attempted-solution source in `status_evidence` with a note.
3. Add a new evidence entry documenting the retraction or error.
4. Set `review_state: needs_review` until re-evaluated.

## Automation

- The `stale_after` field triggers periodic re-review reminders.
- CI checks validate that all status changes include updated `last_reviewed_at`.
- The monthly snapshot captures the status timeline for historical tracking.
