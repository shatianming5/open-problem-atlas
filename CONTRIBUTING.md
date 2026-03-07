# Contributing to OpenProblemAtlas

Thank you for your interest in contributing! This project thrives on community input from researchers, students, engineers, and domain experts.

## Ways to Contribute

### 1. Add a Verified Problem

Use the [Add Problem](../../issues/new?template=add-problem.yml) issue form.

**Requirements:**
- Canonical statement (precise, unambiguous)
- At least one Tier 1 source (paper, problem list, survey, textbook)
- Current status with evidence
- Domain and subdomain classification

### 2. Propose a Radar Lead

Use the [Propose Lead](../../issues/new?template=propose-lead.yml) issue form.

Leads are candidate open problems that haven't been fully verified yet. They can come from papers, blogs, discussions, or personal knowledge.

### 3. Report a Status Change

Use the [Report Status Change](../../issues/new?template=report-status-change.yml) issue form.

If you know that an open problem has been solved, disproved, or partially resolved, report it with evidence.

**Status changes from `open` to `solved`/`disproved` require:**
- Primary evidence (paper link, proof reference)
- At least one domain reviewer approval
- Maintainer approval

### 4. Submit an AI/Human Attempt

Use the [Add AI Attempt](../../issues/new?template=add-ai-attempt.yml) issue form.

**Requirements:**
- Reference to an existing problem ID
- Actor/model identification
- Method description or prompt summary
- Tools and environment used
- Clear `verified` or `unverified` label

### 5. Improve Existing Data

- Fix typos or errors in problem statements
- Add missing sources or partial results
- Add formalization links (Lean/Coq)
- Improve classification tags

## Data Quality Standards

### Verified Problems (Atlas layer)
- Every fact field must have a source
- Machine-generated fields must be clearly marked
- Status must have evidence
- All entries must pass schema validation

### Leads (Radar layer)
- Can be noisy — that's expected
- Must have at least one source reference
- Should include confidence assessment

### Attempts (Lab layer)
- Must reference a valid problem ID
- Must specify actor, model, version, date
- Must be marked `verified` or `unverified`
- Default label is `unverified` + `machine-generated`

## Development Setup

```bash
# Clone and install
git clone https://github.com/OpenProblemAtlas/open-problem-atlas.git
cd open-problem-atlas
pip install -e ".[dev]"

# Run validation
python -m review.validators.validate_all

# Run tests
pytest tests/
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all validations pass: `python -m review.validators.validate_all`
5. Submit a PR using the PR template
6. Wait for review

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).
