---
analyzer: codex/gpt-5.4
reasoning: xhigh
date: 2026-03-07
task: leads quality audit
scope: data/leads/
---

# Leads Quality Audit

## Executive Summary

I structurally scanned all `1,010` files in `data/leads/` and directly read a stratified sample of `210` leads:

- `10` named files
- `50` from `lead-math-*`
- `50` from `lead-tcs-*`
- `50` from `lead-phys-*`
- `50` from `lead-mixed-*`

Point estimate for genuinely useful radar entries: **about 40%**.

- Strict sample clean rate: `77 / 210 = 36.7%`
  - This counts duplicates, non-open/meta-follow-on entries, vague/template-like statements, and taxonomy failures as quality issues.
- If taxonomy drift is treated as metadata-only instead of content quality, the upper bound rises to about `59%`.
- After manual adjustment for additional atlas-grade canonical problems that the heuristic flags undercount, the realistic quality rate is **roughly 35% to 45%**, with **40%** as the best single estimate.

Main conclusion: the lead set is large and salvageable, but it is not a clean radar queue. It is currently a blend of:

- atlas-grade canonical problems that should be promoted out of leads
- already resolved or reframed problems
- duplicated entries across families
- broad research-program prompts rather than atomic open problems
- uncontrolled taxonomy labels
- strongly templated auto-generated records

One structural issue makes this worse: `data/problems/` is currently empty, so canonical problems have not been promoted out of radar at all.

## Method

I used two passes:

1. **Whole-corpus scan over all 1,010 files**
   - counted naming families, schema consistency, source hosts, duplicate titles, taxonomy drift, and missing fields
2. **Direct read of 210 files**
   - evenly distributed across every file family
   - used to estimate the useful-radar rate and to confirm issue categories with concrete examples

## Corpus-Level Findings

### 1. Uniform Auto-Generation Signals

The corpus shows strong signs of bulk template generation:

- `1,010 / 1,010` files use the exact same 11-key schema and key order
- `1,010 / 1,010` have `discovered_at: "2026-03-07"`
- `1,010 / 1,010` have `status: "lead_unverified"`
- extraction methods are only:
  - `800` `survey_extraction`
  - `200` `arxiv_extraction`
  - `10` `manual_seed`
- source hosts are concentrated in a few buckets:
  - `355` Wikipedia
  - `349` arXiv
  - `253` DOI links
  - `27` MathOverflow

Statement style is also repetitive:

- median statement length: `127` characters
- `108` statements contain `What is the`
- `35` contain `Determine`
- `31` contain `Is there`

This does not prove the leads are wrong, but it strongly suggests low-human-review generation.

### 2. Missing Critical Fields

No file is missing a field from the current minimal 11-key lead schema. The problem is that the current schema is too thin for review work.

Relative to the target shape described in the audit brief, **all 1,010 leads are missing**:

- `lead_id`
- structured `source`
- normalized `domain`
- normalized `subdomains`
- `tags`

The dataset currently stores only `source_id`, `source_url`, `domain_hint`, and `subdomain_hint`. That makes promotion, dedupe, filtering, and review much harder than necessary.

## Categorized Issues

### 1. Atlas-Grade Canonical Problems Parked in Leads

Many entries are not “radar leads” in the normal sense. They are already famous, crisp, and stable enough to belong in `data/problems/` once verified.

Examples:

- `abc-conjecture.yaml`
- `cerny-conjecture.yaml`
- `dynamic-optimality-conjecture.yaml`
- `erdos-straus-conjecture.yaml`
- `log-rank-conjecture.yaml`
- `normality-of-pi.yaml`
- `schanuel-conjecture.yaml`
- `second-hardy-littlewood-conjecture.yaml`
- `lead-math-001.yaml` (`Goldbach's Conjecture`)
- `lead-tcs-001.yaml` (`P vs NP Problem`)
- `lead-math-074.yaml` (`Inverse Galois Problem`)
- `lead-math-392.yaml` (`Tate Conjecture`)
- `lead-math-362.yaml` (`Navier-Stokes Existence and Smoothness`)
- `lead-math-361.yaml` (`Yang-Mills Existence and Mass Gap`)

