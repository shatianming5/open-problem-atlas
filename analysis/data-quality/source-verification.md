---
analyzer: codex/gpt-5.4
reasoning: xhigh
date: 2026-03-07
task: source verification
scope: data/problems/
---

# Source Verification Audit

## Executive summary

- Scanned all 312 YAML files under `data/problems/` and parsed all 726 source entries.
- Source coverage is uneven: 444 DOI URLs, 47 arXiv URLs, 29 other HTTP URLs, and 206 entries with no URL at all.
- High-confidence issues are concentrated in DOI metadata and source hygiene:
  - 137 DOI-backed entries are suspicious because `doi.org`/Crossref either returned no metadata or returned a clearly different work.
  - 16 entries have `source_id` year suffixes that disagree with `source.year`.
  - 21 `source_id` values are duplicated across different files; 17 of those duplicates carry conflicting metadata.
  - 80 modern sources (1991+) have no URL, which blocks quick verification and strongly suggests bulk-added entries were not fully sourced.
- Checks that passed:
  - No dangling/non-existent `source_id` references were found. All 726 `source_id` occurrences are definitions inside `sources` blocks.
  - All 45 unique arXiv URLs in the dataset resolved successfully.
- Provenance caveat: the repository does not mark which files are the "original 50 hand-curated ones". `git log -- data/problems` shows a single initial commit for all problem YAMLs, and every file has `created_from: manual_curation`. This report therefore covers all 312 files and calls out where the suspicious entries cluster.

## Method

1. Parsed every `data/problems/**/*.yaml` file and extracted all `sources.canonical[*]` and `sources.status_evidence[*]` entries.
2. Checked local consistency for URL format, duplicate `source_id` reuse, `source_id`/`year` mismatches, and missing URLs.
3. Verified DOI-backed entries against `doi.org` content negotiation and Crossref metadata.
4. Verified that every unique arXiv URL resolves.
5. Consolidated findings into unique suspicious source entries; some entries trigger multiple issue classes.

## Statistics

| Metric | Count | Share |
| --- | ---: | ---: |
| YAML files scanned | 312 | 100.0% |
| Source entries scanned | 726 | 100.0% |
| DOI URLs | 444 | 61.2% |
| arXiv URLs | 47 | 6.5% |
| Other HTTP URLs | 29 | 4.0% |
| Missing URL | 206 | 28.4% |
| Modern entries missing URL (>=1991) | 80 | 11.0% of all sources |
| High-confidence DOI issues | 137 | 18.9% of all sources / 30.9% of DOI sources |
| Duplicated `source_id` occurrences | 42 | 5.8% |
| Distinct duplicated `source_id` values | 21 | 3.0% |
| `source_id`/`year` mismatches | 16 | 2.2% |
| Unique suspicious source entries (union of all checks) | 264 | 36.4% |

## Duplicate `source_id` summary

- `src_aharonov_naveh_2002`: duplicated across 2 files with identical metadata. Occurrences: data/problems/theoretical-cs/qma-vs-qcma.yaml (2002): Quantum NP - A Survey; data/problems/theoretical-cs/quantum-pcp-conjecture.yaml (2002): Quantum NP - A Survey
- `src_aizenman_warzel_2015`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematical-physics/anderson-metal-insulator-transition.yaml (2015): Random Operators: Disorder Effects on Quantum Spectra and Dynamics; data/problems/mathematics/random-schrodinger-operator-localization.yaml (2015): Random Operators: Disorder Effects on Quantum Spectra and Dynamics
- `src_anderson_1958`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematical-physics/anderson-metal-insulator-transition.yaml (1958): Absence of Diffusion in Certain Random Lattices; data/problems/mathematics/random-schrodinger-operator-localization.yaml (1958): Absence of Diffusion in Certain Random Lattices
- `src_arora_barak_2009`: duplicated across 2 files with identical metadata. Occurrences: data/problems/theoretical-cs/l-vs-p.yaml (2009): Computational Complexity: A Modern Approach; data/problems/theoretical-cs/p-vs-pspace.yaml (2009): Computational Complexity: A Modern Approach
- `src_bernstein_vazirani_1997`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/theoretical-cs/bqp-vs-np.yaml (1997): Quantum Complexity Theory; data/problems/theoretical-cs/quantum-supremacy-formal.yaml (1997): Quantum Complexity Theory
- `src_christodoulou_1999`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematical-physics/cosmic-censorship-conjecture.yaml (1999): On the global initial value problem and the issue of singularities; data/problems/mathematics/strong-cosmic-censorship-conjecture.yaml (1999): The instability of naked singularities in the gravitational collapse of a scalar field
- `src_gharibian_2015`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematical-physics/quantum-hamiltonian-complexity-qma.yaml (2015): Quantum Hamiltonian Complexity; data/problems/theoretical-cs/quantum-pcp-conjecture.yaml (2015): Quantum Hamiltonian Complexity
- `src_gilmer_2022`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematics/frankl-conjecture-specific-bounds.yaml (2022): A constant lower bound for the union-closed sets conjecture; data/problems/mathematics/union-closed-sets-conjecture.yaml (2022): A constant lower bound for the union-closed sets conjecture
- `src_guy_2004`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematics/gilbreaths-conjecture.yaml (2004): Unsolved Problems in Number Theory; data/problems/mathematics/goldbach-conjecture.yaml (2004): Unsolved Problems in Number Theory
- `src_hastings_2009`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematical-physics/additivity-conjecture-quantum-channel-capacity.yaml (2009): Superadditivity of communication capacity using entangled inputs; data/problems/mathematical-physics/quantum-channel-capacity-additivity-general.yaml (2009): Superadditivity of communication capacity using entangled inputs
- `src_horodecki_review_2009`: duplicated across 2 files with identical metadata. Occurrences: data/problems/mathematical-physics/entanglement-distillation-optimal-rates.yaml (2009): Quantum entanglement; data/problems/mathematical-physics/ppt-bound-entanglement.yaml (2009): Quantum entanglement
- `src_impagliazzo_wigderson_1997`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/theoretical-cs/bpp-vs-p.yaml (1997): P = BPP if E Requires Exponential Circuits: Derandomizing the XOR Lemma; data/problems/theoretical-cs/derandomization-p-bpp.yaml (1997): P = BPP if E requires exponential circuits: Derandomizing the XOR lemma
- `src_jaffe_witten_2000`: duplicated across 2 files with identical metadata. Occurrences: data/problems/mathematical-physics/mass-gap-non-abelian-gauge-theories.yaml (2000): Quantum Yang-Mills Theory; data/problems/mathematical-physics/yang-mills-existence-and-mass-gap.yaml (2000): Quantum Yang-Mills Theory
- `src_kerr_1963`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematical-physics/final-state-conjecture-general-relativity.yaml (1963): Gravitational Field of a Spinning Mass as an Example of Algebraically Special Metrics; data/problems/mathematical-physics/stability-of-kerr-solution.yaml (1963): Gravitational Field of a Spinning Mass as an Example of Algebraically Special Metrics
- `src_khot_2002`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematical-physics/quantum-unique-games-conjecture.yaml (2002): On the power of unique 2-prover 1-round games; data/problems/theoretical-cs/unique-games-conjecture.yaml (2002): On the Power of Unique 2-Prover 1-Round Games
- `src_matousek_2002`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematics/lattice-distortion-conjecture.yaml (2002): Lectures on Discrete Geometry; data/problems/theoretical-cs/range-searching-lower-bounds.yaml (2002): Lectures on Discrete Geometry
- `src_nisan_wigderson_1994`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/theoretical-cs/bpp-vs-p.yaml (1994): Hardness vs Randomness; data/problems/theoretical-cs/nisan-wigderson-hypothesis.yaml (1994): Hardness vs Randomness
- `src_savitch_1970`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/theoretical-cs/l-vs-nl.yaml (1970): Relationships between nondeterministic and deterministic tape complexities; data/problems/theoretical-cs/p-vs-pspace.yaml (1970): Relationships Between Nondeterministic and Deterministic Tape Complexities
- `src_smale_1998`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematics/smale-17th-problem.yaml (1998): Mathematical Problems for the Next Century; data/problems/theoretical-cs/strongly-polynomial-lp.yaml (1998): Mathematical Problems for the Next Century
- `src_wilde_2017`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematical-physics/additivity-conjecture-quantum-channel-capacity.yaml (2017): Quantum Information Theory (2nd ed.); data/problems/mathematical-physics/quantum-shannon-capacity-regions.yaml (2017): Quantum Information Theory (2nd edition)
- `src_woodin_2017`: duplicated across 2 files with conflicting metadata. Occurrences: data/problems/mathematics/large-cardinal-hierarchy.yaml (2017): In search of Ultimate-L: the 19th Midrasha Mathematicae lectures; data/problems/mathematics/woodins-ultimate-l-conjecture.yaml (2017): In search of Ultimate-L: the 19th Midrasha Mathematicae Lectures

