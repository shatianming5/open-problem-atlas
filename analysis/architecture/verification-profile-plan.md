---
analyzer: codex/gpt-5.4
reasoning: xhigh
date: 2026-03-08
task: Verification profile classification for all 312 problems
scope: data/problems/**/*.yaml
---

# Verification Profile Classification Plan

## Snapshot

- 审计范围：`data/problems/**/*.yaml` 全量 `312` 个问题文件。
- 仓库现状说明：在本地工作区快照（审计时间 `2026-03-07`）中，`schema/problem.schema.json` 与全部 `312` 个问题文件已经包含 `verification_profile` 与 `tier`；因此本报告的工作不是“从零添加字段”，而是**把现有分类系统完整抽取、解释、统计并提出 schema 加固建议**。
- 三个 domain 的问题数分别为：`mathematics=167`、`theoretical-cs=85`、`mathematical-physics=60`。
- 全库总分布：`statement_precision` 为 `high=281 / medium=28 / low=3`；`solution_checkability` 为 `proof_assistant=144 / computational=88 / mixed=49 / expert_review=31`；`machine_actionability` 为 `high=77 / medium=157 / low=78`；`tier` 为 `tier_1=175 / tier_2=106 / tier_3=31`。

## 1. 分类规则的具体判断标准

### 1.1 审计方法

- 主判据：`statement.canonical`、`title`、`problem_type`、`answer_type`、domain 语义。
- 次判据：`scores.formality`、`scores.toolability`、`scores.ai_fit` 只作为边界案例的 tie-breaker，不作为唯一来源。
- 审计策略：优先尊重现有 `verification_profile`/`tier` 标注；若条目语义明显跨多个子问题、依赖未冻结模型，或带有 program / general / extensions / connections / mechanism 等聚合表达，则下调精度或可检验性。

### 1.2 `statement_precision`

| 值 | 判断标准 | 典型信号 |
| --- | --- | --- |
| `high` | 可以自然改写成单个精确命题：存在性、全称量化、复杂度分离、精确阈值、上下界、分类或 exact value | `conjecture` / `bound` / `existence` / `numeric` / `boolean`，canonical statement 中出现清晰量词、参数范围、目标函数或上界 |
| `medium` | 数学对象明确，但 scope 仍然偏宽、含“general case / extensions / structure / programmatic”成分，或者一个条目里塞了多个相关子问题 | 标题/陈述含 `general`、`extensions`、`structure`、`rates`、`classification ... general`、`for all families` 等 |
| `low` | 更像研究方向、机制解释或跨学科 agenda，不能稳定压缩成单个 theorem-shaped proposition | 标题/陈述含 `mechanism`、`connections`、`consistent theory`，或者需要先决定理论框架/模型再谈证明 |

补充经验规则：`scores.formality >= 0.80` 通常支持 `high`，`0.55–0.79` 常见于 `medium` 边界区，`<= 0.50` 是强烈的 `low`/`medium` 信号；但如果 canonical statement 已经给出清晰量化与参数，这个分数不会自动压低到 `medium`。

### 1.3 `solution_checkability`

| 值 | 判断标准 | 典型场景 |
| --- | --- | --- |
| `proof_assistant` | 解答一旦存在，可被 Lean / Coq / Isabelle 形式系统完整承载与验证；重点是 theorem-shaped proof object，而不是当前是否已有 formalization | 纯数学定理、复杂度分离、代数/拓扑/离散结构中的精确定理 |
| `computational` | 反例、最优值、精确阈值、复杂度见证、SAT/SMT/ILP/枚举证书可以由程序独立验真 | Ramsey / threshold / exact value / algorithmic bound / search-heavy 条目 |
| `mixed` | 机器可验证部分证书或关键子结论，但完整闭环仍需数学推导或人工裁量 | 数值/枚举 + 理论证明、分类问题的算法部分 + 概念性证明 |
| `expert_review` | 即使给出“答案”，仍高度依赖专家对模型、定义边界或物理解释的人工判断，难以下降为统一机器证书 | 物理机制、广义 correspondence、研究计划式条目、尚未冻结的框架问题 |

### 1.4 `machine_actionability`

| 值 | 判断标准 | 典型信号 |
| --- | --- | --- |
| `high` | agent 可以直接开跑：搜索反例、枚举构造、SAT/SMT、数值优化、形式化子目标、自动验证证书 | `toolability`/`ai_fit` 偏高，答案形状明确，存在快速反馈回路 |
| `medium` | 需要人类设定模型、分解子目标或解释结果，但机器仍能稳定承担一大块工作 | 需要先固定 family / noise model / parameter regime / lemma interface |
| `low` | 目前缺少稳定可执行的机器内环；更多只能做文献整理或弱辅助 | `toolability` 与 `ai_fit` 均低、问题高度概念化或依赖深层新理论 |

### 1.5 `tier` 归并规则（对用户原始规则的工程化澄清）

用户给出的 `tier_2` 规则里写的是 “`solution_checkability != low`”，但该轴并不存在 `low` 枚举。为保证规则可执行、可 schema 化，本报告采用如下**规范化 tier 规则**：

- `tier_1 = statement_precision=high` 且 `solution_checkability ∈ {proof_assistant, computational}` 且 `machine_actionability ∈ {high, medium}`
- `tier_2 = statement_precision ∈ {high, medium}` 且 `solution_checkability ∈ {proof_assistant, computational, mixed}` 且不满足 `tier_1`
- `tier_3 = statement_precision=low` 或 `solution_checkability=expert_review`

这套规则与当前仓库中的 `312` 条实际标注完全一致。

## 2. 每个 domain 的统计分布

说明：`PA/C/M/ER` 顺序分别代表 `proof_assistant / computational / mixed / expert_review`。

| domain | count | statement_precision (high/medium/low) | solution_checkability (PA/C/M/ER) | machine_actionability (high/medium/low) | tier (1/2/3) |
| --- | ---: | --- | --- | --- | --- |
| mathematics | 167 | 165/2/0 | 109/38/15/5 | 67/67/33 | 118/44/5 |
| theoretical-cs | 85 | 82/3/0 | 35/36/9/5 | 6/51/28 | 48/32/5 |
| mathematical-physics | 60 | 34/23/3 | 0/14/25/21 | 4/39/17 | 9/30/21 |
| overall | 312 | 281/28/3 | 144/88/49/31 | 77/157/78 | 175/106/31 |

### 2.1 结构性观察

- `mathematics` 几乎全部是 `high` precision（`165/167`），并且以 `proof_assistant` 与 `computational` 为主，因此形成最大的 `tier_1` 核心区（`118` 条）。
- `theoretical-cs` 的结构与数学相似，但更明显地分成两类：一类是可形式化的复杂度命题，另一类是可证书化/可搜索的算法与下界问题。
- `mathematical-physics` 明显不同：`60` 条里只有 `9` 条进入 `tier_1`，主因不是“不重要”，而是条目经常带有模型选择、物理解释或多个 conjecture bundle。
- 全库最常见的组合是 `high + proof_assistant + medium + tier_1`（`61` 条），其次是 `high + proof_assistant + low + tier_2`（`48` 条）和 `high + computational + high + tier_1`（`40` 条）。

## 3. 每个问题的具体分类

以下表格直接覆盖 `312` 个问题文件。

