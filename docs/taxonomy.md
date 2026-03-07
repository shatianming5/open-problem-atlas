# Taxonomy

## Entry Types

Every item in the atlas belongs to exactly one of three types:

### 1. Problem (`problem`)

A verified open problem with:
- Precise, unambiguous canonical statement
- At least one Tier 1 source
- Confirmed status with evidence
- Human review record

Problems live in `data/problems/` organized by domain.

### 2. Lead (`lead`)

A candidate open problem that has not been fully verified:
- May come from automated extraction, blog posts, or community tips
- May be imprecise, duplicated, or already solved
- Lives in `data/leads/` and enters a review queue

Leads are expected to be noisy. That's by design.

### 3. Attempt (`attempt`)

A recorded AI or human attempt on a verified problem:
- Must reference a valid problem ID
- Must specify actor, method, tools, and date
- Must be marked `verified` or `unverified`
- Lives in `data/attempts/`

Attempts never enter the truth layer of a problem.

---

## Domains (v1)

### Mathematics (`mathematics`)

Subdomains:
- `number-theory`
- `combinatorics`
- `graph-theory`
- `algebra`
- `analysis`
- `geometry`
- `topology`
- `probability`
- `dynamical-systems`
- `logic-and-foundations`

### Theoretical Computer Science (`theoretical-cs`)

Subdomains:
- `complexity-theory`
- `algorithms`
- `graph-algorithms`
- `cryptography`
- `information-theory`
- `computational-geometry`
- `formal-languages`
- `distributed-computing`
- `quantum-computing`

### Mathematical Physics (`mathematical-physics`)

Subdomains:
- `quantum-information`
- `statistical-mechanics`
- `quantum-field-theory`
- `general-relativity`
- `string-theory`
- `condensed-matter-theory`

---

## Status Labels

### Problem Status

| Status | Meaning |
|--------|---------|
| `open` | No known solution or disproof |
| `partially_solved` | Partial progress but not fully resolved |
| `solved` | Complete solution exists with evidence |
| `disproved` | Counterexample or disproof exists |
| `conditional` | Solved assuming an unproven hypothesis |
| `independent` | Shown independent of standard axioms |
| `ambiguous` | Statement is disputed or ill-defined |
| `retired_duplicate` | Merged into another entry |

### Engineering Status

| Status | Meaning |
|--------|---------|
| `lead_unverified` | Candidate not yet verified |
| `needs_status_refresh` | Status may be outdated |

### Status Change Rules

Transitioning from `open` to `solved` or `disproved` requires:
1. Primary evidence (paper, proof reference)
2. At least one domain reviewer approval
3. Maintainer approval
4. Status history entry preserved (no deletion)

---

## Problem Type

| Type | Description |
|------|-------------|
| `conjecture` | A specific mathematical conjecture |
| `open_question` | A well-defined question without conjectured answer |
| `characterization` | Seeking a characterization of some class |
| `existence` | Does an object with certain properties exist? |
| `computation` | Determine the value of a specific quantity |
| `classification` | Classify all objects of a given type |
| `algorithm` | Find an algorithm with specified properties |
| `bound` | Determine tight bounds on a quantity |

## Answer Type

| Type | Description |
|------|-------------|
| `boolean` | Yes/no answer |
| `numeric` | A specific number or formula |
| `constructive` | An explicit construction |
| `existential` | Existence proof (not necessarily constructive) |
| `classification_list` | A complete list or characterization |
| `algorithm` | An algorithm or procedure |
| `bound` | Upper/lower bound or asymptotic |

## Verification Mode

| Mode | Description |
|------|-------------|
| `proof` | Requires a mathematical proof |
| `formal_proof` | Requires a formal proof in a proof assistant |
| `expert_review` | Requires expert consensus |
| `computational` | Can be verified by computation |
| `mixed` | Combination of methods |

---

## Tags

### Formalization Tags
- `formalizable` — Problem can be stated in a proof assistant
- `lean-linked` — Has an existing Lean formalization
- `coq-linked` — Has an existing Coq formalization
- `formalization-wanted` — Community seeks formalization

### Solver-Ready Tags
- `has-exact-answer-shape` — Answer has a known form
- `computational-search-possible` — Brute force or search may help
- `sat-smt-friendly` — Amenable to SAT/SMT solvers
- `python-checkable` — Can verify with Python code
- `counterexample-friendly` — Disproving may be easier than proving

### AI Fitness Tags
- `decomposable` — Can be broken into subproblems
- `literature-review-helpful` — AI survey could add value
- `pattern-recognition` — May benefit from ML pattern finding

---

## Scores (0.0–1.0)

| Score | Meaning |
|-------|---------|
| `impact` | How significant is this problem to its field? |
| `underexplored` | How little recent attention has it received? |
| `toolability` | How amenable is it to computational tools? |
| `formality` | How precisely can the statement be formalized? |
| `ai_fit` | How well-suited is it for AI approaches? |
