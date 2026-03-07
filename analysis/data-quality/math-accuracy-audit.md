---
analyzer: codex/gpt-5.4
reasoning: xhigh
date: 2026-03-07
task: math accuracy audit
scope: data/problems/
---

# Executive Summary

I audited a broad sample of 193 YAML files:

- 48 files from `data/problems/mathematics/`
- all 85 files from `data/problems/theoretical-cs/`
- all 60 files from `data/problems/mathematical-physics/`

I found 28 files with material accuracy issues, for an estimated material-error rate of about 15% on this sample. The error concentration is much higher in `mathematical-physics/` and in the “meta/open-direction” part of `theoretical-cs/` than in the classic mathematics entries.

The dominant failure mode is not raw mathematical falsehood; it is schema drift:

- solved or disproved problems kept under the title of the old conjecture while the canonical statement quietly pivots to a different open problem
- broad research programs labeled `problem_type: conjecture`
- entries that bundle multiple distinct problems into one record
- dates that record the underlying equation/theory rather than the open problem’s formulation

Severity breakdown:

- Critical: 7
- Major: 18
- Minor: 3

I only flagged items where I could point to a specific false claim, a specific stale status, or a clear schema mismatch between the stated problem and the metadata.

# Scope Notes

- I did not attempt a full 312-file audit.
- I did inspect every file in `theoretical-cs/` and `mathematical-physics/` at least at summary level.
- The mathematics pass was a representative sample focused on famous problems, non-open-status entries, and records whose titles/paths suggested possible drift.

# Findings

## Critical

1. `data/problems/mathematics/brennan-conjecture.yaml`
   Fields: `statement.canonical`
   Wrong: The canonical statement gives Brennan’s conjecture as `4/3 < p < 3` and says the conjectured boundary is `p = 3`.
   Why wrong: The standard Brennan conjecture has upper endpoint `p = 4`, not `p = 3`. The file is internally inconsistent: its own partial results claim integrability up to `p < 3.421`, which would already exceed the stated conjectural boundary.
   Should be: Replace the canonical range with the standard Brennan range ending at `4`, and update the inverse-map reformulation accordingly.

2. `data/problems/mathematics/navier-stokes-regularity-2d-euler.yaml`
   Fields: `title`, `aliases`, `statement.canonical`, `dates.first_stated`
   Wrong: The file path says `navier-stokes-regularity-2d-euler`, but the title and canonical statement are about finite-time blow-up for the smooth `3D` incompressible Euler equations.
   Why wrong: These are different problems. Also, `1757` is the date of Euler’s equations, not of the modern 3D smooth blow-up problem.
   Should be: Either rename/move this record to a dedicated `3d-euler-blowup` entry and use a modern first-stated year consistent with the cited PDE formulation, or rewrite the record to the problem suggested by the filename. As written, it is a factual mismatch.

3. `data/problems/mathematics/smale-17th-problem.yaml`
   Fields: `status.label`, `statement.canonical`, `why_it_matters`
   Wrong: The record is marked `open` and still phrases Smale’s 17th problem as unresolved.
   Why wrong: Smale’s 17th problem was answered affirmatively by Beltrán and Pardo in 2009.
   Should be: Mark the record `solved` and rewrite the statement in historical/past-tense form, or remove it from the open-problem corpus.

4. `data/problems/theoretical-cs/art-gallery-complexity.yaml`
   Fields: `status.label`, `statement.canonical`
   Wrong: The canonical statement asks “What is the exact complexity? Is the problem in NP? Is it in the existential theory of the reals (ETR-complete)?”
   Why wrong: The file’s own `status_evidence` cites the 2018 result proving the point-guard art gallery problem is `∃R`-complete. For the stated question, the classification is no longer open.
   Should be: Either mark this version `solved` and rewrite historically, or retarget the entry to an actually open variant (approximation, restricted guard models, holes, etc.).

5. `data/problems/mathematical-physics/additivity-conjecture-quantum-channel-capacity.yaml`
   Fields: `title`, `status.label`, `problem_type`, `statement.canonical`
   Wrong: The record still presents the “additivity conjecture” as an open conjecture.
   Why wrong: Hastings disproved the general additivity conjecture in 2009. The canonical text itself admits that and then pivots to a different open problem about single-letter formulas and classifying additive channels.
   Should be: Either keep the title and mark the conjecture `disproved`, or retitle/reframe the entry as an `open_question` about channel classes and single-letter capacity formulas.