### Mathematics (167)

| id | title | statement_precision | solution_checkability | machine_actionability | tier |
| --- | --- | --- | --- | --- | --- |
| opa.mathematics.algebra.andrews-curtis-conjecture | Andrews–Curtis Conjecture | high | computational | high | tier_1 |
| opa.mathematics.algebra.bass-conjecture | Bass Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.algebra.happel-conjecture | Happel's Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.algebra.inverse-galois-problem | Inverse Galois Problem | high | proof_assistant | medium | tier_1 |
| opa.mathematics.algebra.jacobian-conjecture | Jacobian Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.algebra.kaplansky-unit-conjecture | Kaplansky's Unit Conjecture | high | mixed | medium | tier_2 |
| opa.mathematics.algebra.kothe-conjecture | Kothe Conjecture | high | mixed | medium | tier_2 |
| opa.mathematics.algebraic-geometry.resolution-of-singularities-positive-characteristic | Resolution of Singularities in Positive Characteristic | high | proof_assistant | low | tier_2 |
| opa.mathematics.algebraic-geometry.tight-closure-localization-conjecture | Tight Closure Localization Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.algebraic-topology.birman-conjecture-braids | Birman's Conjecture on Braid Groups | high | mixed | medium | tier_2 |
| opa.mathematics.algebraic-topology.combinatorial-hodge-conjecture | Combinatorial Hodge Conjecture | high | mixed | medium | tier_2 |
| opa.mathematics.algebraic-topology.telescope-conjecture | Telescope Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.analysis.erdos-conjecture-arithmetic-progressions | Erdos Conjecture on Arithmetic Progressions | high | proof_assistant | low | tier_2 |
| opa.mathematics.analysis.invariant-subspace-problem | Invariant Subspace Problem | high | proof_assistant | medium | tier_1 |
| opa.mathematics.analysis.navier-stokes-existence-and-smoothness | Navier-Stokes Existence and Smoothness | high | mixed | medium | tier_2 |
| opa.mathematics.approximation-theory.approximation-jackson-bernstein-sharp | Sharp Jackson-Bernstein Constants Problem | high | computational | high | tier_1 |
| opa.mathematics.approximation-theory.khintchine-flatness-conjecture | Khintchine's Flatness Conjecture | high | computational | high | tier_1 |
| opa.mathematics.approximation-theory.littlewood-conjecture | Littlewood Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.category-theory.deninger-program | Deninger's Program | high | expert_review | low | tier_3 |
| opa.mathematics.category-theory.grothendieck-standard-conjectures | Grothendieck's Standard Conjectures | high | proof_assistant | low | tier_2 |
| opa.mathematics.category-theory.kontsevich-zagier-conjecture | Kontsevich-Zagier Conjecture | high | mixed | medium | tier_2 |
| opa.mathematics.coding-theory.cerny-conjecture | Cerny Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.coding-theory.simplex-conjecture | Simplex Conjecture in Information Theory | high | computational | high | tier_1 |
| opa.mathematics.combinatorics.burnside-problem-bounded-exponent | Restricted Burnside Problem Generalizations | high | mixed | medium | tier_2 |
| opa.mathematics.combinatorics.erdos-ginzburg-ziv-generalization | Erdos-Ginzburg-Ziv Constant for General Groups | high | computational | high | tier_1 |
| opa.mathematics.combinatorics.hadamard-conjecture | Hadamard Conjecture | high | computational | high | tier_1 |
| opa.mathematics.combinatorics.hadwiger-nelson-problem | Hadwiger-Nelson Problem | high | computational | high | tier_1 |
| opa.mathematics.combinatorics.lonely-runner-conjecture | Lonely Runner Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.combinatorics.ramsey-number-r55 | Ramsey Number R(5,5) | high | computational | high | tier_1 |
| opa.mathematics.combinatorics.rotas-basis-conjecture | Rota's Basis Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.combinatorics.rysers-conjecture | Ryser's Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.combinatorics.singmasters-conjecture | Singmaster's Conjecture | high | computational | high | tier_1 |
| opa.mathematics.combinatorics.union-closed-sets-conjecture | Union-Closed Sets Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.commutative-algebra.casas-alvero-conjecture | Casas-Alvero Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.commutative-algebra.pierce-birkhoff-conjecture | Pierce-Birkhoff Conjecture | high | mixed | medium | tier_2 |
| opa.mathematics.commutative-algebra.tate-conjecture | Tate Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.complex-analysis.fatou-conjecture | Fatou Conjecture (Density of Hyperbolicity) | high | mixed | medium | tier_2 |
| opa.mathematics.complex-analysis.mlc-conjecture | MLC Conjecture (Mandelbrot Set Locally Connected) | high | mixed | medium | tier_2 |
| opa.mathematics.complex-analysis.sendov-conjecture | Sendov's Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.convex-geometry.bourgain-slicing-conjecture | Bourgain's Slicing Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.convex-geometry.log-brunn-minkowski-conjecture | Log-Brunn-Minkowski Conjecture | high | computational | high | tier_1 |
| opa.mathematics.convex-geometry.mahler-conjecture | Mahler Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.differential-equations.hot-spots-conjecture | Hot Spots Conjecture | high | computational | high | tier_1 |
| opa.mathematics.differential-equations.leray-conjecture | Leray's Conjecture on Self-Similar Blow-Up | high | proof_assistant | medium | tier_1 |
| opa.mathematics.differential-geometry.abundance-conjecture | Abundance Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.differential-geometry.hopf-conjecture-positive-curvature | Hopf Conjecture (Positive Sectional Curvature) | high | proof_assistant | low | tier_2 |
| opa.mathematics.differential-geometry.lang-conjecture-rational-points | Lang's Conjecture on Rational Points | high | proof_assistant | medium | tier_1 |
| opa.mathematics.differential-geometry.yau-first-eigenvalue-conjecture | Yau's Conjecture on the First Eigenvalue | high | proof_assistant | medium | tier_1 |
| opa.mathematics.discrete-geometry.borsuk-conjecture | Borsuk's Conjecture | high | computational | high | tier_1 |
| opa.mathematics.discrete-geometry.ungar-conjecture | Ungar's Conjecture on Direction Sets | high | computational | high | tier_1 |
| opa.mathematics.dynamical-systems.furstenberg-x2-x3-conjecture | Furstenberg's x2 x3 Conjecture | high | mixed | medium | tier_2 |
| opa.mathematics.dynamical-systems.hilbert-16th-problem-second-part | Hilbert's 16th Problem (Second Part) | high | computational | medium | tier_1 |
| opa.mathematics.dynamical-systems.jakobson-conjecture | Jakobson's Conjecture (Prevalence of Stochastic Behavior) | high | mixed | medium | tier_2 |
| opa.mathematics.dynamical-systems.lehmer-conjecture | Lehmer's Conjecture (Mahler Measure) | high | proof_assistant | medium | tier_1 |
| opa.mathematics.dynamical-systems.zimmer-conjecture | Zimmer's Conjecture | high | expert_review | low | tier_3 |
| opa.mathematics.enumerative-combinatorics.freiman-ruzsa-conjecture | Polynomial Freiman-Ruzsa Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.enumerative-combinatorics.ringel-conjecture | Ringel's Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.extremal-combinatorics.erdos-ko-rado-generalization | Erdos-Ko-Rado for Permutations | high | proof_assistant | high | tier_1 |
| opa.mathematics.extremal-combinatorics.erdos-sos-conjecture | Erdos-Sos Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.extremal-combinatorics.frankl-conjecture-specific-bounds | Frankl's Conjecture: Optimal Abundance Bound | high | computational | high | tier_1 |
| opa.mathematics.extremal-combinatorics.zarankiewicz-problem | Zarankiewicz Problem | high | computational | medium | tier_1 |
| opa.mathematics.functional-analysis.kadison-kaplansky-conjecture | Kadison-Kaplansky Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.functional-analysis.selberg-eigenvalue-conjecture | Selberg Eigenvalue Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.functional-analysis.weiss-conjecture-admissibility | Weiss Conjecture on Admissibility | high | proof_assistant | medium | tier_1 |
| opa.mathematics.geometric-topology.slice-ribbon-conjecture | Slice-Ribbon Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.geometric-topology.weinstein-conjecture | Weinstein Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.geometry.bellman-lost-in-forest | Bellman's Lost-in-a-Forest Problem | high | computational | high | tier_1 |
| opa.mathematics.geometry.kakeya-conjecture | Kakeya Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.geometry.lebesgue-universal-covering-problem | Lebesgue's Universal Covering Problem | high | computational | high | tier_1 |
| opa.mathematics.geometry.moving-sofa-problem | Moving Sofa Problem | high | computational | high | tier_1 |
| opa.mathematics.geometry.wegner-conjecture | Wegner's Conjecture on Disk Graphs | high | computational | high | tier_1 |
| opa.mathematics.graph-theory.albertson-conjecture | Albertson Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.graph-theory.caccetta-haggkvist-conjecture | Caccetta-Haggkvist Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.graph-theory.cycle-double-cover-conjecture | Cycle Double Cover Conjecture | high | computational | high | tier_1 |
| opa.mathematics.graph-theory.erdos-faber-lovasz-conjecture | Erdos-Faber-Lovasz Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.graph-theory.erdos-gyarfas-conjecture | Erdos-Gyarfas Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.graph-theory.erdos-hajnal-conjecture | Erdos-Hajnal Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.graph-theory.graceful-tree-conjecture | Graceful Tree Conjecture | high | computational | high | tier_1 |
| opa.mathematics.graph-theory.gyarfas-sumner-conjecture | Gyarfas-Sumner Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.graph-theory.hadwiger-conjecture | Hadwiger Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.graph-theory.list-coloring-conjecture | List Coloring Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.graph-theory.overfull-conjecture | Overfull Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.graph-theory.reconstruction-conjecture | Reconstruction Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.graph-theory.seymours-second-neighborhood-conjecture | Seymour's Second Neighborhood Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.graph-theory.total-coloring-conjecture | Total Coloring Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.graph-theory.turan-brick-factory-problem | Turan's Brick Factory Problem | high | computational | high | tier_1 |
| opa.mathematics.graph-theory.vizings-conjecture | Vizing's Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.harmonic-analysis.carleson-coefficients-conjecture | Dimension-Free Estimates in Harmonic Analysis | high | proof_assistant | medium | tier_1 |
| opa.mathematics.harmonic-analysis.sarnak-conjecture | Sarnak's Mobius Disjointness Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.homological-algebra.artins-conjecture-primitive-roots | Artin's Conjecture on Primitive Roots | high | proof_assistant | medium | tier_1 |
| opa.mathematics.homological-algebra.chromatic-splitting-conjecture | Chromatic Splitting Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.homological-algebra.generating-hypothesis | Freyd's Generating Hypothesis | high | proof_assistant | low | tier_2 |
| opa.mathematics.lattice-theory.lattice-distortion-conjecture | Lattice Distortion Problem | high | computational | high | tier_1 |
| opa.mathematics.logic-and-foundations.large-cardinal-hierarchy | Large Cardinal Consistency Strength Hierarchy | high | expert_review | low | tier_3 |
| opa.mathematics.logic-and-foundations.new-foundations-consistency | Consistency of Quine's New Foundations | high | proof_assistant | medium | tier_1 |
| opa.mathematics.logic-and-foundations.vaughts-conjecture | Vaught's Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.mathematical-optimization.linear-programming-strongly-polynomial | Strongly Polynomial Linear Programming | high | proof_assistant | high | tier_1 |
| opa.mathematics.mathematical-optimization.nonnegative-rank-conjecture | Nonnegative Rank vs Extension Complexity | high | computational | high | tier_1 |
| opa.mathematics.mathematical-optimization.smale-18th-problem | Smale's 18th Problem | medium | computational | medium | tier_2 |
| opa.mathematics.matroid-theory.dowling-wilson-conjecture | Dowling-Wilson Top-Heavy Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.matroid-theory.rota-welsh-conjecture | Rota-Welsh Conjecture (Extensions) | high | proof_assistant | medium | tier_1 |
| opa.mathematics.matroid-theory.welsh-conjecture | Welsh's Conjecture | high | computational | high | tier_1 |
| opa.mathematics.measure-theory.brennan-conjecture | Brennan's Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.measure-theory.uhl-conjecture-measures | Uhl's Conjecture on Vector Measures | high | proof_assistant | medium | tier_1 |
| opa.mathematics.model-theory.cherlin-zilber-conjecture | Cherlin-Zilber Conjecture | high | expert_review | low | tier_3 |
| opa.mathematics.model-theory.shelah-categoricity-conjecture | Shelah's Categoricity Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.non-commutative-algebra.connes-embedding-problem | Connes Embedding Problem (Consequences) | high | proof_assistant | low | tier_2 |
| opa.mathematics.non-commutative-algebra.langlands-functoriality-conjecture | Langlands Functoriality Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.non-commutative-algebra.matrix-mortality-problem | Matrix Mortality Problem | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.abc-conjecture-effective | Effective abc Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.number-theory.agoh-giuga-conjecture | Agoh-Giuga Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.bateman-horn-conjecture | Bateman-Horn Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.number-theory.birch-swinnerton-dyer-conjecture | Birch and Swinnerton-Dyer Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.number-theory.brocards-problem | Brocard's Problem | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.bunyakovsky-conjecture | Bunyakovsky Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.number-theory.catalan-dickson-conjecture | Catalan-Dickson Conjecture on Perfect Numbers | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.collatz-conjecture | Collatz Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.cramers-conjecture | Cramer's Conjecture | high | computational | high | tier_1 |
| opa.mathematics.number-theory.erdos-mollin-walsh-conjecture | Erdos-Mollin-Walsh Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.erdos-straus-conjecture | Erdos-Straus Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.gilbreaths-conjecture | Gilbreath's Conjecture | high | computational | high | tier_1 |
| opa.mathematics.number-theory.goldbach-conjecture | Goldbach's Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.grimms-conjecture | Grimm's Conjecture | high | computational | high | tier_1 |
| opa.mathematics.number-theory.halls-conjecture | Hall's Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.hardy-littlewood-k-tuple-conjecture | Hardy-Littlewood k-Tuple Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.number-theory.lander-parkin-selfridge-conjecture | Lander-Parkin-Selfridge Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.legendres-conjecture | Legendre's Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.lehmers-totient-problem | Lehmer's Totient Problem | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.n-squared-plus-one-prime-conjecture | n^2 + 1 Prime Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.number-theory.pillais-conjecture | Pillai's Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.number-theory.polya-conjecture | Polya Conjecture on Dirichlet Characters | high | proof_assistant | medium | tier_1 |
| opa.mathematics.number-theory.riemann-hypothesis | Riemann Hypothesis | high | proof_assistant | medium | tier_1 |
| opa.mathematics.number-theory.sato-tate-generalizations | Generalized Sato-Tate Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.number-theory.schanuel-conjecture | Schanuel's Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.number-theory.schinzel-hypothesis-h | Schinzel's Hypothesis H | high | proof_assistant | low | tier_2 |
| opa.mathematics.number-theory.scholz-conjecture | Scholz Conjecture | high | computational | high | tier_1 |
| opa.mathematics.number-theory.selfridges-conjecture | Selfridge's Conjecture on Primality | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.sierpinski-problem | Sierpinski Problem | high | computational | high | tier_1 |
| opa.mathematics.number-theory.twin-prime-conjecture | Twin Prime Conjecture | high | proof_assistant | high | tier_1 |
| opa.mathematics.number-theory.warings-problem-exact | Waring's Problem (Exact Values of g(k)) | high | computational | high | tier_1 |
| opa.mathematics.numerical-analysis.smale-17th-problem | Smale's 17th Problem | high | computational | high | tier_1 |
| opa.mathematics.operator-algebras.dixmier-problem | Dixmier Problem | high | proof_assistant | medium | tier_1 |
| opa.mathematics.operator-algebras.elliott-classification-conjecture | Elliott Classification Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.operator-algebras.kadison-similarity-problem | Kadison's Similarity Problem | high | proof_assistant | low | tier_2 |
| opa.mathematics.operator-algebras.kadison-singer-extensions | Kadison-Singer Problem Extensions (Infinite-Dimensional Paving) | high | mixed | medium | tier_2 |
| opa.mathematics.order-theory.neggers-stanley-conjecture | Neggers-Stanley Conjecture | high | computational | high | tier_1 |
| opa.mathematics.partial-differential-equations.global-regularity-supercritical-sqs | Global Regularity for Supercritical Surface Quasi-Geostrophic Equation | high | proof_assistant | medium | tier_1 |
| opa.mathematics.partial-differential-equations.navier-stokes-regularity-2d-euler | Global Regularity of 3D Euler Equations | high | proof_assistant | medium | tier_1 |
| opa.mathematics.partial-differential-equations.strong-cosmic-censorship-conjecture | Strong Cosmic Censorship Conjecture (Mathematical Formulation) | high | proof_assistant | low | tier_2 |
| opa.mathematics.probability.density-hales-jewett-polynomial | Polynomial Density Hales–Jewett Conjecture | high | mixed | medium | tier_2 |
| opa.mathematics.probability.elliott-halberstam-conjecture | Elliott-Halberstam Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.probability.entropy-power-inequality-extensions | Entropy Power Inequality for Dependent Variables | high | computational | high | tier_1 |
| opa.mathematics.probability.kalai-conjecture-noise-sensitivity | Kalai's Conjecture on Noise Sensitivity of Boolean Functions | high | computational | high | tier_1 |
| opa.mathematics.probability.keating-snaith-conjecture | Keating-Snaith Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.probability.kls-conjecture | KLS Conjecture | high | proof_assistant | medium | tier_1 |
| opa.mathematics.probability.random-schrodinger-operator-localization | Anderson Localization in Higher Dimensions | high | proof_assistant | medium | tier_1 |
| opa.mathematics.representation-theory.iwasawa-main-conjecture-nonabelian | Non-abelian Iwasawa Main Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.representation-theory.unitary-dual-problem | Unitary Dual Problem for Reductive Groups | medium | mixed | medium | tier_2 |
| opa.mathematics.set-theory.borels-conjecture | Borel's Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.set-theory.halpern-lauchli-partition-conjecture | Halpern-Lauchli Theorem Extensions to Uncountable Cardinals | high | proof_assistant | low | tier_2 |
| opa.mathematics.set-theory.woodins-ultimate-l-conjecture | Woodin's Ultimate L Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.topology.baum-connes-conjecture | Baum–Connes Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.topology.hilbert-smith-conjecture | Hilbert–Smith Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.topology.kervaire-invariant-problem | Kervaire Invariant Problem | high | proof_assistant | low | tier_2 |
| opa.mathematics.topology.novikov-conjecture | Novikov Conjecture | high | proof_assistant | low | tier_2 |
| opa.mathematics.topology.smooth-4d-poincare-conjecture | Smooth 4-Dimensional Poincare Conjecture | high | expert_review | low | tier_3 |
| opa.mathematics.topology.volume-conjecture | Volume Conjecture | high | computational | medium | tier_1 |

