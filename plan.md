这个 idea 有戏，但前提是你别把它做成“爬虫收集宇宙级难题”的内容站，而要把它做成**开放难题基础设施**。我不能真实保证“70% 会高 star”，但可以按“在这个 niche 里把命中率尽量拉高”的方式，给你一套最完整、最能打的版本。

我先给你一句最核心的判断：

**单纯的 open question 列表不会高 star；高 star 版本一定是「结构化数据 + 可验证来源 + 动态更新 + AI/人类可复现实验 + 一个做得很像产品的 GitHub 仓库」五件套。**

而且这个方向现在确实有窗口期。HLE 已经把“超难专家题”做成了 2500 题的集合，并且出了滚动版本 HLE-Rolling；OpenAI 的 FrontierScience 把难题评测扩展到物理、化学、生物的专家级科研任务；Epoch 的 FrontierMath 是 350 道专家编写的高难数学题，典型需要数小时到数天去做，论文里当时的最强模型整套题解出不到 2%；Google DeepMind 则在 IMO 2025 拿到了金牌级表现。也就是说，“frontier reasoning / AI for science / hard problems” 现在是大家看得懂、愿意转发、也愿意 star 的叙事。([AGI Safe][1])

相邻开源赛道也已经证明有受众。Open Problem Garden 本身就是一个数学未解问题集合；Erdős Problems 用 YAML 作为 ground truth，再自动生成可交互表格，目前大约 499 stars；Google DeepMind 的 formal-conjectures 把 conjecture statement 形式化到 Lean，目前大约 850 stars；更泛的 awesome-ai-for-science 也有大约 1.3k stars。你这个项目如果把“问题数据库 + 形式化入口 + AI-ready 数据 + live explorer”合成一个仓库，潜在上限会比单独做其中一条更高。这里我建议把“高 star”先定义成 **6–12 个月 1k+**；这是这个细分赛道里比较现实、也比较有成就感的目标带。([Open Problem Garden][2])

---

## 一、我建议你最终做成的 repo 形态

### 工作名

**`open-problem-atlas`**

这个名字不一定最终采用，但定位一定要是这个味道：
**A living, machine-readable atlas of open problems for researchers, AI agents, and theorem provers.**

### 一句话定位

把分散在论文、问题集、社区页面、专家维护列表里的 open problems，做成一个**可检索、可验证、可贡献、可追踪 AI 尝试**的开源公共基础设施。

### 你的主叙事

不是“AI 去解宇宙级难题”。

而是这句：

**很多问题之所以一直没人做，不只是因为难，还因为它们分散、难找、难比较、缺少可操作入口。**

这句就是你截图里最值钱的洞见。它比“AI 炒作难题”高级得多，也更容易得到研究者、学生、theorem proving 社区、AI eval 社区的认同。

### 目标用户

先盯四类人：

1. 想找 research direction 的学生和研究者。
2. 做 LLM reasoning / theorem proving / agent 的工程师和研究者。
3. 想把问题 formalize 到 Lean/Coq 的社区。
4. 想找“underexplored but meaningful”题目的独立研究者。

### 明确不做什么

这个很重要，不然 scope 会炸：

1. **不做新闻聚合站。**
   新闻、自媒体、公众号只能当 discovery seed，不能当 canonical source。

2. **不做泛泛而谈的“未来工作”垃圾池。**
   没有精确定义的问题，不进 verified 区。

3. **不做“AI 已经解决了某个 open problem”的营销仓库。**
   AI 生成内容只能放在 attempts/lab 区，默认不算事实。

4. **不从第一天就做全学科。**
   v1 先做精确、可结构化、可验证的 formal-ish 领域。

---

## 二、最能打的产品结构：不要一个仓库只放一堆 markdown

这个 repo 应该是四层结构，而不是一个 README。

### 1）Atlas：已验证的问题层

这是项目的“真相层”。

每条问题卡片都必须有：

* 规范标题
* 精确定义或 canonical statement
* 来源
* 现在的状态（open / solved / disproved / ambiguous / etc.）
* 至少一个状态依据
* 人工 review 记录
* related work / partial results
* AI/工具可操作标签