6. `data/problems/mathematical-physics/ppt-bound-entanglement.yaml`
   Fields: `title`, `statement.canonical`, `problem_type`
   Wrong: The canonical statement asks whether every PPT entangled state is bound entangled.
   Why wrong: That part is already known: PPT entangled states are bound entangled. The open problem is the existence of `NPT` bound entangled states, which this file only mentions later. The current first sentence is mathematically stale.
   Should be: Rewrite the entry around the actual open distillability/NPT-bound-entanglement question, or merge it with `data/problems/mathematical-physics/npt-bound-entanglement-existence.yaml`.

7. `data/problems/mathematical-physics/conformal-invariance-criticality-general.yaml`
   Fields: `statement.canonical`
   Wrong: The 2D clause asks for conformal invariance of the critical `q`-state Potts model “for general `q`”.
   Why wrong: In two dimensions, the Potts model has a continuous critical point only for `q <= 4`; for `q > 4` the transition is first-order, so this is not the right conformal-invariance target.
   Should be: Restrict the 2D Potts part to the continuous-transition regime (`q <= 4`, or the appropriate FK/random-cluster formulations), and separate genuinely different higher-dimensional questions.

## Major

8. `data/problems/mathematics/borsuk-conjecture.yaml`
   Fields: `status.label`, `statement.canonical`
   Wrong: The title is still “Borsuk’s Conjecture,” but the canonical statement says the conjecture is false and then switches to the residual low-dimensional problem.
   Why wrong: The original conjecture is `disproved`, not `partially_solved`.
   Should be: Either mark Borsuk’s conjecture `disproved`, or retitle the record to the low-dimensional Borsuk problem and keep that open.

9. `data/problems/mathematics/navier-stokes-existence-and-smoothness.yaml`
   Fields: `dates.first_stated`
   Wrong: `first_stated: 1845`
   Why wrong: That is not the first formulation of the global 3D regularity problem; it is just near the historical period of the equations themselves. The open regularity/existence problem is associated with Leray-era PDE work, not 1845.
   Should be: Use `1934` if the record is about the mathematical regularity problem, or `2000` if it is explicitly the Clay Millennium formulation.

10. `data/problems/mathematics/large-cardinal-hierarchy.yaml`
   Fields: `problem_type`
   Wrong: Labeled `conjecture`.
   Why wrong: The canonical statement is a broad inner-model-theory program (“construct an inner model for a supercompact cardinal; more broadly develop inner model theory…”), not a single boolean conjecture.
   Should be: Reclassify as `open_question` or split into finer-grained conjectures/problems.

11. `data/problems/mathematics/kadison-singer-extensions.yaml`
   Fields: `problem_type`
   Wrong: Labeled `conjecture`.
   Why wrong: The statement is an open-ended family of paving questions beyond the solved Kadison-Singer problem, not a single named conjecture.
   Should be: Reclassify as `open_question`, or split into specific MASA/paving conjectures.

12. `data/problems/mathematics/deninger-program.yaml`
   Fields: `problem_type`
   Wrong: Labeled `conjecture`.
   Why wrong: The entry is explicitly a “program” and the canonical statement describes a proposed framework rather than one crisp conjecture.
   Should be: Reclassify as `open_question` or split into explicit conjectural components.

13. `data/problems/mathematics/simplex-conjecture.yaml`
   Fields: `statement.canonical`, `aliases`
   Wrong: The canonical text conflates at least three different things: the theorem that a regular simplex is optimal for `M = n+1`, the general spherical code problem for `M > n+1`, and an information-theoretic “simplex conjecture” about Gaussian channels.
   Why wrong: These are not one well-defined open problem, and the current aliases do not identify a standard single canonical problem.
   Should be: Split this into separate records or retitle it to one precise problem. As written, the canonical statement is too mixed to be mathematically clean.