### Theoretical CS (85)

| id | title | statement_precision | solution_checkability | machine_actionability | tier |
| --- | --- | --- | --- | --- | --- |
| opa.tcs.algorithms.3sum-complexity | 3SUM Complexity: Is There an O(n log n) Algorithm? | high | proof_assistant | high | tier_1 |
| opa.tcs.algorithms.approximate-nn-lower-bounds | Approximate Nearest Neighbor Lower Bounds | high | computational | medium | tier_1 |
| opa.tcs.algorithms.cache-oblivious-optimal | Optimal Cache-Oblivious Algorithms | high | computational | medium | tier_1 |
| opa.tcs.algorithms.dynamic-graph-lower-bounds | Dynamic Graph Algorithms Lower Bounds | high | computational | medium | tier_1 |
| opa.tcs.algorithms.dynamic-optimality-conjecture | Dynamic Optimality Conjecture for Binary Search Trees | high | proof_assistant | medium | tier_1 |
| opa.tcs.algorithms.k-clique-detection | Optimal k-Clique Detection Algorithm | high | computational | medium | tier_1 |
| opa.tcs.algorithms.matrix-multiplication-exponent | Matrix Multiplication Exponent | high | proof_assistant | medium | tier_1 |
| opa.tcs.algorithms.multi-armed-bandit-regret | Multi-Armed Bandit Optimal Regret | high | computational | high | tier_1 |
| opa.tcs.algorithms.nearest-neighbor-high-dim | Nearest Neighbor Search in High Dimensions | high | computational | high | tier_1 |
| opa.tcs.algorithms.online-bipartite-matching | Online Bipartite Matching Optimal Competitive Ratio | high | computational | medium | tier_1 |
| opa.tcs.algorithms.online-learning-experts | Online Learning with Expert Advice Optimal Bounds | high | computational | medium | tier_1 |
| opa.tcs.algorithms.secretary-problem-variants | Secretary Problem Variants | high | computational | medium | tier_1 |
| opa.tcs.algorithms.sensitivity-conjecture-extensions | Sensitivity Conjecture Extensions | high | computational | medium | tier_1 |
| opa.tcs.algorithms.sorting-networks-depth | Optimal Depth of Sorting Networks | high | computational | medium | tier_1 |
| opa.tcs.algorithms.streaming-frequency-moments | Streaming Lower Bounds for Frequency Moments | high | computational | medium | tier_1 |
| opa.tcs.algorithms.strongly-polynomial-lp | Strongly Polynomial Algorithm for Linear Programming | high | proof_assistant | medium | tier_1 |
| opa.tcs.algorithms.sublinear-edit-distance | Sublinear Time Algorithms for Edit Distance | high | computational | high | tier_1 |
| opa.tcs.algorithms.union-find-optimal | Union-Find Optimal Bounds | high | computational | medium | tier_1 |
| opa.tcs.complexity-theory.acc0-lower-bounds | ACC0 Circuit Lower Bounds | high | proof_assistant | low | tier_2 |
| opa.tcs.complexity-theory.berman-hartmanis-conjecture | Berman-Hartmanis Isomorphism Conjecture | high | proof_assistant | low | tier_2 |
| opa.tcs.complexity-theory.bpp-vs-p | BPP vs P Problem | high | proof_assistant | medium | tier_1 |
| opa.tcs.complexity-theory.circuit-complexity-explicit-functions | Circuit Complexity of Explicit Functions | high | computational | medium | tier_1 |
| opa.tcs.complexity-theory.communication-complexity-open | Log-Rank Conjecture in Communication Complexity | high | proof_assistant | medium | tier_1 |
| opa.tcs.complexity-theory.dense-model-theorem | Dense Model Theorem Extensions | medium | mixed | medium | tier_2 |
| opa.tcs.complexity-theory.derandomization-p-bpp | Derandomization: Does P = BPP? | high | proof_assistant | low | tier_2 |
| opa.tcs.complexity-theory.eth-vs-seth | ETH vs SETH Gap | high | proof_assistant | medium | tier_1 |
| opa.tcs.complexity-theory.formula-vs-circuit-complexity | Formula vs Circuit Complexity Gap | high | computational | low | tier_2 |
| opa.tcs.complexity-theory.graph-isomorphism-complexity | Graph Isomorphism Problem Complexity | high | proof_assistant | medium | tier_1 |
| opa.tcs.complexity-theory.hardness-vs-randomness | Hardness vs Randomness Connections | high | expert_review | low | tier_3 |
| opa.tcs.complexity-theory.l-vs-nl | L vs NL Problem | high | proof_assistant | low | tier_2 |
| opa.tcs.complexity-theory.l-vs-p | L vs P Problem | high | proof_assistant | low | tier_2 |
| opa.tcs.complexity-theory.mcsp-complexity | Minimum Circuit Size Problem Complexity | high | mixed | medium | tier_2 |
| opa.tcs.complexity-theory.monotone-circuit-lower-bounds | Monotone Circuit Lower Bounds | high | computational | low | tier_2 |
| opa.tcs.complexity-theory.natural-proofs-barrier | Natural Proofs Barrier Circumvention | high | expert_review | low | tier_3 |
| opa.tcs.complexity-theory.nc-vs-p | NC vs P Problem | high | proof_assistant | low | tier_2 |
| opa.tcs.complexity-theory.nexp-vs-bpp | NEXP vs BPP Problem | high | proof_assistant | low | tier_2 |
| opa.tcs.complexity-theory.nisan-wigderson-hypothesis | Nisan-Wigderson Hypothesis | high | proof_assistant | low | tier_2 |
| opa.tcs.complexity-theory.np-vs-conp | NP vs co-NP Problem | high | proof_assistant | low | tier_2 |
| opa.tcs.complexity-theory.p-vs-np | P vs NP Problem | high | proof_assistant | low | tier_2 |
| opa.tcs.complexity-theory.p-vs-pspace | P vs PSPACE Problem | high | proof_assistant | low | tier_2 |
| opa.tcs.complexity-theory.polynomial-hierarchy-infinite | Is the Polynomial Hierarchy Infinite? | high | proof_assistant | low | tier_2 |
| opa.tcs.complexity-theory.ppad-nash-equilibrium | PPAD-Completeness of Nash Equilibrium Variants | high | mixed | medium | tier_2 |
| opa.tcs.complexity-theory.tfnp-structure | Structure of Total NP Search Problems (TFNP) | high | mixed | medium | tier_2 |
| opa.tcs.complexity-theory.unique-games-conjecture | Unique Games Conjecture | high | proof_assistant | medium | tier_1 |
| opa.tcs.complexity-theory.vp-vs-vnp | VP vs VNP Problem | high | proof_assistant | low | tier_2 |
| opa.tcs.computational-geometry.art-gallery-complexity | Art Gallery Problem Computational Complexity | high | mixed | medium | tier_2 |
| opa.tcs.computational-geometry.minimum-enclosing-ball | Minimum Enclosing Ball Algorithms in High Dimensions | high | computational | high | tier_1 |
| opa.tcs.computational-geometry.polygon-triangulation-optimal | Optimal Polygon Triangulation | high | proof_assistant | medium | tier_1 |
| opa.tcs.computational-geometry.range-searching-lower-bounds | Range Searching Lower Bounds | high | computational | medium | tier_1 |
| opa.tcs.computational-geometry.rectilinear-steiner-tree | Rectilinear Steiner Tree Problem | high | computational | medium | tier_1 |
| opa.tcs.cryptography.black-box-separations | Black-Box Separations of Cryptographic Primitives | medium | expert_review | low | tier_3 |
| opa.tcs.cryptography.existence-of-one-way-functions | Existence of One-Way Functions | high | proof_assistant | low | tier_2 |
| opa.tcs.cryptography.homomorphic-encryption-efficiency | Fully Homomorphic Encryption Efficiency | high | computational | medium | tier_1 |
| opa.tcs.cryptography.ideal-lattice-problems | Ideal Lattice Problems Hardness | high | mixed | medium | tier_2 |
| opa.tcs.cryptography.indistinguishability-obfuscation | Indistinguishability Obfuscation from Standard Assumptions | high | expert_review | low | tier_3 |
| opa.tcs.cryptography.kolmogorov-cryptography | Kolmogorov Complexity and Cryptography | high | proof_assistant | low | tier_2 |
| opa.tcs.cryptography.lwe-hardness-parameters | LWE Hardness Exact Parameters | high | computational | medium | tier_1 |
| opa.tcs.cryptography.mpc-optimal-rounds | Multi-Party Computation Optimal Round Complexity | high | computational | medium | tier_1 |
| opa.tcs.cryptography.post-quantum-hash-functions | Post-Quantum Secure Hash Functions | high | mixed | medium | tier_2 |
| opa.tcs.cryptography.prg-from-owf-optimal | Optimal Pseudorandom Generators from One-Way Functions | high | computational | medium | tier_1 |
| opa.tcs.cryptography.public-key-from-owf | Public-Key Cryptography from One-Way Functions | high | proof_assistant | low | tier_2 |
| opa.tcs.graph-algorithms.aanderaa-karp-rosenberg-conjecture | Aanderaa-Karp-Rosenberg Conjecture (Evasiveness Conjecture) | high | proof_assistant | medium | tier_1 |
| opa.tcs.graph-algorithms.apsp-truly-subcubic | All-Pairs Shortest Paths in Truly Subcubic Time | high | computational | medium | tier_1 |
| opa.tcs.graph-algorithms.dynamic-connectivity-optimal | Dynamic Connectivity Optimal Bounds | high | computational | medium | tier_1 |
| opa.tcs.graph-algorithms.max-flow-linear | Maximum Flow in Linear Time | high | proof_assistant | medium | tier_1 |
| opa.tcs.graph-algorithms.mst-optimal-comparison | Minimum Spanning Tree Optimal Comparison Complexity | high | computational | medium | tier_1 |
| opa.tcs.graph-algorithms.planarity-testing-optimal | Planarity Testing in Optimal Parallel Time | high | computational | medium | tier_1 |
| opa.tcs.information-theory.capacity-achieving-linear-time-code | Capacity-Achieving Code with Linear-Time Encoding and Decoding | high | proof_assistant | high | tier_1 |
| opa.tcs.learning-theory.active-learning-query-complexity | Active Learning Query Complexity | high | computational | medium | tier_1 |
| opa.tcs.learning-theory.agnostic-learning-limits | Agnostic Learning Fundamental Limits | high | computational | medium | tier_1 |
| opa.tcs.learning-theory.computational-statistical-gap | Computational-Statistical Gap | high | computational | medium | tier_1 |
| opa.tcs.learning-theory.pac-learning-dnf | PAC Learning DNF Formulas | high | proof_assistant | medium | tier_1 |
| opa.tcs.learning-theory.proper-pac-learning-hardness | Proper PAC Learning Hardness | high | computational | medium | tier_1 |
| opa.tcs.quantum-computing.bqp-vs-np | BQP vs NP Problem | high | proof_assistant | medium | tier_1 |
| opa.tcs.quantum-computing.bqp-vs-ph | BQP vs the Polynomial Hierarchy | high | proof_assistant | low | tier_2 |
| opa.tcs.quantum-computing.qma-vs-qcma | QMA vs QCMA | high | proof_assistant | low | tier_2 |
| opa.tcs.quantum-computing.quantum-communication-complexity | Quantum Communication Complexity Advantages | high | computational | medium | tier_1 |
| opa.tcs.quantum-computing.quantum-error-correction-threshold | Quantum Error Correction Threshold (Exact) | high | computational | medium | tier_1 |
| opa.tcs.quantum-computing.quantum-interactive-proofs | Quantum Interactive Proofs Structure | medium | expert_review | low | tier_3 |
| opa.tcs.quantum-computing.quantum-money-standard | Quantum Money from Standard Assumptions | high | mixed | medium | tier_2 |
| opa.tcs.quantum-computing.quantum-pcp-conjecture | Quantum PCP Conjecture | high | proof_assistant | low | tier_2 |
| opa.tcs.quantum-computing.quantum-speedup-np | Quantum Speedup for NP-Complete Problems | high | computational | low | tier_2 |
| opa.tcs.quantum-computing.quantum-supremacy-formal | Quantum Supremacy Formal Proof | high | proof_assistant | low | tier_2 |
| opa.tcs.quantum-computing.quantum-walk-limits | Quantum Walk Algorithms Limits | high | computational | medium | tier_1 |
| opa.tcs.quantum-computing.topological-qc-universality | Topological Quantum Computation Universality | high | mixed | medium | tier_2 |