**这里的原则：宁可少，不可脏。**

### 2）Radar：自动挖掘的候选问题层

这是你的爬虫和大模型最该发力的地方。

它不是“真相层”，而是“雷达层”：

* 从论文的 open problems / conjecture / discussion / future work 段落中抽取候选
* 从专家维护列表和社区资源里发现新条目
* 自动归类、打分、聚类
* 进入 review 队列

**Radar 可以 noisy，Atlas 绝不能 noisy。**

这两个层分开，是这个项目最关键的架构决定之一。

### 3）Lab：AI / 人类尝试层

这层是你抓 attention 的地方，但不能污染真相层。

这里放：

* LLM 的 literature review
* decomposition / lemma proposals
* brute-force / SAT / symbolic search 尝试
* Lean formalization 尝试
* counterexample search
* reproducible notebooks
* prompt / model / tool / commit hash / date

默认标签必须是：

* `unverified`
* `machine-generated` 或 `hybrid`
* `not canonical`

### 4）Graph / Explorer：展示和传播层

这是高 star 的关键，不然别人只会觉得你是“一个 data dump”。

必须做的展示能力：

* 全局搜索
* 多维筛选
* 关系图谱
* featured collections
* recently added / recently solved
* formalizable / solver-ready / underexplored 过滤
* 问题详情页

---

## 三、v1 的边界一定要收得极狠

你截图里提到图论、宇宙弦、各种“宇宙级问题”。我的建议是：

### v1 只做三块

1. **Mathematics**
2. **Theoretical CS**
3. **Mathematical physics / quantum information 里那些表述足够精确的问题**

### v1 不做

* 生物/化学里的广义 research questions
* 宏大叙事式“physics mysteries”
* 需要大量实验背景才能理解的问题
* 只能靠新闻稿复述的问题

原因很简单：
你这个项目第一性原理是**精确、可验证、可结构化**。
数学、理论 CS、量子信息最适合做第一版本。

### v1 发版门槛

我建议你不给自己留太多幻想，直接定死 launch 线：

* **300 个 verified problems**
* **1000 个 radar leads**
* **20 个 gold-standard 详情页**
* **至少 3 个 collection 页面**
* **至少 1 个 AI attempt demo**
* **站点可搜索、可筛选、可下载 JSON/Parquet**
* **每条 verified problem 都有 source + status evidence + last reviewed**

达不到这个标准，不要急着冲 Product Hunt / HN / Reddit。

---

## 四、数据模型要像“公共数据库”而不是“文章合集”

你的 canonical record 我建议长这样。用 YAML/JSON 都行，但对贡献者更友好的通常是 YAML。

```yaml
id: opa.math.nt.collatz
kind: problem
title: Collatz conjecture
aliases:
  - 3x+1 problem

status:
  label: open
  confidence: high
  last_reviewed_at: 2026-03-01
  review_state: human_verified

domain: mathematics
subdomains:
  - number-theory
  - dynamical-systems

problem_type: conjecture
answer_type: boolean
verification_mode: expert_review

statement:
  canonical: >
    For every positive integer n, repeated iteration of ...
  informal: >
    Starting from any positive integer, the sequence eventually reaches 1.

why_it_matters: >
  Central toy problem with deep links to dynamical systems and number theory.

prerequisites:
  - elementary-number-theory
  - recurrence-relations

sources:
  canonical:
    - source_id: src_001
      kind: problem_list
      locator: "Problem #..."
  status_evidence:
    - source_id: src_014
      kind: survey
      locator: "Section 2"

partial_results:
  - summary: "Verified up to ..."
    source_id: src_021

relations:
  equivalent_to: []
  generalizes: []
  special_cases: []
  related_sequences: []

formalization:
  available: false
  systems: []
  wanted: true

scores:
  impact: 0.91
  underexplored: 0.22
  toolability: 0.67
  formality: 0.94
  ai_fit: 0.74

ai:
  solver_ready: true
  recommended_tools:
    - python
    - sat
    - lean

machine_generated:
  summary: >
    ...
  decomposition:
    - ...
  disclaimer: unverified

provenance:
  created_from: open_problem_garden
  parser_version: 0.3.1
  schema_version: 1.0.0
```