These are useful mathematical objects, but they are mis-layered. A radar queue should primarily contain uncertain or newly surfaced candidates, not canonical atlas entries.

### 2. Not Actually Open Problems

This category is the most severe. These files encode statements that are already solved, disproved, or explicitly reframed as “the original problem is done, but some follow-on remains.”

Clear examples:

- `lead-math-216.yaml` — `Willmore Conjecture`
- `lead-math-217.yaml` — `Min-Oo Conjecture`
- `lead-math-221.yaml` — `Kazhdan-Lusztig Conjecture`
- `lead-math-262.yaml` — `Kadison-Singer Problem`
- `lead-math-271.yaml` — `Connes Embedding Conjecture`
- `lead-phys-001.yaml` — original additivity question already disproved by Hastings; file turns into a follow-on question
- `lead-phys-013.yaml` — statement itself says `MIP*=RE` settled Tsirelson's problem
- `lead-phys-005.yaml` — statement says NLTS was resolved and then asks about generalizations
- `lead-tcs-123.yaml` — same issue as above

Files whose own text admits the original problem is already resolved but keeps the record as a lead:

- `lead-math-069.yaml` — `Hedetniemi's Conjecture (Resolved but Generalizations Open)`
- `lead-math-118.yaml` — `Kadison-Singer Problem Generalizations`
- `lead-math-144.yaml` — `Virtually Haken Conjecture (Remaining Cases)`

Whole-corpus heuristic scan found **40** files whose title or statement explicitly contains cues such as `proved`, `disproved`, `settled`, `resolved`, `counterexample`, or `remaining cases`.

Spot-checks against the literature confirm several of these are genuinely non-open:

- `Willmore Conjecture` was solved by Marques and Neves ([arXiv:1202.6036](https://arxiv.org/abs/1202.6036))
- `Kadison-Singer Problem` was solved by Marcus, Spielman, and Srivastava ([arXiv:1306.3969](https://arxiv.org/abs/1306.3969))
- `Connes Embedding Conjecture` received a negative answer via `MIP*=RE` ([arXiv:2001.04383](https://arxiv.org/abs/2001.04383))
- `Min-Oo Conjecture` has a counterexample ([arXiv:1007.2873](https://arxiv.org/abs/1007.2873))

### 3. Duplicate Leads

Cross-family dedupe is failing.

- duplicate-title clusters found: **49**
- files involved in duplicate-title clusters: **106**

Representative duplicate clusters:

- `erdos-straus-conjecture.yaml`
- `lead-math-011.yaml`
- `lead-mixed-090.yaml`

- `normality-of-pi.yaml`
- `lead-math-016.yaml`
- `lead-mixed-157.yaml`

- `lead-tcs-117.yaml`
- `lead-phys-004.yaml`
- `lead-mixed-003.yaml`

- `lead-math-097.yaml`
- `lead-math-362.yaml`
- `lead-phys-186.yaml`

- `lead-math-120.yaml`
- `lead-math-335.yaml`
- `lead-mixed-147.yaml`

- `lead-math-191.yaml`
- `lead-tcs-001.yaml`

There are also same-title duplicates inside math where only the subdomain changes:

- `lead-math-145.yaml` and `lead-math-275.yaml` (`Baum-Connes Conjecture`)
- `lead-math-122.yaml` and `lead-math-391.yaml` (`Birch and Swinnerton-Dyer Conjecture`)
- `lead-math-114.yaml` and `lead-math-332.yaml` (`Bochner-Riesz Conjecture`)
- `lead-math-221.yaml` and other solved/theorem-style records are not deduped against their related variants

### 4. Vague, Bundled, or Meaningless Statements

Many entries are not atomic open problems. They are umbrella programs, optimization agendas, “improve this theorem” prompts, or multi-question bundles.

Examples:

- `lead-math-082.yaml` — `Several related conjectures remain open`
- `lead-mixed-195.yaml` — `Can recent IMO geometry problems be systematically resolved...`
- `lead-phys-094.yaml` — `Glass Transition Theory`
- `lead-phys-098.yaml` — asks for a `complete theory` of turbulence
- `lead-phys-123.yaml` — `Black Hole Information Paradox` as a field-wide puzzle, not a scoped problem record
- `lead-phys-200.yaml` — asks whether an entire AQFT program can give a `complete non-perturbative construction`
- `lead-mixed-155.yaml` — `Barriers in Communication Complexity`
- `lead-mixed-200.yaml` — `Supersymmetry Breaking and Mathematical Structure`

Whole-corpus broadness heuristic flagged **237** files with phrasing such as:

- `What is the optimal...`
- `What is the exact...`
- `complete picture`
- `comprehensive theory`
- `generalization`
- `extensions`
- `progress`
- `beyond`
- `fully classify`

These are often useful research directions, but they are weak dataset entries because they are not crisp enough for review or downstream tooling.

### 5. Misclassified or Taxonomy-Drifted Leads

The repo taxonomy in `docs/taxonomy.md` defines a relatively small controlled vocabulary. The lead files do not follow it consistently.

- files with `subdomain_hint` outside the controlled taxonomy: **389 / 1,010** (`38.5%`)

Examples of obvious problems:

- `lead-math-191.yaml` puts `P vs NP Problem` under `mathematics / logic`
- `lead-phys-188.yaml`, `lead-phys-192.yaml`, `lead-phys-196.yaml`, `lead-phys-200.yaml` use `mathematical-physics` as both domain and subdomain
- `cerny-conjecture.yaml` uses `automata-theory`, which is not in the TCS taxonomy
- `dynamic-optimality-conjecture.yaml` uses `data-structures`, which is not in the TCS taxonomy
- `lead-mixed-001.yaml` uses `algorithmic-game-theory`
- `lead-mixed-042.yaml` uses `meta-complexity`
- `lead-mixed-058.yaml` uses `condensed-matter`
- `lead-mixed-086.yaml` uses `scattering-amplitudes`
- `lead-mixed-143.yaml` uses `holography`

Some of these are reasonable academic labels. The quality problem is not that the labels are absurd; it is that the dataset is mixing controlled taxonomy with ad hoc free text, which breaks consistency and dedupe.

### 6. Template-Generated Follow-On Leads

A recurring failure mode is:

1. take a famous solved or partially solved statement
2. add `generalization`, `improvement`, `remaining cases`, `progress`, or `and beyond`
3. store it as a lead

Examples:

- `lead-math-069.yaml`
- `lead-math-099.yaml`
- `lead-math-118.yaml`
- `lead-math-144.yaml`
- `lead-tcs-123.yaml`
- `lead-phys-005.yaml`
- `lead-mixed-029.yaml`
- `lead-mixed-098.yaml`
- `lead-mixed-131.yaml`

These records often have a real research topic behind them, but they are bad dataset entries because the actual open problem is no longer the title that was stored.

## Sample Quality by Family

Strict clean rate in the 210-file direct-read sample:

| Family | Sampled | Strict clean | Notes |
| --- | ---: | ---: | --- |
| named files | 10 | 0 | all are canonical named conjectures; several are duplicates of numbered entries |
| `lead-math-*` | 50 | 15 | many precise problems, but a large chunk are canonical atlas items or taxonomy-drifted |
| `lead-tcs-*` | 50 | 31 | strongest family overall, but still has broad “optimality” prompts and some resolved follow-ons |
| `lead-phys-*` | 50 | 24 | many records are broad field-level puzzles rather than scoped problems |
| `lead-mixed-*` | 50 | 7 | weakest numbered family; lots of custom subdomains, duplication, and meta-follow-on phrasing |

The clean-rate table is intentionally strict. Some entries marked unclean are still salvageable after rewording or reclassification. Even so, the dataset is far from a high-precision radar queue in its current state.

## Specific Problematic Files

The following files are concrete cleanup targets:

| File | Primary issue | Why it should be reviewed first |
| --- | --- | --- |
| `abc-conjecture.yaml` | canonical atlas item | famous, precise conjecture; not a radar-style lead |
| `lead-math-001.yaml` | canonical atlas item | `Goldbach's Conjecture` should not sit in an unverified lead bucket indefinitely |
| `lead-tcs-001.yaml` | canonical atlas item | `P vs NP` is a core atlas record, not a radar lead |
| `lead-math-191.yaml` | duplicate + wrong domain | duplicates `lead-tcs-001.yaml` and misclassifies it as mathematics |
| `erdos-straus-conjecture.yaml` | duplicate | duplicates numbered math and mixed entries |
| `normality-of-pi.yaml` | duplicate | duplicates numbered math and mixed entries |
| `lead-math-216.yaml` | not open | `Willmore Conjecture` is already solved |
| `lead-math-217.yaml` | not open | `Min-Oo Conjecture` has a counterexample |
| `lead-math-221.yaml` | not open | theorem-level statement, not an open lead |
| `lead-math-262.yaml` | not open | `Kadison-Singer Problem` is solved |
| `lead-math-271.yaml` | not open | `Connes Embedding Conjecture` is no longer open |
| `lead-math-069.yaml` | follow-on disguised as original problem | title admits the original conjecture was resolved |
| `lead-math-118.yaml` | follow-on disguised as original problem | original problem solved, remaining text is a generalization prompt |
| `lead-math-144.yaml` | follow-on disguised as original problem | same pattern |
| `lead-phys-001.yaml` | original problem disproved | file asks a different follow-on than the title names |
| `lead-phys-005.yaml` | original problem resolved | text says NLTS is resolved and pivots to generalization |
| `lead-phys-013.yaml` | original problem settled | title and statement no longer describe the same open object |
| `lead-tcs-123.yaml` | original problem resolved | `and Beyond` phrasing signals a post-solution follow-on |
| `lead-mixed-195.yaml` | not a real open problem entry | reads like a project prompt about IMO problems |
| `lead-math-082.yaml` | bundled statement | combines multiple conjectures into one lead |
| `lead-phys-098.yaml` | too vague | asks for a complete theory of turbulence |
| `lead-phys-200.yaml` | too vague | asks whether an entire AQFT program succeeds |
| `lead-mixed-155.yaml` | too vague | research-barrier prompt, not a single open problem |
| `lead-mixed-200.yaml` | too vague | broad programmatic statement |

## Recommendations

1. **Create a real promotion path into `data/problems/` immediately.**
   - Start with the named files and the most obvious classical entries.
   - `data/problems/` being empty is currently forcing all atlas-grade material to remain in radar.

2. **Retire or rewrite resolved/non-open records.**
   - If the original problem is solved or disproved, do not keep it as a lead under the old title.
   - If a genuine follow-on problem exists, create a new lead with a new title and a precise statement.

3. **Run cross-family dedupe before any further ingestion.**
   - Normalize titles and compare across `math`, `tcs`, `phys`, `mixed`, and named files.
   - Mark duplicates with merge targets instead of keeping parallel records.

4. **Enforce controlled taxonomy.**
   - Replace free-text `subdomain_hint` values with a normalized controlled list.
   - Reject entries whose domain/subdomain pair is obviously incompatible.

5. **Add missing operational fields.**
   - `lead_id`
   - structured `source`
   - normalized `domain`
   - normalized `subdomains`
   - `tags`
   - optional but valuable: `alias_of`, `dedupe_cluster`, `review_state`, `promotion_candidate`

6. **Add a “vagueness lint” to ingestion.**
   - Reject titles or statements containing patterns such as:
     - `generalization`
     - `progress`
     - `and beyond`
     - `remaining cases`
     - `complete theory`
     - `fully classify`
     - `what is the optimal`
   - Require an atomic, reviewable statement.

7. **Prefer problem-specific sources over generic source pages.**
   - A lead may start from Wikipedia, MathOverflow, or arXiv.
   - Promotion should require problem-specific evidence, not just a generic survey or forum page.

## Bottom Line

The corpus is useful as a **raw candidate pool**, but not yet as a **high-quality radar queue**.

- Best estimate of genuinely useful radar entries: **about 40%**
- Most urgent cleanup tasks:
  - remove or rewrite non-open records
  - dedupe across families
  - promote canonical atlas-grade problems out of leads
  - normalize taxonomy and add stable IDs/tags