14. `data/problems/mathematics/frankl-conjecture-specific-bounds.yaml`
   Fields: `problem_type`
   Wrong: Labeled `conjecture`.
   Why wrong: The canonical statement asks for the best constant `c`; that is an optimization/open-question variant, not a boolean conjecture.
   Should be: Reclassify as `open_question` and keep the relation to the main Frankl/union-closed record explicit.

15. `data/problems/theoretical-cs/quantum-interactive-proofs.yaml`
   Fields: `statement.canonical`, `problem_type`
   Wrong: The canonical statement still asks “What is the complexity of MIP*?” and labels the record as a conjecture.
   Why wrong: `MIP* = RE` is already known. The remaining content is a bundle of post-resolution follow-up questions about intermediate models and restricted variants.
   Should be: Retitle/rewrite as an `open_question` about post-`MIP* = RE` structure questions.

16. `data/problems/theoretical-cs/black-box-separations.yaml`
   Fields: `problem_type`
   Wrong: Labeled `conjecture`.
   Why wrong: The canonical statement is a research agenda (“which implications can be established non-black-box, and which are genuine impossibilities?”), not a single conjecture.
   Should be: Reclassify as `open_question`, or split into specific primitive-to-primitive implication questions.

17. `data/problems/theoretical-cs/dense-model-theorem.yaml`
   Fields: `problem_type`
   Wrong: Labeled `conjecture`.
   Why wrong: The canonical statement asks for stronger versions/parameter improvements of an already-proved theorem.
   Should be: Reclassify as `open_question`.

18. `data/problems/theoretical-cs/planarity-testing-optimal.yaml`
   Fields: `problem_type`, `aliases`, `statement.canonical`
   Wrong: The entry bundles two distinct problems: optimal parallel planarity testing and dynamic planarity testing. It also lists `Dynamic planarity testing` as an alias.
   Why wrong: Dynamic planarity is not an alias of parallel planarity testing; it is a separate problem family. The record is also not a conjecture.
   Should be: Split into separate records and reclassify as `open_question`.

19. `data/problems/theoretical-cs/union-find-optimal.yaml`
   Fields: `problem_type`
   Wrong: Labeled `conjecture`.
   Why wrong: The canonical statement explicitly says the classical bound is already tight in the classical setting and then asks about modern variants (concurrent/cache-oblivious). That is not one conjecture.
   Should be: Reclassify as `open_question`, or split by computational model.

20. `data/problems/theoretical-cs/quantum-supremacy-formal.yaml`
   Fields: `problem_type`
   Wrong: Labeled `conjecture`.
   Why wrong: The statement is “Can we formally prove…?”, i.e. an open question about unconditional `BQP` vs `BPP`, not a named conjecture.
   Should be: Reclassify as `open_question`.

21. `data/problems/mathematical-physics/mip-star-equals-re.yaml`
   Fields: `problem_type`, `statement.canonical`
   Wrong: The record is still typed as a `conjecture`, even though the canonical text itself describes “the MIP* = RE theorem” and the status is `solved`.
   Why wrong: This is no longer an open conjecture.
   Should be: Move it out of the open-problem set, or reclassify it as a resolved theorem/historical record.

22. `data/problems/mathematical-physics/quantum-channel-capacity-additivity-general.yaml`
   Fields: `problem_type`, `aliases`, `statement.canonical`
   Wrong: The record is labeled `conjecture` and still uses stale additivity-style aliases, even though the general additivity conjecture is false and the canonical statement has shifted to classifying channel families and capacity formulas.
   Should be: Reclassify as `open_question`, and rename aliases/title so they do not read like the old disproved conjecture.

23. `data/problems/mathematical-physics/quantum-reverse-shannon-theorem-extensions.yaml`
   Fields: `problem_type`
   Wrong: Labeled `conjecture`.
   Why wrong: The canonical statement is an extension program for an already-proved theorem, not a single conjecture.
   Should be: Reclassify as `open_question`.

24. `data/problems/mathematical-physics/quantum-key-distribution-optimal-rates.yaml`
   Fields: `problem_type`
   Wrong: Labeled `conjecture`.
   Why wrong: The entry asks for exact key capacities and computable formulas for different channels; that is an open question family, not a boolean conjecture.
   Should be: Reclassify as `open_question`.