### 这里面最重要的不是字段多，而是字段分层

你必须把字段分成四类：

#### A. 事实字段

这些必须有来源，且可审计：

* title
* canonical statement
* status
* sources
* partial results
* formalization links
* prize / bounty
* dates

#### B. review 字段

这些是治理层：

* last_reviewed_at
* reviewer
* review_state
* confidence
* stale_after

#### C. ranking 字段

这些是产品层：

* impact
* underexplored
* toolability
* formality
* ai_fit

#### D. machine-generated 字段

这些是实验层：

* LLM summary
* decomposition
* suggested keywords
* relation candidates

**绝不能让 D 混进 A。**

---

## 五、状态体系要借鉴成熟项目，但再加两个工程态字段

这个项目的数据组织方式，直接借鉴两个成熟模式就够了：
`erdosproblems` 的做法是一个 ground truth 数据文件驱动整个站点；`formal-conjectures` 的做法是把 open / solved / formally solved 以及 subject tags 显式结构化。你应该把这两种思路揉在一起。([GitHub][3])

### 我建议的状态枚举

对 verified problems：

* `open`
* `partially_solved`
* `solved`
* `disproved`
* `conditional`
* `independent`
* `ambiguous`
* `retired_duplicate`

对工程流程：

* `lead_unverified`
* `needs_status_refresh`

这两个工程态字段很关键，因为现实里很多候选项你没法立即确认；很多老问题你也需要周期性重新确认状态。

### 状态变更规则

从 `open -> solved/disproved` 的状态切换，必须满足：

1. 有 primary evidence
2. 有人工 reviewer
3. 最好附 status history
4. 不删原条目，只做状态演化

---

## 六、这个项目真正的护城河，是“来源策略”而不是“模型有多大”

像你截图里那种新闻稿、自媒体文章，只能作为**发现入口**，不能作为**规范来源**。这是生死线。

### Source priority 应该这样分

#### Tier 1：可做 canonical source

* 明确的问题集 / problem list
* 论文原文
* survey / textbook
* 专家维护的 open problem 页面
* formalized conjecture repositories

#### Tier 2：可做辅助状态来源

* 社区高质量讨论
* benchmark 论文
* 专题综述
* authoritative databases

#### Tier 3：只能做 lead source

* 新闻
* 公众号/博客
* 二手解读
* 视频口述

---

## 七、技术架构：先做 source adapter，不要先做大而全爬虫

工程上我建议你先走“source adapter”而不是“全网通用爬虫”。论文 metadata 与引用链优先走官方接口：OpenAlex 提供免费 key 和免费额度说明，Crossref 支持 polite pool，Semantic Scholar 官方文档给出 key 的初始 1 RPS，arXiv 则明确要求遵守 API Terms、加入 acknowledgement，并避免任何看起来像官方背书的品牌使用。先吃这些高质量入口，v1 会稳得多。([OpenAlex][4])

### 推荐的 ingestion 顺序

先高精度，后高召回：

1. **Curated source adapters**
   Open Problem Garden / erdosproblems / formal-conjectures / named problem lists / benchmark pages

2. **Literature adapters**
   arXiv / Crossref / OpenAlex / Semantic Scholar

3. **Web leads**
   blog/news/wiki/forum，只进 radar

### 管道设计

完整 pipeline 应该是：

`source adapter -> raw source record -> section splitter -> candidate extractor -> status classifier -> alias linker -> dedupe -> reviewer queue -> publish build`

### 每一步做什么

#### source adapter

负责把外部内容变成统一 `source` 结构。

#### section splitter

识别：

* Open Problems
* Conjectures
* Discussion
* Future Work
* Problem list entries

#### candidate extractor

用规则 + LLM，把“疑似 open problem”的候选句段抽出来。

#### status classifier

判断是：

* 真 open problem
* solved result
* future work
* vague agenda
* non-problem

#### alias linker