### Mathematical Physics (60)

| id | title | statement_precision | solution_checkability | machine_actionability | tier |
| --- | --- | --- | --- | --- | --- |
| opa.phys.condensed-matter-theory.anderson-metal-insulator-transition | Anderson Metal-Insulator Transition | high | mixed | medium | tier_2 |
| opa.phys.condensed-matter-theory.classification-topological-phases-3d | Classification of Topological Phases of Matter in 3D | medium | mixed | medium | tier_2 |
| opa.phys.condensed-matter-theory.fractional-quantum-hall-classification | Classification of Fractional Quantum Hall States | medium | computational | medium | tier_2 |
| opa.phys.condensed-matter-theory.high-tc-superconductivity-mechanism | Mechanism of High-Temperature Superconductivity | low | expert_review | medium | tier_3 |
| opa.phys.condensed-matter-theory.many-body-localization | Many-Body Localization | medium | expert_review | medium | tier_3 |
| opa.phys.condensed-matter-theory.topological-order-classification-general | Topological Order Classification (General) | medium | computational | medium | tier_2 |
| opa.phys.general-relativity.bkl-conjecture-singularity-structure | BKL Conjecture on Singularity Structure | medium | expert_review | low | tier_3 |
| opa.phys.general-relativity.cosmic-censorship-conjecture | Cosmic Censorship Conjecture | high | mixed | medium | tier_2 |
| opa.phys.general-relativity.cosmic-no-hair-conjecture | Cosmic No-Hair Conjecture | high | mixed | low | tier_2 |
| opa.phys.general-relativity.final-state-conjecture-general-relativity | Final State Conjecture in General Relativity | high | mixed | medium | tier_2 |
| opa.phys.general-relativity.no-hair-theorem-rigorous | No-Hair Theorem (Rigorous General Proof) | high | expert_review | low | tier_3 |
| opa.phys.general-relativity.penrose-inequality-general | Penrose Inequality (General Case) | high | mixed | medium | tier_2 |
| opa.phys.general-relativity.stability-of-kerr-solution | Stability of the Kerr Solution | high | expert_review | low | tier_3 |
| opa.phys.mathematical-physics.agt-correspondence-proof | AGT Correspondence Proof | medium | mixed | medium | tier_2 |
| opa.phys.mathematical-physics.dysons-conjecture-extensions | Dyson's Conjecture Extensions | high | mixed | medium | tier_2 |
| opa.phys.mathematical-physics.existence-magnetic-monopoles | Existence of Magnetic Monopoles | medium | expert_review | low | tier_3 |
| opa.phys.mathematical-physics.geometric-langlands-physics | Geometric Langlands Conjecture (Physics Approach) | medium | expert_review | low | tier_3 |
| opa.phys.mathematical-physics.mirror-symmetry-mathematical-proof | Mirror Symmetry Mathematical Proof | high | expert_review | low | tier_3 |
| opa.phys.quantum-field-theory.anomalous-magnetic-moment-theory | Muon Anomalous Magnetic Moment Theory Prediction | medium | computational | high | tier_2 |
| opa.phys.quantum-field-theory.confinement-in-qcd | Confinement in Quantum Chromodynamics | medium | expert_review | low | tier_3 |
| opa.phys.quantum-field-theory.consistent-theory-of-quantum-gravity | Existence of a Consistent Theory of Quantum Gravity | low | expert_review | low | tier_3 |
| opa.phys.quantum-field-theory.constructive-qft-4d | Constructive Quantum Field Theory in 4D | high | expert_review | low | tier_3 |
| opa.phys.quantum-field-theory.haags-theorem-implications | Haag's Theorem and Interaction Picture in QFT | high | expert_review | low | tier_3 |
| opa.phys.quantum-field-theory.mass-gap-non-abelian-gauge-theories | Mass Gap in Non-Abelian Gauge Theories | medium | expert_review | low | tier_3 |
| opa.phys.quantum-field-theory.renormalization-group-rigorous | Rigorous Treatment of the Renormalization Group | medium | mixed | medium | tier_2 |
| opa.phys.quantum-field-theory.seiberg-witten-theory-completeness | Seiberg-Witten Theory Completeness | medium | expert_review | medium | tier_3 |
| opa.phys.quantum-field-theory.strong-cp-problem-mathematical | Strong CP Problem Mathematical Formulation | medium | expert_review | low | tier_3 |
| opa.phys.quantum-field-theory.triviality-phi4-4d | Triviality of phi^4 Theory in 4D | high | mixed | medium | tier_2 |
| opa.phys.quantum-field-theory.wittens-conjecture-3-manifold-invariants | Witten's Conjecture on 3-Manifold Invariants | high | expert_review | low | tier_3 |
| opa.phys.quantum-field-theory.yang-mills-existence-and-mass-gap | Yang-Mills Existence and Mass Gap | medium | expert_review | low | tier_3 |
| opa.phys.quantum-information.additivity-conjecture-quantum-channel-capacity | Additivity Conjecture for Quantum Channel Capacity | high | computational | high | tier_1 |
| opa.phys.quantum-information.entanglement-distillation-optimal-rates | Optimal Rates of Entanglement Distillation | high | computational | medium | tier_1 |
| opa.phys.quantum-information.entanglement-entropy-area-law-general | Entanglement Entropy Area Law in General | high | mixed | medium | tier_2 |
| opa.phys.quantum-information.holographic-entanglement-entropy-conjectures | Holographic Entanglement Entropy Conjectures | medium | expert_review | low | tier_3 |
| opa.phys.quantum-information.mip-star-equals-re | MIP* = RE | high | mixed | medium | tier_2 |
| opa.phys.quantum-information.npt-bound-entanglement-existence | Existence of NPT Bound Entangled States | medium | mixed | medium | tier_2 |
| opa.phys.quantum-information.ppt-bound-entanglement | PPT Bound Entanglement Problem | high | mixed | medium | tier_2 |
| opa.phys.quantum-information.quantum-channel-capacity-additivity-general | Quantum Channel Capacity Additivity (General Conjectures) | high | mixed | medium | tier_2 |
| opa.phys.quantum-information.quantum-communication-complexity-separations | Quantum Communication Complexity Exact Separations | high | mixed | medium | tier_2 |
| opa.phys.quantum-information.quantum-error-correction-fundamental-limits | Fundamental Limits of Quantum Error Correction | high | computational | medium | tier_1 |
| opa.phys.quantum-information.quantum-fault-tolerance-threshold-exact | Exact Quantum Fault Tolerance Threshold | medium | computational | high | tier_2 |
| opa.phys.quantum-information.quantum-gravity-information-connections | Quantum Gravity and Quantum Information Connections | low | expert_review | low | tier_3 |
| opa.phys.quantum-information.quantum-hamiltonian-complexity-qma | Quantum Hamiltonian Complexity and QMA-completeness | high | mixed | medium | tier_2 |
| opa.phys.quantum-information.quantum-key-distribution-optimal-rates | Optimal Key Rates in Quantum Key Distribution | high | computational | medium | tier_1 |
| opa.phys.quantum-information.quantum-reverse-shannon-theorem-extensions | Quantum Reverse Shannon Theorem Extensions | high | mixed | medium | tier_2 |
| opa.phys.quantum-information.quantum-shannon-capacity-regions | Quantum Shannon Theory Capacity Regions | medium | computational | medium | tier_2 |
| opa.phys.quantum-information.quantum-state-merging-generalizations | Quantum State Merging Generalizations | high | computational | medium | tier_1 |
| opa.phys.quantum-information.quantum-unique-games-conjecture | Quantum Unique Games Conjecture | high | mixed | medium | tier_2 |
| opa.phys.statistical-mechanics.3d-ising-model-phase-transition | Rigorous Analysis of the 3D Ising Model Phase Transition | high | computational | high | tier_1 |
| opa.phys.statistical-mechanics.conformal-invariance-criticality-general | Conformal Invariance at Criticality (General) | medium | mixed | medium | tier_2 |
| opa.phys.statistical-mechanics.dimer-model-3d | Dimer Model Exact Solutions in 3D | high | computational | medium | tier_1 |
| opa.phys.statistical-mechanics.griffiths-singularities-rigorous | Griffiths Singularities Rigorous Treatment | medium | mixed | medium | tier_2 |
| opa.phys.statistical-mechanics.kpz-universality-conjecture | KPZ Universality Conjecture | high | mixed | medium | tier_2 |
| opa.phys.statistical-mechanics.lee-yang-zeros-phase-transitions | Lee-Yang Zeros and Phase Transitions | high | mixed | medium | tier_2 |
| opa.phys.statistical-mechanics.percolation-threshold-exact-values | Percolation Threshold Exact Values | high | computational | medium | tier_1 |
| opa.phys.statistical-mechanics.random-matrix-universality | Random Matrix Theory Universality | high | mixed | medium | tier_2 |
| opa.phys.statistical-mechanics.self-avoiding-walk-connective-constant | Self-Avoiding Walk Connective Constant | high | computational | medium | tier_1 |
| opa.phys.statistical-mechanics.sle-conformal-invariance-3d-critical-phenomena | SLE and Conformal Invariance for 3D Critical Phenomena | medium | expert_review | medium | tier_3 |
| opa.phys.statistical-mechanics.spin-glass-parisi-ultrametricity | Spin Glass Theory and Parisi Ultrametricity | high | mixed | medium | tier_2 |
| opa.phys.statistical-mechanics.universality-critical-exponents-proof | Universality of Critical Exponents Proof | medium | expert_review | medium | tier_3 |