25. `data/problems/mathematical-physics/lee-yang-zeros-phase-transitions.yaml`
   Fields: `problem_type`
   Wrong: Labeled `conjecture`.
   Why wrong: The canonical statement asks for extensions of the Lee-Yang theorem to broad classes of models and for a general density-of-zeros theory. That is too broad to count as one conjecture.
   Should be: Reclassify as `open_question`, or split into model-specific conjectures.

## Minor

26. `data/problems/theoretical-cs/matrix-multiplication-exponent.yaml`
   Fields: `statement.canonical`, `partial_results`
   Wrong: The canonical bound `omega < 2.372` is stale.
   Why wrong: The best published upper bound is lower than that; the record’s own `status_evidence` already points to newer work.
   Should be: Update the canonical statement and partial-results ladder to the latest bound (`omega < 2.371339` in the 2024 Alman-Xu-Xu-Zhou work).

27. `data/problems/mathematical-physics/quantum-hamiltonian-complexity-qma.yaml`
   Fields: `title`, `aliases`
   Wrong: The title is broad, but the canonical statement is specifically the quantum PCP conjecture. The alias `QMA-completeness of Local Hamiltonian` is not an alias of quantum PCP; it is a solved theorem.
   Should be: Retitle to `Quantum PCP Conjecture` (or split the record), and remove the solved-theorem alias.

28. `data/problems/mathematical-physics/self-avoiding-walk-connective-constant.yaml`
   Fields: `statement.canonical`
   Wrong: The canonical statement still says “specifically, prove” the honeycomb-lattice value of the connective constant, even though the same sentence immediately notes that this was proved by Duminil-Copin and Smirnov.
   Should be: Remove the honeycomb case from the open-problem statement and focus the record on genuinely open lattices/exponents.

# Recommendations

1. Separate `conjecture` from `open_question` aggressively.
   A practical lint rule: if the canonical statement begins with “determine”, “classify”, “extend”, “what is”, or bundles several subquestions, default away from `conjecture`.

2. Do not keep disproved/solved titles while silently pivoting the canonical text to a different live problem.
   This is the biggest source of mathematically misleading records.

3. Add a consistency check between `status.label` and `statement.canonical`.
   If `status` is `solved`/`disproved`, the statement should not read like an unresolved question. If `status` is `open`, the statement should not begin by saying the named conjecture was disproved/solved.

4. Add a date sanity check.
   `dates.first_stated` should refer to the open problem/conjecture, not to the original equation, model, or physical theory. The two Navier-Stokes/Euler entries are the clearest failures here.

5. Split mixed records.
   Several entries currently compress multiple distinct problems into one YAML: `simplex-conjecture`, `planarity-testing-optimal`, `quantum-interactive-proofs`, and several quantum-capacity entries.

6. Treat solved theorem aliases carefully.
   Aliases should name the same problem, not a solved theorem adjacent to it. The quantum PCP/local-Hamiltonian record is the clearest example.

7. Add a stale-numerics review pass.
   Fast-moving quantitative bounds such as the matrix-multiplication exponent should have automated reminders or a smaller `stale_after` window.

# Representative Verification Sources

- Beltrán and Pardo, “Smale’s 17th problem: average polynomial time to compute affine and projective solutions”, JAMS 22 (2009): https://www.ams.org/jams/2009-22-02/S0894-0347-08-00608-1/
- Abrahamsen, Adamaszek, and Miltzow, “The Art Gallery Problem is ∃R-complete” (2018): https://arxiv.org/abs/1704.06969
- Alman, Xu, Xu, and Zhou, “More Recent Advances in Matrix Multiplication” (2024 bound context): https://arxiv.org/abs/2404.16349
- Beffara and Duminil-Copin, survey noting 2D Potts is second-order for `q <= 4` and first-order for `q > 4`: https://arxiv.org/abs/0910.0351
- For several other entries, the corrective evidence is already in the YAML’s own cited sources (for example Hastings 2009 for channel additivity, Horodecki et al. 1998 for PPT bound entanglement, and Ji-Natarajan-Vidick-Wright-Yuen 2020 for `MIP* = RE`).