把不同叫法合并成一个问题簇。

#### dedupe

防止同一问题被多个来源重复收录。

#### reviewer queue

所有高价值候选都必须经过人工关卡。

#### publish build

从 canonical data 自动生成站点、搜索索引、release artifacts。

---

## 八、不要把系统搭太重：v1 就是 monorepo + static site

我建议你一开始就做 **monorepo**，别拆多仓库。
原因很现实：stars 要集中，贡献入口要单一，维护成本要低。

### 目录结构建议

```text
open-problem-atlas/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CITATION.cff
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── add-problem.yml
│   │   ├── propose-lead.yml
│   │   ├── report-status-change.yml
│   │   ├── add-source.yml
│   │   ├── add-ai-attempt.yml
│   │   └── config.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── validate.yml
│       ├── build-site.yml
│       ├── refresh-radar.yml
│       ├── release-snapshot.yml
│       └── lint-data.yml
├── docs/
│   ├── manifesto.md
│   ├── taxonomy.md
│   ├── source-policy.md
│   ├── review-guidelines.md
│   ├── attempt-policy.md
│   ├── architecture.md
│   └── zh/
├── schema/
│   ├── problem.schema.json
│   ├── source.schema.json
│   ├── attempt.schema.json
│   └── collection.schema.json
├── data/
│   ├── problems/
│   │   ├── mathematics/
│   │   ├── theoretical-cs/
│   │   └── mathematical-physics/
│   ├── leads/
│   ├── attempts/
│   ├── collections/
│   └── snapshots/
├── ingestion/
│   ├── adapters/
│   ├── parsers/
│   └── jobs/
├── extraction/
│   ├── prompts/
│   ├── classifiers/
│   ├── dedupe/
│   └── ranking/
├── review/
│   ├── checklists/
│   └── validators/
├── site/
│   ├── app/
│   ├── components/
│   └── build/
├── api/
│   └── read-only/
├── scripts/
├── tests/
└── notebooks/
```

### v1 的存储策略

* **repo 里只放 canonical data 和可公开分发的衍生数据**
* 原始全文、抓下来的网页、PDF cache 不要直接 commit
* 只存 metadata、locator、必要短摘录、你自己的结构化注释

这一步会极大降低版权和维护风险。

---

## 九、真正高 star 的核心功能，不是“题多”，而是“能用”

### 你至少要做出这五个 killer features

#### 1）Underexplored filter

这个是你最有差异化的点。

不是只给 famous problems，而是能找：

* 重要
* 精确
* 有工具入口
* 最近关注度不高
* 还没有被整理烂的题

你可以做一个 heuristic：

`underexplored = impact high + statement precision high + recent attention low + toolability not too low`

#### 2）Formalizable filter

吸 theorem proving 社区。

标签例子：

* `formalizable`
* `lean-linked`
* `formalization-wanted`

#### 3）Solver-ready filter

吸 agent / LLM / search 社区。

标签例子：

* `has-exact-answer-shape`
* `computational-search-possible`
* `sat-smt-friendly`
* `python-checkable`
* `counterexample-friendly`

#### 4）Radar page

让仓库不是静态死库，而是“每周有新发现”。

页面要能看：

* newest leads
* hot sources
* needs review
* recently promoted to verified

#### 5）Attempts page

展示 AI / 人类怎么试的，但要非常克制：

* 只放可复现尝试
* 标清模型/作者
* 标清状态
* 能看到失败也有价值

---

## 十、LLM 应该用在什么地方，绝不能用在什么地方

你有 API、卡、cloud，这当然能上，但用错地方会把仓库做废。

### LLM 适合干的事

1. 抽 candidate open problems
2. 生成 alias / keyword 候选
3. 归纳 partial results
4. 生成短摘要
5. 生成 relation candidates
6. 给 attempts 生成结构化报告

### LLM 绝不能单独决定的事

1. 一个问题到底 open 不 open
2. canonical statement 是什么
3. 这个证明是不是成立
4. 这个状态是不是应该从 open 改成 solved
5. 这是不是某个已知问题的重复项

### 成本策略

