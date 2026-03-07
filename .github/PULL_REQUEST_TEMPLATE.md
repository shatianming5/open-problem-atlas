## What does this PR do?

<!-- Brief description of the change -->

## Type of change

- [ ] New problem(s) added
- [ ] Lead(s) proposed
- [ ] Status change
- [ ] Attempt recorded
- [ ] Source added
- [ ] Schema/validator change
- [ ] Site/UI change
- [ ] Pipeline/ingestion change
- [ ] Documentation
- [ ] Bug fix
- [ ] Other

## Checklist

### For new problems:
- [ ] Follows `opa.<domain>.<subdomain>.<slug>` ID convention
- [ ] Has canonical statement
- [ ] Has at least one Tier 1 canonical source
- [ ] Has status evidence
- [ ] Has domain and subdomain
- [ ] Has `last_reviewed_at` date
- [ ] Machine-generated fields (if any) have `disclaimer: unverified`
- [ ] Passes `python -m review.validators.validate_all`
- [ ] Not a duplicate of existing entry

### For status changes:
- [ ] Primary evidence provided
- [ ] Status history preserved
- [ ] Domain reviewer approval obtained (for open → solved/disproved)

### For attempts:
- [ ] References valid problem ID
- [ ] Actor/model/version specified
- [ ] Method summary provided
- [ ] Tools and environment documented
- [ ] Verification status marked
- [ ] No unverified claims mixed into truth layer

### For code changes:
- [ ] Tests pass
- [ ] Linting passes
- [ ] No breaking changes to data format