## 4. 需要人工复核的边界案例

| id | title | 当前分类 | 复核原因 |
| --- | --- | --- | --- |
| opa.phys.condensed-matter-theory.high-tc-superconductivity-mechanism | Mechanism of High-Temperature Superconductivity | low / expert_review / medium / tier_3 | 当前被标为 `low / expert_review / medium / tier_3`。问题本体像“研究计划 + 若干子问题”的打包项，建议拆成 Hubbard 模型、t-J 模型、配对机制三个更窄条目。 |
| opa.phys.quantum-field-theory.yang-mills-existence-and-mass-gap | Yang-Mills Existence and Mass Gap | medium / expert_review / low / tier_3 | 当前是 `medium / expert_review / low / tier_3`。其 canonical statement 已相当精确；需要人工确认库内对 `proof_assistant` 的含义是“原则上可形式化”还是“现实上近期可形式化”。 |
| opa.phys.general-relativity.stability-of-kerr-solution | Stability of the Kerr Solution | high / expert_review / low / tier_3 | 当前是 `high / expert_review / low / tier_3`。PDE 陈述很精确，但证明链条巨大；若未来 formalization 路线成熟，可能上调到 `proof_assistant`。 |
| opa.phys.quantum-information.quantum-fault-tolerance-threshold-exact | Exact Quantum Fault Tolerance Threshold | medium / computational / high / tier_2 | 当前是 `medium / computational / high / tier_2`。如果把“最一般噪声模型”收紧为固定噪声模型，它更像 `high`，可直接进 `tier_1`。 |
| opa.phys.quantum-field-theory.anomalous-magnetic-moment-theory | Muon Anomalous Magnetic Moment Theory Prediction | medium / computational / high / tier_2 | 当前是 `medium / computational / high / tier_2`。边界点在于“理论预测”的输入常数、强子贡献和模型约定是否被完全冻结。 |
| opa.phys.condensed-matter-theory.many-body-localization | Many-Body Localization | medium / expert_review / medium / tier_3 | 当前是 `medium / expert_review / medium / tier_3`。对象明确，但“何谓严格 MBL 相”在不同社群里定义不完全一致。 |
| opa.tcs.cryptography.black-box-separations | Black-Box Separations of Cryptographic Primitives | medium / expert_review / low / tier_3 | 当前是 `medium / expert_review / low / tier_3`。标题与 canonical statement 都是一个研究计划合集；应考虑拆成 `OWF -> PKE`、`OWF -> OT` 等独立条目。 |
| opa.tcs.quantum-computing.quantum-interactive-proofs | Quantum Interactive Proofs Structure | medium / expert_review / low / tier_3 | 当前是 `medium / expert_review / low / tier_3`。`MIP* = RE` 之后剩余问题被打包在一起，建议拆成 intermediate models / `QIP(k)` 等更窄问题。 |
| opa.mathematics.representation-theory.unitary-dual-problem | Unitary Dual Problem for Reductive Groups | medium / mixed / medium / tier_2 | 当前是 `medium / mixed / medium / tier_2`。对象和目标都明确，但“for all real reductive groups”使其更像按群族展开的计划，而非单一可直接形式化定理。 |
| opa.mathematics.mathematical-optimization.smale-18th-problem | Smale's 18th Problem | medium / computational / medium / tier_2 | 当前是 `medium / computational / medium / tier_2`。该问题的自然语言范围非常宽，建议拆成学习复杂度、优化极限、样本复杂度等独立问题。 |
| opa.mathematics.category-theory.deninger-program | Deninger's Program | high / expert_review / low / tier_3 | 当前是 `high / expert_review / low / tier_3`。虽然写成了存在性命题，但 “program” 语义很强，建议人工确认是否应降到 `medium`。 |
| opa.mathematics.logic-and-foundations.large-cardinal-hierarchy | Large Cardinal Consistency Strength Hierarchy | high / expert_review / low / tier_3 | 当前是 `high / expert_review / low / tier_3`。前半句是清晰的 inner model 问题，后半句又扩展成更广计划；建议拆分或改写 canonical statement。 |
| opa.tcs.complexity-theory.hardness-vs-randomness | Hardness vs Randomness Connections | high / expert_review / low / tier_3 | 当前是 `high / expert_review / low / tier_3`。第一问（`P = BPP` 是否蕴含 lower bounds）很精确，第二句 “更一般地” 又把条目拉宽。 |
| opa.phys.quantum-information.holographic-entanglement-entropy-conjectures | Holographic Entanglement Entropy Conjectures | medium / expert_review / low / tier_3 | 当前是 `medium / expert_review / low / tier_3`。标题本身就是复数 “conjectures”，很可能应拆成 Ryu-Takayanagi、QES、island formula 等独立条目。 |