最省钱也最稳的做法：

* 小模型做大规模 triage
* 大模型只打 shortlist
* 所有输出都缓存
* 所有 prompt/version 都记录
* 所有 machine fields 都可追溯

---

## 十一、CI 和质量门槛，不严格的话你会很快烂尾

这个项目一定要有数据 CI，不然 contributors 一多就会乱。

### 每个 verified problem 必须通过的检查

* `id` 唯一
* `slug` 唯一
* 有 canonical statement
* 有至少一个 canonical source
* 有至少一个 status evidence
* 有 domain / subdomain
* 有 last_reviewed_at
* machine-generated 字段带 disclaimer
* 关系引用的 problem id 存在
* 外链格式和 locator 合法

### 每个 status change PR 必须通过的检查

* 附 primary evidence
* 附 status history note
* 至少一个 domain reviewer approve
* 从 `open -> solved/disproved` 需要 maintainer approve

### 每个 attempt 必须通过的检查

* problem_id 存在
* actor/model/version 存在
* prompt 或 method 摘要存在
* 工具和环境存在
* 明确标注 `verified` / `unverified`

---

## 十二、分阶段路线图：每个阶段的目标、难点、注意点、检查点

下面这部分我按“一个人主导，几个月内能拉起来”的方式写。

---

### Phase 0（第 1 周）：定 thesis 和边界

**目标**
把项目从“我想收集 open questions”收敛成一句可传播、可执行的话。

**产出**
`manifesto.md`、`taxonomy.md`、`source-policy.md`，以及 50 条人工挑选的 seed examples。

**最大难点**
scope creep。你会很想把所有学科都装进来，最后什么都不精。

**需要注意的点**
先把每条内容分成三类：`problem`、`lead`、`attempt`。这一刀不切开，后面全部混在一起。

**验证检查点**
拿 50 条 seed example，让两个人独立判断它到底属于 problem / lead / 非问题，分类一致率至少要到 80% 以上。不到这个程度，说明 taxonomy 还没定稳。

---

### Phase 1（第 2–3 周）：做 gold set 和 schema

**目标**
先做一个极小但极准的“真相层”。

**产出**

* `problem.schema.json`
* `source.schema.json`
* `attempt.schema.json`
* 30–50 条 fully annotated verified problems
* 数据 lint 和 pre-commit

**最大难点**
“同一个问题多个名字”和“问题状态含糊”。

**需要注意的点**
所有事实字段必须有 provenance。
所有生成字段必须单独分区。
所有 verified items 必须能追溯到 canonical source。

**验证检查点**
100% gold items 都能通过 schema；
100% gold items 都有 status evidence；
任意抽 10 条，维护者能在 1 分钟内找到状态依据。

---

### Phase 2（第 4–5 周）：source adapters + ingestion

**目标**
把高质量来源接进来，形成自动更新的 source layer。

**产出**

* curated source adapters
* literature adapters
* raw source normalization
* nightly/weekly jobs
* fetch cache

**最大难点**
来源异构：HTML、PDF、列表页、论文页、数据库页格式完全不同。

**需要注意的点**
先 API，后 scraping。
先 metadata，后 full text。
先高精度来源，后高召回来源。
不要把 raw fulltext 全部 commit 到仓库。

**验证检查点**
从 500 个样本来源里，metadata fetch 成功率 > 90%；
source normalization 后关键字段缺失率 < 10%；
没有任何违反来源条款的抓取策略上线。

---

### Phase 3（第 6–7 周）：candidate extraction + dedupe

**目标**
把“会挖”这件事真正做起来。

**产出**

* open-problem candidate classifier
* alias linker
* dedupe pipeline
* lead scoring
* radar feed

**最大难点**
“future work” 和 “真正的 open problem” 很容易混。
“我们 conjecture” 和 “这个 conjecture 已被解决” 也容易混。

**需要注意的点**
分类器必须允许 `abstain`。
低置信度候选宁可进 `needs_review`，也不要自动升格成 verified。
dedupe 必须分三级：exact match、high-confidence alias、human merge。

**验证检查点**
在标注集上：

