# Source Policy

## Source Tiers

### Tier 1: Canonical Sources

These can serve as the primary reference for a verified problem.

- **Problem lists** — Official compilations (e.g., Clay Millennium Problems, Erdős problems)
- **Original papers** — Where the problem was first stated
- **Surveys and textbooks** — Comprehensive reviews by domain experts
- **Expert-maintained pages** — Actively curated by recognized authorities
- **Formalized conjecture repositories** — e.g., formal-conjectures (Lean statements)

### Tier 2: Supporting Sources

These can corroborate status or provide additional context, but cannot be the sole source for a verified entry.

- **Community discussions** — MathOverflow, Math StackExchange (high-quality answers)
- **Benchmark papers** — Academic evaluations referencing the problem
- **Authoritative databases** — OEIS, MathWorld, nLab
- **Conference proceedings** — Workshop reports, problem sessions

### Tier 3: Lead Sources Only

These can only feed the Radar layer. They must never be the sole basis for a verified entry.

- **News articles** — Science journalism, press releases
- **Blog posts** — Personal blogs, even by experts
- **Social media** — Twitter/X threads, Reddit posts
- **Video content** — YouTube, lectures (unless published proceedings exist)
- **Secondary interpretations** — Articles about papers, not the papers themselves

## Rules

1. **Every verified problem must cite at least one Tier 1 source** for its canonical statement.
2. **Every status claim must cite at least one source** as evidence (Tier 1 or 2).
3. **Tier 3 sources** can only create leads in the Radar layer.
4. **No source fabrication.** Every `source_id` must correspond to a real, accessible reference.
5. **Source metadata** must include: kind, title, authors (if applicable), year, URL or DOI, and a locator (section, page, problem number).

## Source Record Format

```yaml
source_id: src_001
kind: problem_list         # paper | survey | textbook | problem_list | database | website | discussion
title: "Some Problem List"
authors:
  - "Author Name"
year: 2020
url: "https://example.com/..."
doi: "10.xxxx/..."
locator: "Problem 3.2"
tier: 1
```

## Handling Ambiguous Sources

- If a blog post references a paper, cite the paper (Tier 1), not the blog.
- If a MathOverflow answer references a result, cite the original paper when possible.
- If no Tier 1 source exists, the entry stays in Radar as a lead.

## Copyright and Fair Use

- **Never commit full-text PDFs or complete articles** to the repository.
- Store only: metadata, locators, short excerpts (fair use), and your own structured annotations.
- Respect API terms of service for all programmatic access (arXiv, Semantic Scholar, OpenAlex, etc.).
- Include acknowledgements as required by data providers.