人工复核优先级建议：

- **优先级 A：拆分型条目** — `high-tc-superconductivity-mechanism`、`black-box-separations`、`quantum-interactive-proofs`、`holographic-entanglement-entropy-conjectures`。这些不是简单“改一档”就够，而是更适合拆成多个更窄、可验证性更高的条目。
- **优先级 B：定义冻结型条目** — `quantum-fault-tolerance-threshold-exact`、`anomalous-magnetic-moment-theory`、`unitary-dual-problem`、`smale-18th-problem`。如果先冻结模型/参数族，它们可能上移到更高精度与更高 tier。
- **优先级 C：formalization 解释型条目** — `yang-mills-existence-and-mass-gap`、`stability-of-kerr-solution`、`hardness-vs-randomness`、`large-cardinal-hierarchy`、`deninger-program`。核心问题不是“是否重要”，而是库内把 `proof_assistant` 解释为理论上可形式化，还是近期现实可形式化。

## 5. 对 schema 修改的具体建议（JSON Schema patch）

由于 schema 与数据文件实际上已经包含这些字段，建议做的是**schema 加固**而不是再次“加字段”。最重要的三件事是：

1. 把 `verification_profile` 和 `tier` 提升到 top-level `required`。
2. 要求 `verification_profile` 内部三个子字段必须全部存在，并禁止额外键。
3. 用 `allOf + if/then` 把 `tier` 与三轴的逻辑一致性写进 schema，避免未来出现 `tier_1 + expert_review` 这类脏数据。