## All suspicious sources found

The list below is the union of all suspicious entries found by the audit. An entry appears here if it had a high-confidence DOI problem, a `source_id`/`year` mismatch, modern missing URL, and/or duplicate `source_id` reuse.

- `data/problems/mathematical-physics/3d-ising-model-phase-transition.yaml` `src_duminil_copin_2020`: 100 years of the (critical) Ising model on the hypercubic lattice. source_id encodes year 2020 but source.year is 2022
- `data/problems/mathematical-physics/additivity-conjecture-quantum-channel-capacity.yaml` `src_hastings_2009`: Superadditivity of communication capacity using entangled inputs. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematical-physics/additivity-conjecture-quantum-channel-capacity.yaml` `src_wilde_2017`: Quantum Information Theory (2nd ed.). modern source (>=1991) has no URL, which blocks verification; source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematical-physics/agt-correspondence-proof.yaml` `src_tachikawa_2015`: A brief review of the 2d/4d correspondences. DOI resolves to a likely different work (title score 0.283); resolver returned 'Quantum Hall Effect, Bosonization and Chiral Actions in Higher Dimensions'; source_id encodes year 2015 but source.year is 2013
- `data/problems/mathematical-physics/anderson-metal-insulator-transition.yaml` `src_aizenman_warzel_2015`: Random Operators: Disorder Effects on Quantum Spectra and Dynamics. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematical-physics/anderson-metal-insulator-transition.yaml` `src_anderson_1958`: Absence of Diffusion in Certain Random Lattices. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematical-physics/bkl-conjecture-singularity-structure.yaml` `src_bkl_1970`: Oscillatory approach to a singular point in the relativistic cosmology. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematical-physics/conformal-invariance-criticality-general.yaml` `src_polyakov_1970`: Conformal symmetry of critical fluctuations. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematical-physics/constructive-qft-4d.yaml` `src_rivasseau_2000`: Constructive Field Theory and Applications. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematical-physics/cosmic-censorship-conjecture.yaml` `src_christodoulou_1999`: On the global initial value problem and the issue of singularities. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematical-physics/entanglement-distillation-optimal-rates.yaml` `src_horodecki_review_2009`: Quantum entanglement. source_id duplicated across 2 files with identical metadata
- `data/problems/mathematical-physics/final-state-conjecture-general-relativity.yaml` `src_kerr_1963`: Gravitational Field of a Spinning Mass as an Example of Algebraically Special Metrics. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematical-physics/fractional-quantum-hall-classification.yaml` `src_wen_2017`: Quantum Field Theory of Many-body Systems. modern source (>=1991) has no URL, which blocks verification; source_id encodes year 2017 but source.year is 2004
- `data/problems/mathematical-physics/haags-theorem-implications.yaml` `src_haag_1955`: On quantum field theories. DOI resolves to a likely different work (title score 0.240); resolver returned 'Percutaneous transcatheter ethanol sclerotheraphy of postoperative pelvic lymphoceles'
- `data/problems/mathematical-physics/mass-gap-non-abelian-gauge-theories.yaml` `src_jaffe_witten_2000`: Quantum Yang-Mills Theory. source_id duplicated across 2 files with identical metadata
- `data/problems/mathematical-physics/mass-gap-non-abelian-gauge-theories.yaml` `src_teper_2009`: Large N and the Lattice. DOI resolves to a likely different work (title score 0.238); resolver returned 'Exploring Excited Hadrons'
- `data/problems/mathematical-physics/mip-star-equals-re.yaml` `src_vidick_2020_notices`: From Operator Algebras to Complexity Theory and Back. source_id encodes year 2020 but source.year is 2024
- `data/problems/mathematical-physics/percolation-threshold-exact-values.yaml` `src_broadbent_1957`: Percolation processes I. Crystals and mazes. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematical-physics/ppt-bound-entanglement.yaml` `src_horodecki_review_2009`: Quantum entanglement. source_id duplicated across 2 files with identical metadata
- `data/problems/mathematical-physics/quantum-channel-capacity-additivity-general.yaml` `src_hastings_2009`: Superadditivity of communication capacity using entangled inputs. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematical-physics/quantum-channel-capacity-additivity-general.yaml` `src_holevo_2012`: Quantum Systems, Channels, Information. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematical-physics/quantum-fault-tolerance-threshold-exact.yaml` `src_gottesman_2014`: Fault-Tolerant Quantum Computation. source_id encodes year 2014 but source.year is 2016
- `data/problems/mathematical-physics/quantum-hamiltonian-complexity-qma.yaml` `src_gharibian_2015`: Quantum Hamiltonian Complexity. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematical-physics/quantum-shannon-capacity-regions.yaml` `src_wilde_2017`: Quantum Information Theory (2nd edition). source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematical-physics/quantum-unique-games-conjecture.yaml` `src_khot_2002`: On the power of unique 2-prover 1-round games. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematical-physics/random-matrix-universality.yaml` `src_mehta_2004`: Random Matrices (3rd edition). modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematical-physics/stability-of-kerr-solution.yaml` `src_kerr_1963`: Gravitational Field of a Spinning Mass as an Example of Algebraically Special Metrics. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematical-physics/wittens-conjecture-3-manifold-invariants.yaml` `src_freed_2009`: Remarks on Chern-Simons Theory. DOI resolves to a clearly different work (title score 0.000); resolver returned ''
- `data/problems/mathematical-physics/yang-mills-existence-and-mass-gap.yaml` `src_douglas_2004`: Report on the Status of the Yang-Mills Millennium Prize Problem. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematical-physics/yang-mills-existence-and-mass-gap.yaml` `src_jaffe_witten_2000`: Quantum Yang-Mills Theory. source_id duplicated across 2 files with identical metadata
- `data/problems/mathematics/abundance-conjecture.yaml` `src_lazarsfeld_2004`: Positivity in Algebraic Geometry. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/agoh-giuga-conjecture.yaml` `src_agoh_1995`: On Giuga's conjecture. DOI resolves to a likely different work (title score 0.224); resolver returned 'On products in a family of cohomology theories associated to the invariant prime ideals of π*(BP)(BP)'
- `data/problems/mathematics/agoh-giuga-conjecture.yaml` `src_borwein_borwein_borwein_girgensohn_2005`: Giuga's Conjecture on Primality. DOI resolves to a likely different work (title score 0.262); resolver returned 'Differentiating Powers of an Old Friend'; source_id encodes year 2005 but source.year is 1996
- `data/problems/mathematics/agoh-giuga-conjecture.yaml` `src_giuga_1950`: Su una presumibile proprietà caratteristica dei numeri primi. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/albertson-conjecture.yaml` `src_albertson_2007`: Crossing numbers and chromatic numbers. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/albertson-conjecture.yaml` `src_albertson_2008`: Chromatic number, independence ratio, and crossing number. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/andrews-curtis-conjecture.yaml` `src_andrews_curtis_1965`: Free groups and handlebodies. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/andrews-curtis-conjecture.yaml` `src_borovik_lubotzky_myasnikov_2005`: The Andrews-Curtis conjecture and black box groups. DOI resolves to a clearly different work (title score 0.186); resolver returned 'RESTRICTING COHOMOLOGICAL REPRESENTATIONS OF <font>SO</font><sub>0</sub>(n,1) AND <font>SU</font>(n,1)'
- `data/problems/mathematics/bass-conjecture.yaml` `src_bass_1976`: Euler characteristics and characters of discrete groups. DOI resolves to different title/authors (title score 0.429); resolver returned 'Irreducible representations of finite classical groups'
- `data/problems/mathematics/bass-conjecture.yaml` `src_eckmann_2001`: Idempotents in a complex group algebra, projective modules, and the von Neumann algebra. DOI resolves to a likely different work (title score 0.279); resolver returned 'Algebraic independence of elements from $ \mathbb{C}_p $ over $ \mathbb{Q}_p $ , I'
- `data/problems/mathematics/bateman-horn-conjecture.yaml` `src_sander_2009`: On the Bateman-Horn conjecture. DOI resolves to a clearly different work (title score 0.149); resolver returned 'A generalization of a modular identity of Rogers'
- `data/problems/mathematics/baum-connes-conjecture.yaml` `src_baum_connes_higson_1994`: Classifying space for proper actions and K-theory of group C*-algebras. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/bellman-lost-in-forest.yaml` `src_finch_wetzel_2004`: Lost in a Forest. DOI resolves to a likely different work (title score 0.267); resolver returned 'Another Proof That ℝ 3 Has No Square Root'
- `data/problems/mathematics/birch-swinnerton-dyer-conjecture.yaml` `src_coates_2005`: The conjecture of Birch and Swinnerton-Dyer. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/birch-swinnerton-dyer-conjecture.yaml` `src_wiles_2000`: The Birch and Swinnerton-Dyer Conjecture (Millennium Prize Problem description). source_id encodes year 2000 but source.year is 2006
- `data/problems/mathematics/birman-conjecture-braids.yaml` `src_birman_1969`: Braids, Links, and Mapping Class Groups. source_id encodes year 1969 but source.year is 1975
- `data/problems/mathematics/birman-conjecture-braids.yaml` `src_margalit_2019`: Braid groups and mapping class groups: new directions. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/brennan-conjecture.yaml` `src_hedenmalm_shimorin_2005`: Weighted Bergman spaces and the integral means spectrum of conformal mappings. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/brocards-problem.yaml` `src_berndt_galway_2000`: On the Brocard-Ramanujan Diophantine equation n! + 1 = m^2. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/brocards-problem.yaml` `src_guy_2004_brocard`: Unsolved Problems in Number Theory. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/burnside-problem-bounded-exponent.yaml` `src_adian_2015`: New results on the Burnside problem. DOI resolves to a clearly different work (title score 0.000); resolver returned 'Единый подход к построению определяющих форм для двумерной системы уравнений Навье - Стокса: случай общих интерполирующих операторов'
- `data/problems/mathematics/caccetta-haggkvist-conjecture.yaml` `src_hladky_etal_2017`: On the Caccetta-Haggkvist conjecture with a forbidden transversal. DOI resolves to a likely different work (title score 0.270); resolver returned 'Properly colored and rainbow copies of graphs with few cherries'
- `data/problems/mathematics/carleson-coefficients-conjecture.yaml` `src_bourgain_2014`: On the Hardy-Littlewood maximal function for the cube. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/casas-alvero-conjecture.yaml` `src_casas_alvero_2001`: Higher order polar germs. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/casas-alvero-conjecture.yaml` `src_graf_2014`: The Casas-Alvero conjecture for infinitely many degrees. DOI resolves to different title/authors (title score 0.385); resolver returned 'On intersections of orbital varieties and components of Springer fiber'; source_id encodes year 2014 but source.year is 2006
- `data/problems/mathematics/cerny-conjecture.yaml` `src_volkov_2008`: Synchronizing Automata and the Černý Conjecture. DOI resolves to different title/authors (title score 0.364); resolver returned 'Various Aspects of Finite Quantum Automata'
- `data/problems/mathematics/cherlin-zilber-conjecture.yaml` `src_borovik_2008`: Simple Groups of Finite Morley Rank. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/chromatic-splitting-conjecture.yaml` `src_beaudry_2017`: The chromatic splitting conjecture at n = p = 2. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/chromatic-splitting-conjecture.yaml` `src_hovey_1995`: Bousfield localization functors and Hopkins' chromatic splitting conjecture. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/combinatorial-hodge-conjecture.yaml` `src_mikhalkin_2014`: Tropical Hodge conjecture. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/cramers-conjecture.yaml` `src_pintz_2007`: Cramer vs. Cramer: On Cramer's probabilistic model for primes. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/deninger-program.yaml` `src_deninger_1992`: On the Gamma-factors attached to motives. DOI resolves to a likely different work (title score 0.257); resolver returned 'The extension of Johnson's homomorphism from the Torelli group to the mapping class group'
- `data/problems/mathematics/deninger-program.yaml` `src_deninger_2002`: A note on arithmetic topology and dynamical systems. DOI resolves to a likely different work (title score 0.224); resolver returned 'Local Leopoldt’s problem for ideals in totally ramified 𝑝-extensions of complete discrete valuation fields'
- `data/problems/mathematics/density-hales-jewett-polynomial.yaml` `src_polymath_2010_blog`: A new proof of the density Hales-Jewett theorem. source_id encodes year 2010 but source.year is 2012
- `data/problems/mathematics/dixmier-problem.yaml` `src_pisier_2005`: Are unitarizable groups amenable?. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/dowling-wilson-conjecture.yaml` `src_dowling_wilson_1975`: Whitney number inequalities for geometric lattices. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/elliott-classification-conjecture.yaml` `src_elliott_1993`: On the classification of inductive limits of sequences of semisimple finite-dimensional algebras. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/elliott-classification-conjecture.yaml` `src_tikuisis_white_winter_2017`: Quasidiagonality of nuclear C*-algebras. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/entropy-power-inequality-extensions.yaml` `src_bobkov_chistyakov_2015`: Entropy power inequality for the Rényi entropy. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/erdos-gyarfas-conjecture.yaml` `src_erdos_gyarfas_1997`: A variant of the classical Ramsey problem. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/erdos-hajnal-conjecture.yaml` `src_chudnovsky_2014`: The Erdos-Hajnal conjecture -- a survey. DOI resolves to a likely different work (title score 0.207); resolver returned 'Sub-exponentially many 3-colorings of triangle-free planar graphs'
- `data/problems/mathematics/erdos-mollin-walsh-conjecture.yaml` `src_mollin_walsh_1986`: On powerful numbers. DOI resolves to a likely different work (title score 0.258); resolver returned 'The semigroup of nonempty finite subsets of integers'
- `data/problems/mathematics/erdos-sos-conjecture.yaml` `src_ajtai_etal_2009`: The Erdos-Sos conjecture for trees of large size. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/fatou-conjecture.yaml` `src_mcmullen_1994`: Complex Dynamics and Renormalization. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/frankl-conjecture-specific-bounds.yaml` `src_gilmer_2022`: A constant lower bound for the union-closed sets conjecture. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematics/freiman-ruzsa-conjecture.yaml` `src_ruzsa_1999`: An analog of Freiman's theorem in groups. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/furstenberg-x2-x3-conjecture.yaml` `src_lindenstrauss_2007`: Invariant measures and arithmetic quantum unique ergodicity. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/gilbreaths-conjecture.yaml` `src_guy_2004`: Unsolved Problems in Number Theory. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematics/global-regularity-supercritical-sqs.yaml` `src_kiselev_2010`: Nonlocal maximum principles for active scalars. DOI resolves to different title/authors (title score 0.319); resolver returned 'A weak energy identity and the length of necks for a sequence of Sacks–Uhlenbeck α-harmonic maps'
- `data/problems/mathematics/goldbach-conjecture.yaml` `src_guy_2004`: Unsolved Problems in Number Theory. modern source (>=1991) has no URL, which blocks verification; source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematics/graceful-tree-conjecture.yaml` `src_gallian_survey_status`: A dynamic survey of graph labeling. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/grimms-conjecture.yaml` `src_erdos_pomerance_1978`: Matching the natural numbers up to n with distinct multiples in another interval. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/grimms-conjecture.yaml` `src_grimm_1969`: A conjecture on consecutive composite numbers. DOI resolves to a clearly different work (title score 0.000); resolver returned '5724'
- `data/problems/mathematics/gyarfas-sumner-conjecture.yaml` `src_scott_seymour_2020`: A survey of chi-boundedness. DOI resolves to a likely different work (title score 0.206); resolver returned 'The (theta, wheel)-free graphs Part II: Structure theorem'
- `data/problems/mathematics/hadamard-conjecture.yaml` `src_djokovic_2008`: Hadamard matrices of small order. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/hadamard-conjecture.yaml` `src_horadam_2007`: Hadamard Matrices and Their Applications. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/hadwiger-conjecture.yaml` `src_norin_song_2019`: Breaking the degeneracy barrier for coloring graphs with no K_t minor. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/hadwiger-nelson-problem.yaml` `src_soifer_2009`: The Mathematical Coloring Book. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/halls-conjecture.yaml` `src_elkies_2007`: Rational points near curves and small nonzero |x^3 - y^2| via lattice reduction. DOI resolves to a clearly different work (title score 0.168); resolver returned 'Abelian Varieties with Prescribed Embedding Degree'
- `data/problems/mathematics/halls-conjecture.yaml` `src_hall_1971`: The Diophantine equation x^3 - y^2 = k. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/halpern-lauchli-partition-conjecture.yaml` `src_dobrinen_2017`: Halpern-Lauchli theorem at a measurable cardinal. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/happel-conjecture.yaml` `src_happel_1991`: On the derived category of a finite-dimensional algebra. DOI resolves to different title/authors (title score 0.327); resolver returned 'Dual-standard subgroups of finite and locally finite groups'
- `data/problems/mathematics/happel-conjecture.yaml` `src_happel_2001`: A characterization of hereditary categories with tilting object. DOI resolves to a clearly different work (title score 0.177); resolver returned 'Continuous family of invariant subspaces for R-diagonal operators'
- `data/problems/mathematics/hilbert-16th-problem-second-part.yaml` `src_ilyashenko_2002`: Centennial history of Hilbert's 16th problem. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/hopf-conjecture-positive-curvature.yaml` `src_ziller_2014`: Riemannian manifolds with positive sectional curvature. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/hot-spots-conjecture.yaml` `src_steinerberger_2021`: Hot Spots in Convex Domains are in the Tips of the Boundary. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/invariant-subspace-problem.yaml` `src_enflo_1987`: On the invariant subspace problem for Banach spaces. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/inverse-galois-problem.yaml` `src_malle_matzat_1999`: Inverse Galois Theory. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/inverse-galois-problem.yaml` `src_serre_2008`: Topics in Galois Theory. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/iwasawa-main-conjecture-nonabelian.yaml` `src_coates_fukaya_kato_sujatha_2005`: The GL_2 main conjecture for elliptic curves without complex multiplication. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/iwasawa-main-conjecture-nonabelian.yaml` `src_kakde_2013`: The main conjecture of Iwasawa theory for totally real fields. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/jacobian-conjecture.yaml` `src_van_den_essen_2000`: Polynomial Automorphisms and the Jacobian Conjecture. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/jakobson-conjecture.yaml` `src_palis_2005`: A global perspective for non-conservative dynamics. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/kadison-similarity-problem.yaml` `src_pisier_2001`: Similarity Problems and Completely Bounded Maps. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/kadison-singer-extensions.yaml` `src_casazza_tremain_2016`: Consequences of the Marcus/Spielman/Srivastava solution of the Kadison-Singer problem. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/kadison-singer-extensions.yaml` `src_marcus_spielman_srivastava_2015`: Interlacing families II: Mixed characteristic polynomials and the Kadison-Singer problem. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/kakeya-conjecture.yaml` `src_katz_tao_2002`: New bounds for Kakeya problems. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/kalai-conjecture-noise-sensitivity.yaml` `src_bks_1999`: Noise sensitivity of Boolean functions and applications to percolation. DOI resolves to a clearly different work (title score 0.146); resolver returned 'Die Begutachtung des Meniskusschadens'
- `data/problems/mathematics/keating-snaith-conjecture.yaml` `src_cfkrs_2005`: Integral moments of L-functions. DOI resolves to different title/authors (title score 0.341); resolver returned 'Scattering theory on SL(3)/SO(3): Connections with quantum 3-body scattering'
- `data/problems/mathematics/kervaire-invariant-problem.yaml` `src_kervaire_1960`: A manifold which does not admit any differentiable structure. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/khintchine-flatness-conjecture.yaml` `src_banaszczyk_1996`: Inequalities for convex bodies and polar reciprocal lattices in R^n. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/kontsevich-zagier-conjecture.yaml` `src_kontsevich_zagier_2001`: Periods. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/kothe-conjecture.yaml` `src_krempa_1997`: Logical connections between some open problems concerning nil rings. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/kothe-conjecture.yaml` `src_smoktunowicz_2006`: Some results in noncommutative ring theory. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/lang-conjecture-rational-points.yaml` `src_hindry_silverman_2000`: Diophantine Geometry: An Introduction. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/large-cardinal-hierarchy.yaml` `src_sargsyan_2015`: Hod Mice and the Mouse Set Conjecture. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/large-cardinal-hierarchy.yaml` `src_woodin_2017`: In search of Ultimate-L: the 19th Midrasha Mathematicae lectures. DOI resolves to different title/authors (title score 0.333); resolver returned 'INTUITIONISTIC ANALYSIS AT THE END OF TIME'; source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematics/lattice-distortion-conjecture.yaml` `src_linial_london_rabinovich_1995`: The geometry of graphs and some of its algorithmic applications. DOI resolves to a likely different work (title score 0.229); resolver returned 'Crossing families'
- `data/problems/mathematics/lattice-distortion-conjecture.yaml` `src_matousek_2002`: Lectures on Discrete Geometry. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematics/lebesgue-universal-covering-problem.yaml` `src_brass_moser_pach_2005`: Research Problems in Discrete Geometry. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/legendres-conjecture.yaml` `src_guy_2004_legendre`: Unsolved Problems in Number Theory. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/lehmer-conjecture.yaml` `src_smyth_2008`: The Mahler measure of algebraic numbers: a survey. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/lehmers-totient-problem.yaml` `src_banks_luca_2012`: Composite integers n for which φ(n) | n − 1. DOI resolves to a likely different work (title score 0.298); resolver returned 'Complete asymptotic expansions for certain multiple q-integrals and q-differentials of Thomae–Jackson type'
- `data/problems/mathematics/leray-conjecture.yaml` `src_nrs_1996`: On Leray's self-similar solutions of the Navier-Stokes equations. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/list-coloring-conjecture.yaml` `src_galvin_1995`: The list chromatic index of a bipartite multigraph. DOI resolves to a likely different work (title score 0.247); resolver returned 'Extremal Graphs for Intersecting Triangles'
- `data/problems/mathematics/list-coloring-conjecture.yaml` `src_kahn_2000`: Asymptotics of the list chromatic index for multigraphs. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/matrix-mortality-problem.yaml` `src_halava_harju_2001`: Mortality in matrix semigroups. DOI resolves to a likely different work (title score 0.200); resolver returned 'First order theories for nonmonotone inductive definitions: recursively inaccessible and Mahlo'
- `data/problems/mathematics/matrix-mortality-problem.yaml` `src_paterson_1970`: Unsolvability in 3x3 matrices. DOI resolves to a clearly different work (title score 0.175); resolver returned 'Keine Kontingenten Identitäten in Lemmons Modaler Mengenlehre'
- `data/problems/mathematics/mlc-conjecture.yaml` `src_milnor_2000`: Dynamics in One Complex Variable. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/moving-sofa-problem.yaml` `src_gerver_1992`: On moving a sofa around a corner. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/n-squared-plus-one-prime-conjecture.yaml` `src_iwaniec_1978`: Almost-primes represented by quadratic polynomials. DOI resolves to a likely different work (title score 0.216); resolver returned 'The Milnor number and deformations of complex curve singularities'
- `data/problems/mathematics/navier-stokes-existence-and-smoothness.yaml` `src_robinson_2016`: The Three-Dimensional Navier-Stokes Equations. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/neggers-stanley-conjecture.yaml` `src_branden_2004`: Counterexamples to the Neggers-Stanley conjecture. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/neggers-stanley-conjecture.yaml` `src_stanley_1986`: Two poset polytopes. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/novikov-conjecture.yaml` `src_kasparov_1988`: Equivariant KK-theory and the Novikov conjecture. DOI resolves to a clearly different work (title score 0.179); resolver returned 'Heegner points and derivatives ofL-series'
- `data/problems/mathematics/overfull-conjecture.yaml` `src_mcdonald_2013`: Edge-colorings. DOI resolves to a clearly different work (title score 0.138); resolver returned 'Graphs on Surfaces'
- `data/problems/mathematics/ramsey-number-r55.yaml` `src_angeltveit_mckay_2017`: R(5,5) <= 48. DOI resolves to a clearly different work (title score 0.039); resolver returned 'The decycling number and maximum genus of cubic graphs'
- `data/problems/mathematics/random-schrodinger-operator-localization.yaml` `src_aizenman_warzel_2015`: Random Operators: Disorder Effects on Quantum Spectra and Dynamics. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematics/random-schrodinger-operator-localization.yaml` `src_anderson_1958`: Absence of Diffusion in Certain Random Lattices. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematics/reconstruction-conjecture.yaml` `src_bondy_1991`: A graph reconstructor's manual. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/resolution-of-singularities-positive-characteristic.yaml` `src_hauser_2010`: On the problem of resolution of singularities in positive characteristic. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/rotas-basis-conjecture.yaml` `src_geelen_webb_2007`: On Rota's basis conjecture. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/rotas-basis-conjecture.yaml` `src_huang_rota_1994`: On the relations of various conjectures on Latin squares and straightening coefficients. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/sarnak-conjecture.yaml` `src_ferenczi_kulaga_2018`: Sarnak's conjecture: what's new. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/sarnak-conjecture.yaml` `src_sarnak_2010`: Three lectures on the Mobius function, randomness, and dynamics. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/sato-tate-generalizations.yaml` `src_serre_2012`: Lectures on N_X(p). DOI resolves to different title/authors (title score 0.343); resolver returned 'Unleashing the Power of 3P'
- `data/problems/mathematics/schanuel-conjecture.yaml` `src_lang_1966`: Introduction to Transcendental Numbers. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/schinzel-hypothesis-h.yaml` `src_schinzel_2005`: Selecta. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/scholz-conjecture.yaml` `src_scholz_1937`: Aufgabe 253. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/selberg-eigenvalue-conjecture.yaml` `src_kim_sarnak_2003`: Refined estimates towards the Ramanujan and Selberg conjectures. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/sendov-conjecture.yaml` `src_tao_2022`: Sendov's conjecture for sufficiently-high-degree polynomials. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/seymours-second-neighborhood-conjecture.yaml` `src_cohn_2023`: Seymour's second neighborhood conjecture for tournaments. DOI resolves to a likely different work (title score 0.256); resolver returned 'The mod k $k$ chromatic index of random graphs'
- `data/problems/mathematics/seymours-second-neighborhood-conjecture.yaml` `src_dean_latka_1995`: Squaring the tournament -- an open problem. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/shelah-categoricity-conjecture.yaml` `src_grossberg_2002`: Classification theory for abstract elementary classes. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/shelah-categoricity-conjecture.yaml` `src_shelah_1999`: Classification Theory for Abstract Elementary Classes. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/sierpinski-problem.yaml` `src_sierpinski_1960`: Sur un problème concernant les nombres k * 2^n + 1. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/simplex-conjecture.yaml` `src_rankin_1955`: The closest packing of spherical caps in n dimensions. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/singmasters-conjecture.yaml` `src_kane_2007`: Singmaster's conjecture revisited. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/slice-ribbon-conjecture.yaml` `src_gompf_scharlemann_2010`: Fibered knots and potential counterexamples to the Property 2R and Slice-Ribbon Conjectures. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/smale-17th-problem.yaml` `src_beltrán_pardo_2011`: Fast linear homotopy to find approximate zeros of polynomial systems. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/smale-17th-problem.yaml` `src_smale_1998`: Mathematical Problems for the Next Century. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematics/smooth-4d-poincare-conjecture.yaml` `src_kirby_1997`: Problems in low-dimensional topology. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/smooth-4d-poincare-conjecture.yaml` `src_scorpan_2005`: The Wild World of 4-Manifolds. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/strong-cosmic-censorship-conjecture.yaml` `src_christodoulou_1999`: The instability of naked singularities in the gravitational collapse of a scalar field. DOI did not return metadata via doi.org or Crossref; source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematics/tight-closure-localization-conjecture.yaml` `src_hochster_2007`: Tight closure theory and characteristic p methods. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/total-coloring-conjecture.yaml` `src_molloy_reed_1998`: A bound on the total chromatic number. DOI resolves to different title/authors (title score 0.324); resolver returned 'Quick Approximation to Matrices and Applications'
- `data/problems/mathematics/turan-brick-factory-problem.yaml` `src_devos_2019`: Crossing numbers of graphs. DOI resolves to a clearly different work (title score 0.182); resolver returned 'Handbook of Discrete and Computational Geometry, Third Edition'
- `data/problems/mathematics/ungar-conjecture.yaml` `src_pach_sharir_2009`: Combinatorial Geometry and Its Algorithmic Applications. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/union-closed-sets-conjecture.yaml` `src_gilmer_2022`: A constant lower bound for the union-closed sets conjecture. source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematics/unitary-dual-problem.yaml` `src_adams_vogan_2020`: Atlas of Lie Groups project and the unitary dual. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/vaughts-conjecture.yaml` `src_marker_2002`: Model Theory: An Introduction. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/vaughts-conjecture.yaml` `src_steel_vaught`: On Vaught's conjecture. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/volume-conjecture.yaml` `src_kashaev_1997`: The hyperbolic volume of knots from the quantum dilogarithm. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/volume-conjecture.yaml` `src_murakami_2011`: An Introduction to the Volume Conjecture. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/volume-conjecture.yaml` `src_murakami_murakami_2001`: The colored Jones polynomials and the simplicial volume of a knot. DOI did not return metadata via doi.org or Crossref
- `data/problems/mathematics/warings-problem-exact.yaml` `src_hilbert_1909`: Beweis für die Darstellbarkeit der ganzen Zahlen durch eine feste Anzahl n-ter Potenzen. DOI resolves to a likely different work (title score 0.280); resolver returned 'Effect of mouse genotype on interferon production. I. Lines congenic at theIf-1 locus'
- `data/problems/mathematics/warings-problem-exact.yaml` `src_vaughan_wooley_2002`: Waring's problem: a survey. DOI resolves to a clearly different work (title score 0.197); resolver returned 'General homogeneous equations: Birch's theorem'
- `data/problems/mathematics/wegner-conjecture.yaml` `src_peeters_1991`: On coloring j-unit sphere graphs. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/weinstein-conjecture.yaml` `src_taubes_2007`: The Seiberg-Witten equations and the Weinstein conjecture. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/weiss-conjecture-admissibility.yaml` `src_jacob_partington_2001`: Admissibility of control and observation operators for semigroups: a survey. DOI resolves to a clearly different work (title score 0.144); resolver returned 'Some remarks on spherical isometries'
- `data/problems/mathematics/woodins-ultimate-l-conjecture.yaml` `src_woodin_2010`: Suitable extender models I. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/woodins-ultimate-l-conjecture.yaml` `src_woodin_2017`: In search of Ultimate-L: the 19th Midrasha Mathematicae Lectures. modern source (>=1991) has no URL, which blocks verification; source_id reused across 2 files with 2 metadata variants
- `data/problems/mathematics/yau-first-eigenvalue-conjecture.yaml` `src_choe_soret_2006`: First eigenvalue of symmetric minimal surfaces in S^3. modern source (>=1991) has no URL, which blocks verification
- `data/problems/mathematics/zimmer-conjecture.yaml` `src_brown_fisher_hurtado_2022`: Zimmer's conjecture for actions of SL(m,Z). modern source (>=1991) has no URL, which blocks verification
- `data/problems/theoretical-cs/3sum-complexity.yaml` `src_kopelowitz_et_al_2016`: Higher Lower Bounds from the 3SUM Conjecture. DOI resolves to different title/authors (title score 0.340); resolver returned 'Incidence Geometries and the Pass Complexity of Semi-Streaming Set Cover'
- `data/problems/theoretical-cs/3sum-complexity.yaml` `src_vassilevska_williams_2018`: On Some Fine-Grained Questions in Algorithms and Complexity. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/aanderaa-karp-rosenberg-conjecture.yaml` `src_kahn_saks_sturtevant_1984`: A Topological Approach to Evasiveness. DOI resolves to a likely different work (title score 0.283); resolver returned 'Orthogonal vectors in then-dimensional cube and codes with missing distances'
- `data/problems/theoretical-cs/aanderaa-karp-rosenberg-conjecture.yaml` `src_rosenberg_1973`: On the Time Required to Recognize Properties of Graphs: A Problem. DOI resolves to a likely different work (title score 0.255); resolver returned 'A Formalization of Transition Diagram Systems'
- `data/problems/theoretical-cs/acc0-lower-bounds.yaml` `src_kopparty_srinivasan_2018`: Certifying Polynomials for AC^0[p] circuits. source_id encodes year 2018 but source.year is 2012
- `data/problems/theoretical-cs/active-learning-query-complexity.yaml` `src_dasgupta_2011`: Two Faces of Active Learning. DOI resolves to a clearly different work (title score 0.182); resolver returned 'Online scheduling on unbounded parallel-batch machines with incompatible job families'
- `data/problems/theoretical-cs/approximate-nn-lower-bounds.yaml` `src_andoni_indyk_nguyen_razenshteyn_2014`: Beyond Locality-Sensitive Hashing. DOI resolves to different title/authors (title score 0.308); resolver returned 'Computing Cut-Based Hierarchical Decompositions in Almost Linear Time'
- `data/problems/theoretical-cs/art-gallery-complexity.yaml` `src_chvatal_1975`: A Combinatorial Theorem in Plane Geometry. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/berman-hartmanis-conjecture.yaml` `src_agrawal_2002`: Pseudo-random Generators and the Frequency of Simplicity. DOI resolves to different title/authors (title score 0.349); resolver returned 'Hyper-Encryption and Everlasting Security'
- `data/problems/theoretical-cs/black-box-separations.yaml` `src_barak_2001`: How to Go Beyond the Black-Box Simulation Barrier. DOI resolves to different title/authors (title score 0.313); resolver returned 'An iterative rounding 2-approximation algorithm for the element connectivity problem'
- `data/problems/theoretical-cs/bpp-vs-p.yaml` `src_impagliazzo_wigderson_1997`: P = BPP if E Requires Exponential Circuits: Derandomizing the XOR Lemma. source_id reused across 2 files with 2 metadata variants
- `data/problems/theoretical-cs/bpp-vs-p.yaml` `src_kabanets_2002`: Derandomization: A Brief Overview. DOI resolves to a clearly different work (title score 0.171); resolver returned 'Nesting Until and Since in Linear Temporal Logic'
- `data/problems/theoretical-cs/bpp-vs-p.yaml` `src_nisan_wigderson_1994`: Hardness vs Randomness. source_id reused across 2 files with 2 metadata variants
- `data/problems/theoretical-cs/bpp-vs-p.yaml` `src_shaltiel_2004`: Recent Developments in Explicit Constructions of Extractors. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/bqp-vs-np.yaml` `src_bernstein_vazirani_1997`: Quantum Complexity Theory. source_id reused across 2 files with 2 metadata variants
- `data/problems/theoretical-cs/cache-oblivious-optimal.yaml` `src_brodal_fagerberg_2003`: On the Limits of Cache-Obliviousness. DOI resolves to a clearly different work (title score 0.145); resolver returned 'Selfish traffic allocation for server farms'
- `data/problems/theoretical-cs/circuit-complexity-explicit-functions.yaml` `src_blum_1984`: A Boolean Function Requiring 3n Network Size. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/circuit-complexity-explicit-functions.yaml` `src_find_golovnev_hirsch_kulikov_2016`: A Better-than-3n Lower Bound for the Circuit Complexity of an Explicit Function. DOI resolves to a likely different work (title score 0.262); resolver returned 'Towards Strong Reverse Minkowski-Type Inequalities for Lattices'
- `data/problems/theoretical-cs/communication-complexity-open.yaml` `src_chattopadhyay_mande_sherif_2020`: The Log-Approximate-Rank Conjecture is False. DOI resolves to a likely different work (title score 0.207); resolver returned 'Planar graphs of bounded degree have bounded queue number'; source_id encodes year 2020 but source.year is 2019
- `data/problems/theoretical-cs/communication-complexity-open.yaml` `src_lovasz_saks_1988`: Lattices, Möbius Functions and Communication Complexity. DOI resolves to a clearly different work (title score 0.190); resolver returned 'Polynomial algorithm for the k-cut problem'
- `data/problems/theoretical-cs/computational-statistical-gap.yaml` `src_brennan_bresler_2020`: Reducibility and Statistical-Computational Gaps from Secret Leakage. DOI resolves to a clearly different work (title score 0.151); resolver returned 'Strategy-Stealing Is Non-Constructive'
- `data/problems/theoretical-cs/dense-model-theorem.yaml` `src_gowers_2010`: Decompositions, Approximate Structure, Transference, and the Hahn-Banach Theorem. DOI resolves to different title/authors (title score 0.335); resolver returned 'Infinite sequences of linear functionals, positive operator-valued measures and Naimark extension theorem'
- `data/problems/theoretical-cs/derandomization-p-bpp.yaml` `src_goldreich_2011`: In a world of P = BPP. DOI resolves to a clearly different work (title score 0.120); resolver returned 'The GGM Construction Does NOT Yield Correlation Intractable Function Ensembles'
- `data/problems/theoretical-cs/derandomization-p-bpp.yaml` `src_impagliazzo_wigderson_1997`: P = BPP if E requires exponential circuits: Derandomizing the XOR lemma. source_id reused across 2 files with 2 metadata variants
- `data/problems/theoretical-cs/dynamic-graph-lower-bounds.yaml` `src_henzinger_krinninger_nanongkai_2015`: Conditional Lower Bounds for Dynamic Problems. DOI resolves to a likely different work (title score 0.213); resolver returned '2-Vertex Connectivity in Directed Graphs'
- `data/problems/theoretical-cs/dynamic-optimality-conjecture.yaml` `src_demaine_harmon_iacono_patrascu_2007`: Dynamic Optimality — Almost. DOI resolves to a likely different work (title score 0.224); resolver returned 'Explicit Sensor Network Localization using Semidefinite Representations and Facial Reductions'
- `data/problems/theoretical-cs/eth-vs-seth.yaml` `src_williams_2015`: Hardness of Easy Problems: Basing Hardness on Popular Conjectures such as the Strong Exponential Time Hypothesis. DOI resolves to a likely different work (title score 0.259); resolver returned 'Cohomology of Finite Groups: Interactions and Applications'
- `data/problems/theoretical-cs/formula-vs-circuit-complexity.yaml` `src_subbotovskaya_1961`: Realizations of Linear Functions by Formulas Using ∧, ∨, ¬. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/hardness-vs-randomness.yaml` `src_chen_tell_2021`: Hardness vs Randomness, Revised: Uniform, Non-Black-Box, and Instance-Wise. DOI resolves to a likely different work (title score 0.258); resolver returned 'Unambiguous DNFs and Alon-Saks-Seymour'
- `data/problems/theoretical-cs/ideal-lattice-problems.yaml` `src_cramer_ducas_wesolowski_2021`: Short Stickelberger Class Relations and Application to Ideal-SVP. DOI resolves to different title/authors (title score 0.358); resolver returned 'One-Shot Verifiable Encryption from Lattices'; source_id encodes year 2021 but source.year is 2017
- `data/problems/theoretical-cs/k-clique-detection.yaml` `src_nesetril_poljak_1985`: On the Complexity of the Subgraph Problem. DOI resolves to different title/authors (title score 0.348); resolver returned 'Lower bound of the hadwiger number of graphs by their average degree'
- `data/problems/theoretical-cs/kolmogorov-cryptography.yaml` `src_liu_pass_2020`: On One-way Functions and Kolmogorov Complexity. DOI resolves to different title/authors (title score 0.341); resolver returned 'Resolution of the Burrows-Wheeler Transform Conjecture'
- `data/problems/theoretical-cs/kolmogorov-cryptography.yaml` `src_liu_pass_2023`: One-Way Functions and the Hardness of (Probabilistic) Time-Bounded Kolmogorov Complexity. DOI resolves to a clearly different work (title score 0.187); resolver returned 'Universal Amplification of KDM Security: From 1-Key Circular to Multi-Key KDM'
- `data/problems/theoretical-cs/l-vs-nl.yaml` `src_savitch_1970`: Relationships between nondeterministic and deterministic tape complexities. source_id reused across 2 files with 2 metadata variants
- `data/problems/theoretical-cs/l-vs-p.yaml` `src_arora_barak_2009`: Computational Complexity: A Modern Approach. source_id duplicated across 2 files with identical metadata
- `data/problems/theoretical-cs/lwe-hardness-parameters.yaml` `src_albrecht_player_scott_2015`: On the Concrete Hardness of Learning with Errors. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/mcsp-complexity.yaml` `src_allender_2017`: The Complexity of Complexity. DOI resolves to a clearly different work (title score 0.154); resolver returned 'Surfing with Rod'
- `data/problems/theoretical-cs/monotone-circuit-lower-bounds.yaml` `src_goos_pitassi_watson_2018`: Deterministic Communication vs. Partition Number. DOI resolves to a likely different work (title score 0.264); resolver returned 'Singularity Formation and Global Existence of Classical Solutions for One-Dimensional Rotating Shallow Water System'
- `data/problems/theoretical-cs/natural-proofs-barrier.yaml` `src_razborov_rudich_1997`: Natural Proofs. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/natural-proofs-barrier.yaml` `src_williams_2013_natural`: Natural Proofs versus Derandomization. DOI resolves to different title/authors (title score 0.318); resolver returned 'Reusable garbled circuits and succinct functional encryption'
- `data/problems/theoretical-cs/nc-vs-p.yaml` `src_pippenger_1979`: On Simultaneous Resource Bounds. DOI resolves to a likely different work (title score 0.207); resolver returned 'Observations about the development of theoretical computer science'
- `data/problems/theoretical-cs/nexp-vs-bpp.yaml` `src_williams_2011`: Non-Uniform ACC Circuit Lower Bounds. DOI resolves to a likely different work (title score 0.213); resolver returned 'Improved Constructions of Three Source Extractors'
- `data/problems/theoretical-cs/nisan-wigderson-hypothesis.yaml` `src_nisan_wigderson_1994`: Hardness vs Randomness. source_id reused across 2 files with 2 metadata variants
- `data/problems/theoretical-cs/np-vs-conp.yaml` `src_fortnow_homer_2003`: A Short History of Computational Complexity. DOI resolves to a likely different work (title score 0.277); resolver returned 'Schauder estimates for a class of second order elliptic operators on a cube'
- `data/problems/theoretical-cs/np-vs-conp.yaml` `src_sipser_2012_np`: Introduction to the Theory of Computation. modern source (>=1991) has no URL, which blocks verification
- `data/problems/theoretical-cs/online-bipartite-matching.yaml` `src_huang_zhang_2020`: Online Primal Dual Meets Online Matching with Stochastic Rewards. DOI resolves to different title/authors (title score 0.342); resolver returned 'Reducing path TSP to TSP'
- `data/problems/theoretical-cs/p-vs-pspace.yaml` `src_arora_barak_2009`: Computational Complexity: A Modern Approach. source_id duplicated across 2 files with identical metadata
- `data/problems/theoretical-cs/p-vs-pspace.yaml` `src_savitch_1970`: Relationships Between Nondeterministic and Deterministic Tape Complexities. source_id reused across 2 files with 2 metadata variants
- `data/problems/theoretical-cs/p-vs-pspace.yaml` `src_sipser_2012`: Introduction to the Theory of Computation. modern source (>=1991) has no URL, which blocks verification
- `data/problems/theoretical-cs/pac-learning-dnf.yaml` `src_klivans_servedio_2004`: Learning DNF in Time 2^(O(n^(1/3))). DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/planarity-testing-optimal.yaml` `src_ramachandran_reif_1994`: Planarity Testing in Parallel. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/polygon-triangulation-optimal.yaml` `src_amato_goodrich_ramos_2000`: A Randomized Algorithm for Triangulating a Simple Polygon in Linear Time. DOI resolves to a likely different work (title score 0.271); resolver returned 'On Bounding the Betti Numbers and Computing the Euler Characteristic of Semi-Algebraic Sets'
- `data/problems/theoretical-cs/polygon-triangulation-optimal.yaml` `src_chazelle_1991`: Triangulating a Simple Polygon in Linear Time. DOI resolves to different title/authors (title score 0.408); resolver returned 'Polygon triangulation inO(n log logn) time with simple data structures'
- `data/problems/theoretical-cs/post-quantum-hash-functions.yaml` `src_zhandry_2015`: A Note on the Quantum Collision and k-Distinctness Problems. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/ppad-nash-equilibrium.yaml` `src_rubinstein_2018`: Inapproximability of Nash Equilibrium. source_id encodes year 2018 but source.year is 2017
- `data/problems/theoretical-cs/proper-pac-learning-hardness.yaml` `src_pitt_valiant_1988`: Computational Limitations on Learning from Examples. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/public-key-from-owf.yaml` `src_gertner_kannan_malkin_reingold_vishwanathan_2000`: The Relationship between Public Key Encryption and Oblivious Transfer. DOI resolves to a clearly different work (title score 0.173); resolver returned 'Opportunistic data structures with applications'
- `data/problems/theoretical-cs/qma-vs-qcma.yaml` `src_aaronson_kuperberg_2007`: Quantum versus Classical Proofs and Advice. DOI resolves to a clearly different work (title score 0.000); resolver returned ''
- `data/problems/theoretical-cs/qma-vs-qcma.yaml` `src_aharonov_naveh_2002`: Quantum NP - A Survey. source_id duplicated across 2 files with identical metadata
- `data/problems/theoretical-cs/quantum-interactive-proofs.yaml` `src_ji_natarajan_vidick_wright_yuen_2020`: MIP* = RE. source_id encodes year 2020 but source.year is 2022
- `data/problems/theoretical-cs/quantum-pcp-conjecture.yaml` `src_aharonov_naveh_2002`: Quantum NP - A Survey. source_id duplicated across 2 files with identical metadata
- `data/problems/theoretical-cs/quantum-pcp-conjecture.yaml` `src_gharibian_2015`: Quantum Hamiltonian Complexity. source_id reused across 2 files with 2 metadata variants
- `data/problems/theoretical-cs/quantum-supremacy-formal.yaml` `src_bernstein_vazirani_1997`: Quantum Complexity Theory. source_id reused across 2 files with 2 metadata variants
- `data/problems/theoretical-cs/range-searching-lower-bounds.yaml` `src_chazelle_1993`: Lower Bounds on the Complexity of Polytope Range Searching. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/range-searching-lower-bounds.yaml` `src_matousek_2002`: Lectures on Discrete Geometry. source_id reused across 2 files with 2 metadata variants
- `data/problems/theoretical-cs/secretary-problem-variants.yaml` `src_babaioff_immorlica_kleinberg_2007`: Matroids, Secretary Problems, and Online Mechanisms. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/secretary-problem-variants.yaml` `src_lachish_2014`: O(log log rank)-Competitive Ratio for the Matroid Secretary Problem. DOI resolves to a likely different work (title score 0.250); resolver returned 'Path Finding Methods for Linear Programming: Solving Linear Programs in &amp;#x00D5;(vrank) Iterations and Faster Algorithms for Maximum Flow'
- `data/problems/theoretical-cs/sensitivity-conjecture-extensions.yaml` `src_aaronson_2020`: Open problems related to the sensitivity conjecture. source_id encodes year 2020 but source.year is 2019
- `data/problems/theoretical-cs/sorting-networks-depth.yaml` `src_goodrich_2014`: Zig-Zag Sort: A Simple Deterministic Data-Oblivious Sorting Algorithm Running in O(n log n) Time. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/streaming-frequency-moments.yaml` `src_braverman_ostrovsky_2013`: Zero-One Frequency Laws. DOI resolves to a clearly different work (title score 0.163); resolver returned 'Multidimensional approximate agreement in Byzantine asynchronous systems'
- `data/problems/theoretical-cs/strongly-polynomial-lp.yaml` `src_kitahara_mizuno_2013`: A Bound for the Number of Different Basic Feasible Solutions Generated by the Simplex Method. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/strongly-polynomial-lp.yaml` `src_megiddo_1983`: Towards a Genuinely Polynomial Algorithm for Linear Programming. DOI resolves to a likely different work (title score 0.225); resolver returned 'Optimal Search in Planar Subdivisions'
- `data/problems/theoretical-cs/strongly-polynomial-lp.yaml` `src_smale_1998`: Mathematical Problems for the Next Century. source_id reused across 2 files with 2 metadata variants
- `data/problems/theoretical-cs/sublinear-edit-distance.yaml` `src_andoni_krauthgamer_onak_2010`: Polylogarithmic Approximation for Edit Distance and the Asymmetric Query Complexity. DOI resolves to a likely different work (title score 0.239); resolver returned 'Solving Linear Systems through Nested Dissection'
- `data/problems/theoretical-cs/tfnp-structure.yaml` `src_goldberg_hollender_2020`: The Hairy Ball Problem is PPAD-Complete. DOI resolves to a likely different work (title score 0.245); resolver returned 'Deterministic protocols in the SINR model without knowledge of coordinates'
- `data/problems/theoretical-cs/tfnp-structure.yaml` `src_megiddo_papadimitriou_1991`: On Total Functions, Existence Theorems and Computational Complexity. DOI did not return metadata via doi.org or Crossref
- `data/problems/theoretical-cs/unique-games-conjecture.yaml` `src_khot_2002`: On the Power of Unique 2-Prover 1-Round Games. source_id reused across 2 files with 2 metadata variants
- `data/problems/theoretical-cs/unique-games-conjecture.yaml` `src_khot_2010`: On the Unique Games Conjecture. DOI resolves to a clearly different work (title score 0.057); resolver returned 'Wheeled props in algebra, geometry and quantization'
- `data/problems/theoretical-cs/unique-games-conjecture.yaml` `src_khot_2014_survey`: Hardness of Approximation. DOI resolves to a likely different work (title score 0.215); resolver returned 'Low-dimensional topology, low-dimensional field theory and representation theory'
- `data/problems/theoretical-cs/vp-vs-vnp.yaml` `src_valiant_1979`: Completeness Classes in Algebra. DOI resolves to different title/authors (title score 0.393); resolver returned 'On simultaneous resource bounds'

## Recommendations

- Re-audit the DOI-backed entries first. The strongest failures are not formatting problems; many DOIs resolve to completely unrelated papers/books.
- Add a provenance field that distinguishes the original curated seed set from later additions. Right now that separation cannot be reconstructed from repo metadata.
- Enforce a validator rule: `source_id` must be unique repo-wide, or at least unique unless metadata is byte-for-byte identical.
- Enforce a validator rule: if `source_id` ends in a 4-digit year, it must match `source.year`.
- Enforce a validator rule: modern papers/surveys/textbooks should have a resolvable URL; arXiv sources should use `https://arxiv.org/abs/...`.
- Add a DOI verifier in CI that checks resolver metadata title similarity and rejects obviously unrelated DOI/title pairs.
- Triage the mathematics directory first. That domain contains the largest concentration of modern missing URLs and resolver failures.