* candidate extraction precision ≥ 80%
* open/solved status classification 的严重错误率 ≤ 5%
* dedupe precision ≥ 95%

---

### Phase 4（第 8–9 周）：review workflow 和治理层

**目标**
让项目不是“你一个人的笔记”，而是“别人可以安全参与的公共仓库”。

**产出**

* issue forms
* PR template
* review checklist
* roles（maintainer / domain reviewer / contributor）
* status change policy

**最大难点**
专家 review 是瓶颈。

**需要注意的点**
v1 不要自建复杂 admin panel，直接用 GitHub issue + PR workflow。
新问题一个 reviewer 就够；状态变更至少一个 reviewer + 一个 maintainer。
从 `open -> solved/disproved` 最严。

**验证检查点**
外部贡献者在 10 分钟内能完成一次 `propose-lead` 或 `add-problem`；
review checklist 能覆盖 90% 以上常见错误；
首个外部 PR 不需要你手把手解释 20 分钟。

---

### Phase 5（第 10–11 周）：site / explorer / API

**目标**
把仓库做出“第一眼就值得 star”的感觉。

**产出**

* 首页
* problems explorer
* radar page
* attempts page
* collections page
* 静态导出的 JSON/Parquet
* 只读 API

**最大难点**
很多项目数据没问题，但展示层太弱，第一眼没有 wow。

**需要注意的点**
首页默认一定是**可用的列表视图**，不要只放炫酷 graph。
graph 视图只能是第二视图。
用户第一眼应该看到：这是什么、收录多少、能怎么筛、点进去是什么样。

**验证检查点**
找 5 个外部测试者，给他们 60 秒：
能不能找到一个 `formalizable` 问题；
能不能找到一个 `underexplored` 问题；
能不能下载一份数据。
做不到，就继续打磨。

---

### Phase 6（第 12 周）：Lab / AI attempts / reproducible demos

**目标**
补上最抓眼球的那一层，但不伤 credibility。

**产出**

* attempt spec
* 3–5 个代表性 notebook
* 统一 attempts schema
* “AI tried this” 页面
* demo video / gif

**最大难点**
AI 内容很容易失控，仓库会从“基础设施”变成“幻觉博物馆”。

**需要注意的点**
attempt 默认不进入 canonical page 的事实区域。
显示 attempt 时必须同时显示：

* actor/model
* version
* date
* tools
* prompt/method summary
* verification status
* limitations

**验证检查点**
100% attempts 可追溯；
100% attempts 有 `verified/unverified` 标记；
0 条 unverified AI claim 混进 verified problem truth layer。

---

### Phase 7（上线周）：GitHub 包装和首发

**目标**
把“好项目”变成“会被 star 的项目”。

**产出**

* 完整 README
* social preview image
* GIF / demo
* launch thread
* 3 篇 collection 页面
* monthly snapshot release

**最大难点**
很多项目技术做完了，但不会 launch。

**需要注意的点**
README 必须英文优先，中文镜像文档单独放 `docs/zh/`。
首屏必须 15 秒内解释清楚价值。
不要写成论文摘要；要写成产品 landing page。

**验证检查点**
72 小时内你至少应该拿到：

* 一批 stars
* 第一批外部 issues
* 至少一个外部 PR 或 correction
* 至少一个社区转载/讨论点

---

### Phase 8（上线后 1–2 个月）：Rolling benchmark / monthly snapshots

**目标**
从“数据库”升级成“活的 benchmark / radar infrastructure”。

**产出**

* monthly frozen snapshot
* changelog
* `rolling` collection
* contamination-aware eval subset
* benchmark protocol 文档

**最大难点**
一旦自称 benchmark，就要面对 freshness、污染、评测公平性。

**需要注意的点**
先 atlas，后 benchmark。
不要一开始就把所有公开问题都叫 eval。
rolling subset 必须和主库分开维护。

**验证检查点**
能稳定产出每月 snapshot；
每个 snapshot 都能复现；
新旧版本差异可追踪。

---

## 十三、GitHub 本身要像产品一样打磨