建议 patch 片段如下：

```diff
--- a/schema/problem.schema.json
+++ b/schema/problem.schema.json
@@
   "required": [
     "id",
     "kind",
     "title",
     "status",
     "domain",
     "subdomains",
     "statement",
-    "sources"
+    "sources",
+    "verification_profile",
+    "tier"
   ],
@@
     "verification_profile": {
       "type": "object",
+      "required": [
+        "statement_precision",
+        "solution_checkability",
+        "machine_actionability"
+      ],
+      "additionalProperties": false,
       "description": "Three-axis verification classification",
       "properties": {
         "statement_precision": {
           "type": "string",
           "enum": ["high", "medium", "low"]
         },
         "solution_checkability": {
           "type": "string",
           "enum": ["proof_assistant", "computational", "mixed", "expert_review"]
         },
         "machine_actionability": {
           "type": "string",
           "enum": ["high", "medium", "low"]
         }
       }
     },
@@
+  "allOf": [
+    {
+      "if": { "properties": { "tier": { "const": "tier_1" } }, "required": ["tier"] },
+      "then": {
+        "properties": {
+          "verification_profile": {
+            "properties": {
+              "statement_precision": { "const": "high" },
+              "solution_checkability": { "enum": ["proof_assistant", "computational"] },
+              "machine_actionability": { "enum": ["high", "medium"] }
+            }
+          }
+        }
+      }
+    },
+    {
+      "if": { "properties": { "tier": { "const": "tier_3" } }, "required": ["tier"] },
+      "then": {
+        "anyOf": [
+          {
+            "properties": {
+              "verification_profile": {
+                "properties": {
+                  "statement_precision": { "const": "low" }
+                }
+              }
+            }
+          },
+          {
+            "properties": {
+              "verification_profile": {
+                "properties": {
+                  "solution_checkability": { "const": "expert_review" }
+                }
+              }
+            }
+          }
+        ]
+      }
+    },
+    {
+      "if": { "properties": { "tier": { "const": "tier_2" } }, "required": ["tier"] },
+      "then": {
+        "properties": {
+          "verification_profile": {
+            "properties": {
+              "statement_precision": { "enum": ["high", "medium"] },
+              "solution_checkability": { "enum": ["proof_assistant", "computational", "mixed"] }
+            }
+          }
+        },
+        "not": {
+          "properties": {
+            "verification_profile": {
+              "properties": {
+                "statement_precision": { "const": "high" },
+                "solution_checkability": { "enum": ["proof_assistant", "computational"] },
+                "machine_actionability": { "enum": ["high", "medium"] }
+              }
+            }
+          }
+        }
+      }
+    }
+  ],
   "additionalProperties": false
 }
```

### 5.1 附加架构建议

- 如果下一步真的要把这套系统用作 UI 过滤器或 agent 路由器，建议再新增一个**非 schema 强制**字段：`verification_profile_notes`，专门记录“为什么是 medium 而不是 high”。
- 对所有 `tier_3` 且 `statement_precision != low` 的条目，建议增加拆分/改写 backlog，因为这批问题通常不是“不精确”，而是“单条目里捆了太多问题”。
- 可以把 `scores.formality/toolability/ai_fit` 与 `verification_profile` 做一致性检查脚本：不是强制相等，但当 `statement_precision=low` 且 `formality>=0.80` 时自动报警，供人工复核。