GitHub 包装不是小事。官方 community profile 会检查 README、CODE_OF_CONDUCT、LICENSE、CONTRIBUTING、issue templates 等健康文件；issue forms 需要放在 `.github/ISSUE_TEMPLATE`；仓库链接还支持自定义 social preview 图，而且 GitHub 建议最佳展示尺寸至少 1280×640。高 star 仓库通常不是“把代码推上去”，而是首屏就告诉别人：这是什么、为什么有用、怎么参与。([GitHub Docs][5])

### README 首屏建议直接这么写

```md
# OpenProblemAtlas
> A living, machine-readable atlas of open problems for researchers, AI agents, and theorem provers.

Discover verified open problems, mine fresh leads from the literature, and track reproducible AI/human attempts — all in one open dataset.

- Verified problems
- Fresh radar leads
- Formalization links
- Reproducible attempts
- JSON / Parquet snapshots

[Explore the Atlas] [Browse Radar] [Contribute a Problem] [Download Data]
```

### Issue forms 至少要有这几个

* `add-problem.yml`
* `propose-lead.yml`
* `report-status-change.yml`
* `add-source.yml`
* `add-ai-attempt.yml`

### label 体系

* `type:problem`
* `type:lead`
* `type:attempt`
* `domain:math`
* `domain:tcs`
* `domain:physics`
* `needs-review`
* `good-first-entry`
* `status-change`
* `formalization-wanted`
* `solver-ready`

---

## 十四、最容易失败的地方

### 1）一上来就全学科

结果是每个领域都只懂一点点，没有一个领域够深。

**解法**：v1 只打 formal-ish 领域。

### 2）把 AI 生成内容混进事实层

这会直接毁掉声誉。

**解法**：三层分离：problem / lead / attempt。

### 3）太早做复杂后端

你会把时间浪费在 infra，而不是价值本身。

**解法**：repo + GitHub Actions + static site 先跑起来。

### 4）来源不干净

新闻稿、博客、二手文章会让数据越来越脏。

**解法**：source priority，严格区分 canonical vs lead。

### 5）没有 review 机制

最后就变成你个人笔记仓库，别人不敢参与。

**解法**：issue forms + PR review + domain reviewer。

### 6）只做 list，不做 explorer

别人看完 README 就走，不会 star。

**解法**：必须有 live explorer 和 collections。

---

## 十五、首批应该开出来的 12 个 issues

1. Define problem/lead/attempt taxonomy
2. Draft `problem.schema.json`
3. Build data validator + pre-commit
4. Curate first 50 gold problems
5. Add `erdosproblems` adapter
6. Add `formal-conjectures` metadata bridge
7. Add `open_problem_garden` adapter
8. Add OpenAlex/Crossref/Semantic Scholar source normalization
9. Build candidate extraction classifier
10. Build alias linker + dedupe pipeline
11. Build explorer homepage + filters
12. Write review guidelines + status change policy

这 12 个 issue 不是形式主义，而是你项目从“想法”变成“仓库”的最短路径。

---

## 十六、最后给你一个最直白的版本

你这个 repo 的 winning version，不是：

**“AI 去解世界难题。”**

而是：

**“OpenProblemAtlas：把分散的 open problems、recent leads、formalization 入口、AI/human attempts 结构化成一个可搜索、可验证、可贡献、可复现实验的公共基础设施。”**

这才是最有机会冲到高 star 的版本。

真正的 killer move 也不是先写大规模云爬虫，而是先把这三件事做准：

1. **taxonomy**
2. **schema**
3. **50 个金标 seed problems**

这三步一旦定稳，后面的 cloud、agent、批量 extraction、weekly radar、rolling benchmark 都是顺水推舟。反过来，这三步不稳，后面算力越多，噪音越大。

[1]: https://agi.safe.ai/ "https://agi.safe.ai/"
[2]: https://www.openproblemgarden.org/ "https://www.openproblemgarden.org/"
[3]: https://github.com/teorth/erdosproblems "https://github.com/teorth/erdosproblems"
[4]: https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication "https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication"
[5]: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories "https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories"
