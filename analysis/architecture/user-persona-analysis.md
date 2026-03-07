---
analyzer: codex/gpt-5.4
reasoning: xhigh
date: 2026-03-08
task: User persona and product strategy analysis
scope: Full project
---

# 先把话说死

如果这个项目要走**纯机器闭环**，那它就**不是**现在文档里写的那种“社区治理 + 人工 review 的 open problem atlas”。它会变成另一种东西：**给自动化求解系统、验证系统、评测系统用的任务基础设施**。

现在仓库的现实很直接：

- `docs/manifesto.md`、`docs/attempt-policy.md`、`docs/source-policy.md`、`review/queue.py` 全都默认**人类在真相层把关**。
- 当前数据快照是：`312` 个 problems、`944` 个 leads、`3` 个 attempts。
- `analysis/architecture/verification-profile-plan.md` 显示其中 `175` 个是 `tier_1`，但这只是“理论上较适合机器”，**不是已经可跑**。
- `144` 个是 `proof_assistant`，`88` 个是 `computational`，`31` 个还是 `expert_review`。后者在纯机器闭环里基本等于没法闭环。
- `311` 个问题 `formalization.wanted=true`，只有 `1` 个 `formalization.available=true`。
- `ai.solver_ready=true` 的问题数是 `0`。
- `3` 个 attempt 全是 `unverified`。

结论很简单：**现在这个仓库不是“机器闭环产品”，只是“想往机器友好方向长”的数据仓。** 如果继续拿“researchers, AI agents, theorem provers”一起说，定位会继续发散。你得砍。

---

# 1. 用户画像重新定义

## 1.1 核心用户到底是谁

既然不要人 review，核心用户就不再是“想浏览 open problem 的人”。核心用户是：

> **运行自动化求解、验证、评测流水线的人和系统。**

说白了，真正的“用户”不是数学家本人，而是下面这几类东西：

1. 跑 frontier reasoning / theorem proving / agent benchmark 的团队。
2. 维护 Lean / SAT / SMT / Python checker 验证基础设施的人。
3. 想把“尝试 → 自动验证 → 自动记账”变成稳定流水线的 infra 工程师。
4. 需要一批**可执行、可复现、可计分**任务的评测/数据集设计者。

如果还把“核心用户”写成“学生和研究者”，那是在自欺欺人。学生会看，但不会决定产品成败。**决定成败的是：机器能不能直接拿来跑。**

## 1.2 Persona 划分（至少 4 个）

## Persona A：前沿推理评测工程师（Model Lab Eval Engineer）

**目标**：给模型/agent 跑持续评测，不想再用已经被训练集污染烂掉的老题。

**他要什么**：
- 一批**活的**、持续更新的问题集，不是死 benchmark。
- 每题有明确验证合同：能不能自动验、怎么验、资源预算多少。
- 每次运行有快照、attempt trace、可复现 artifact。

**他怎么用 atlas**：
- 拉取月度 snapshot。
- 过滤出 `tier_1`、`computational` 或 `proof_assistant` 的题。
- 把题喂给 agent pipeline。
- 自动收集 pass/fail/timeout/invalid/counterexample 等结果。
- 对比不同模型、不同 prompting、不同工具链的产出。

**典型 workflow**：
1. 选定 `snapshot-YYYY-MM-DD`。
2. 按 `verification_profile` 切分任务池。
3. 批量运行 baseline agent。
4. 自动验证。
5. 生成 leaderboard、failure breakdown、artifact 索引。

---

## Persona B：Lean 4 形式化流水线维护者（Formalization Operator）

**目标**：把“可形式化但没形式化”的问题，变成可编译、可检查、可累积的 theorem backlog。

**他要什么**：
- 精确 statement，不是散文。
- Lean 入口、stub、Mathlib 版本锁定、构建脚本。
- 失败也要留下机器可消费的错误轨迹。

**他怎么用 atlas**：
- 只看 `solution_checkability=proof_assistant` 且 `statement_precision=high` 的题。
- 自动生成 theorem stub / skeleton。
- 让模型尝试 formalization。
- 用 Lean 编译器当裁判，不听模型吹牛。

**典型 workflow**：
1. 过滤 high-formality 题。
2. 生成 Lean task package。
3. LLM 产出 `.lean` 文件。
4. `lake build` / `lean --run` 自动检查。
5. 记录 compile errors、通过率、依赖缺失、未解决 lemma。

---

## Persona C：SAT/SMT/搜索求解管道工程师（Solver Pipeline Engineer）

**目标**：找那些能转成证书搜索、反例搜索、界值验证的问题，狠狠干自动搜索。

**他要什么**：
- 问题是否适合 SAT/SMT/ILP/枚举，不要模棱两可。
- witness/counterexample 的 schema。
- checker 必须独立于 solver 本体，不能自说自话。

**他怎么用 atlas**：
- 只看 `solution_checkability=computational` 或 `mixed` 且 machine_actionability 高的题。
- 拉取 encoding spec。
- 跑 solver，产出证书或反例。
- 由独立 checker 二次验证。

**典型 workflow**：
1. 选问题。
2. 生成 encoding。
3. 并行跑 SAT/SMT/MIP/枚举器。
4. 得到 witness/certificate。
5. 用 checker 验真并自动入账。

---

## Persona D：Agent 平台 / Research Ops 负责人（Closed-loop Orchestrator）

**目标**：不是解一道题，是维护一个**持续运转的尝试工厂**。

**他要什么**：
- 任务队列。
- 预算控制。
- 失败分类。
- 自动重试策略。
- attempt ledger 和可追溯 artifact 存储。

**他怎么用 atlas**：
- atlas 不是阅读界面，而是**任务注册表 + 验证路由表**。
- 根据题目类型把任务发给不同 agent / tool backend。
- 根据验证结果决定继续搜索、换策略还是放弃。

**典型 workflow**：
1. 任务进入 queue。
2. planner 按 profile 分流。
3. worker 生成 proof sketch / code / encoding / witness。
4. verifier 判断结果。
5. recorder 写入 attempt ledger。
6. scheduler 重新排序下一轮候选。

---

## Persona E：Frontier Benchmark 设计者（Dataset Curator）

**目标**：做一个比 MATH / miniF2F 更新鲜、比 Open Problem Garden 更可跑的 frontier benchmark。

**他要什么**：
- 去污染说明。
- 冻结快照。
- 题目元数据标准化。
- attempt 和 verifier 结果都能导出。

**他怎么用 atlas**：
- 从 atlas 切出 benchmark split。
- 冻结验证器版本。
- 发布 baseline 结果与 replay 脚本。

**典型 workflow**：
1. 选择一个版本快照。
2. 过滤出机器可检的题。
3. 生成 benchmark subset。
4. 跑 baseline。
5. 发布 JSON + Parquet + artifacts + report。

## 1.3 Persona 的共同需求

这几类用户虽然表面不同，但底层只关心三件事：

1. **题目是不是机器真的能开跑。**
2. **结果是不是机器真的能验。**
3. **失败是不是能留下下次还能用的轨迹。**

如果 atlas 做不到这三件事，那它对纯机器用户就只是“好看但没法接进流水线的网页”。那没用。

---

# 2. 产品定位重新思考

## 2.1 纯机器闭环下，这个 atlas 本质上是什么

一句话：

> **它不是 open problem 百科，而是 frontier problem 的机器任务基础设施。**

更准确一点：

> **它是一个带验证合同（verification contract）的任务注册表，外加 attempt ledger 和可执行 verifier。**

也就是说，atlas 在纯机器闭环里至少要承担四个角色：

1. **任务目录**：问题是什么。
2. **验证路由**：这题该走 Lean、SAT/SMT、Python checker 还是根本不该进机器池。
3. **运行账本**：谁试过、怎么试的、结果是什么。
4. **快照基线**：哪个版本的题、哪个版本的 verifier、哪个版本的工具链。

没有这四层，你就不是基础设施，只是内容站。

## 2.2 与现有竞品的差异化

| 项目 | 本质 | 强项 | 致命缺口（相对纯机器闭环） |
| --- | --- | --- | --- |
| Open Problem Garden | 人类阅读用的问题花园 | 可读性、选题趣味性 | 不是任务基础设施，没有统一 verifier / attempt ledger |
| Polymath | 人类协作研究机制 | 讨论、共创、社会动员 | 完全不是机器流水线；验证依赖人类共识 |
| Lean mathlib | 已知数学的形式化库 | 形式化基础设施极强 | 不是 open problem registry，也不负责 frontier task orchestration |
| ProofNet / miniF2F | 形式化证明 benchmark | 可评测、可对比 | 题集相对冻结，且多是“有答案的 benchmark”，不是活的 open problem 系统 |
| MATH benchmark | 数学题评测集 | 受众大、上手快 | 绝大多数不是 frontier open problem，更不是 living dataset |
| formal-conjectures | Lean 形式化 conjecture 数据 | 机器验证味道最重 | 覆盖面窄，主要是 Lean 入口，不是统一的多验证后端系统 |

真正能打的差异化，不是“我也收集难题”，而是下面这四条：

1. **活数据，不是死题库**：持续增量，不是一次性 benchmark。
2. **每题带验证剖面**：不是“这题很难”，而是“这题该怎么被机器判定”。
3. **尝试可积累**：失败不是垃圾，是下次调度的输入。
4. **多验证后端统一接入**：Lean 只是其中一层，不是唯一真理。

如果做不到第 2 和第 4 条，你和 Open Problem Garden 的差异会被迅速抹平；如果做不到第 3 条，你和任何 benchmark 的差异也会被抹平。

## 2.3 一句话核心价值主张

最该打出去的一句不是“一个 open problem atlas”，而是：

> **一个给 AI agent、求解器和证明器直接开跑的 frontier problem registry：每道题都有可执行验证路径，每次尝试都会被自动验证并永久记账。**

这句话的重点是三个词：**直接开跑 / 可执行验证 / 永久记账**。

---

# 3. GitHub star 策略

## 3.1 高 star 项目的三种模式

### 模式 1：awesome-list

**特点**：
- 上手快。
- 传播轻。
- 最容易蹭到“收藏型 star”。

**问题**：
- 护城河低得像纸。
- 很难形成使用闭环。
- 你只要不更新，就立刻变尸体。

**结论**：别走。走这个就是把自己降级成“整理癖项目”。

### 模式 2：tool

**特点**：
- 一旦解决了一个疼点，star 爆得快。
- 演示爽，转发强。

**问题**：
- 你现在没有一个“压倒性单点能力”的工具。
- 你现在不是 theorem prover，不是 solver，不是 general agent framework。

**结论**：现在硬装 tool，会很尴尬。你会变成“看起来很全，其实没一个点打透”。

### 模式 3：dataset

**特点**：
- 最适合你当前资产：YAML/JSON schema、快照、验证 profile、attempt log。
- 容易被 benchmark、agent、formalization 圈直接拿走使用。
- 更容易成为“别人的基础设施”。

**问题**：
- 纯数据项目容易看起来 boring。
- 所以必须附带最小可运行工具层，不然 star 只会停留在小圈子。

**结论**：

> **这个项目应该走“dataset 主路，tool 副路”的混合打法。**

外宣上你是 dataset / benchmark substrate；内核上你必须有 verifier runner 和 attempt pipeline 这种 tool 味儿，不然没人真用。

## 3.2 这个项目应该走哪条路

明确答案：

> **走 dataset，不走 awesome-list；对外包装成“可执行验证的数据集基础设施”，而不是百科站，也不是万能求解工具。**

原因很现实：

1. 你当前最强的不是“解题能力”，而是**结构化问题资产**。
2. 你真正可能形成复利的是**快照 + schema + verifier contract + attempt ledger**。
3. 你想拿 star，不能只给“内容”，得给“别人一接就能跑”的感觉。

## 3.3 具体 launch 策略

## Launch 原则：别先去面向大众，先去面向会接 API/跑 benchmark 的人

首发受众应该是：
- AI eval / reasoning 圈
- theorem proving / Lean 圈
- formal methods 圈
- solver / SAT / SMT 圈
- 做 benchmark、做 agent infra 的开源工程师

不是先去面向“广义数学爱好者”。那群人会点赞，但不会形成复用。

## 去哪发

### 第一波：硬核受众
- Hacker News（Show HN）
- X / Twitter 上的 theorem proving、AI eval、formal methods 圈
- Lean Zulip / 相关 Discord / theorem proving 社区
- Reddit：`r/MachineLearning`、`r/LocalLLaMA`、`r/math`（后两者要看包装角度）
- LessWrong / EA 里关注 frontier reasoning 的人群

### 第二波：数据集和开源分发
- GitHub Topics / awesome-* 列表挂载
- Papers with Code 风格的 benchmark 描述页
- 各类 benchmark aggregator / dataset index

### 第三波：内容放大
- 一篇“我们如何把 frontier open problems 变成可验证机器任务”的技术博客
- 一篇 baseline 报告：不同 agent / verifier 在 50 题上的结果

## 怎么包装

首页不要先讲理想，先给这三件东西：

1. **一句话**：这是什么。
2. **一个动态图 / 截图**：agent 产出 → verifier 自动判定 → attempt 入账。
3. **一段 30 秒可复现 demo**：`download snapshot -> run baseline -> get verified ledger`。

README 第一屏要出现的，不该是 manifesto，而应该是：

- 当前题目数
- 当前可运行题目数
- 当前验证后端数
- 当前 attempt 数
- 一键运行命令
- 一张 explorer / verifier pipeline 图

## 第一印象该怎么做

现在仓库的第一印象更像“做得很认真的 open problem 站点”。这不够。纯机器闭环版本的第一印象必须更像：

> **这是一个我可以拿来喂 agent、接 verifier、跑 benchmark 的 repo。**

所以第一印象必须包含：

- `Machine-runnable tasks: N`
- `Verifier backends: Lean / SAT-SMT / Python`
- `Attempts recorded: N`
- `Reproducible snapshots`
- `Run baseline in 1 command`

如果首页只展示“我们整理了很多 open problems”，star 不会高。那种仓库很多，大家点一下就走了。

---

# 4. 纯机器闭环的可行路线

## 4.1 如果答案验证不靠人，靠什么

靠四类东西，别幻想第五类神秘力量：

1. **形式证明验证**：Lean 4 / Coq / Isabelle 编译通过。
2. **证书验证**：SAT/SMT/ILP/枚举器产出的 witness / unsat certificate / counterexample，由独立 checker 验。
3. **程序可重放验证**：固定输入、固定 checker、固定随机种子，结果可重跑。
4. **弱证据分级**：数值实验、启发式发现、文献综述只算 evidence，不算 solved。

这意味着你必须放弃一个幻想：

> **不是所有 open problem 都能进纯机器闭环。**

能闭环的只有那部分**问题表述够精确、结果形状够明确、验证器能落地**的任务。其余问题要么滚去参考层，要么根本别进 V1。

## 4.2 Lean 4 formalization 作为验证层的可行性评估

### 结论先说

**可行，但只能当验证层之一，绝对不能当唯一主线。**

### 为什么可行

- 它是最硬的 verifier。通过就是通过，没得嘴硬。
- 对 theorem-shaped 任务特别合适。
- artifact 天然可复现，可版本化。
- 能把“模型觉得自己证明了”这种屁话直接打回去。

### 为什么不能当唯一主线

- 仓库现状里 `312` 个题只有 `1` 个已有 formalization；`311` 个还是 wanted。说明这层现在基本还停留在愿望。
- 很多题虽然 `proof_assistant` 友好，但距离“能被 LLM 在 Lean 里稳定推进”差得远。
- 数学物理、混合型问题、需要数值/搜索辅助的问题，用 Lean 一刀切会把自己玩死。
- formalization 成本高，依赖 Mathlib、定理接口、定义选择，前期工程量极大。

### 务实判断

- 作为**金标准验证层**：中高可行。
- 作为**V1 的唯一闭环**：低可行，别做梦。
- 作为**多验证后端中的一个核心 backend**：对。

### Lean 层该怎么落地

V1 只接三类 Lean 任务：

1. **statement formalization**：把自然语言 statement 变成 Lean theorem stub。
2. **small lemma completion**：不是整题证明，而是局部 lemma。
3. **small finite cases**：小规模可 `decide` / `simp` / brute-force 的情形。

别一上来就把“黎曼猜想 Lean 化自动攻克”写进 roadmap。那不是野心，是抽风。

## 4.3 SAT/SMT/计算验证管道怎么设计

这层反而更应该先做，因为它更现实。

## 核心思想

每道题不是只存 metadata，还要存一个**verification contract**。最少包括：

- `task_type`: `lean_theorem` / `sat_smt_search` / `python_checker` / `mixed`
- `input_spec`
- `artifact_spec`
- `checker_cmd`
- `resource_limits`
- `success_criteria`
- `failure_modes`

## 一条靠谱的计算验证流水线

1. **Problem registry**：题目 YAML 附带 verifier contract。
2. **Encoder**：把题目转成 SAT/SMT/ILP/搜索程序的输入。
3. **Runner**：在沙箱里执行 solver / script。
4. **Certificate store**：保存 witness、unsat proof、counterexample、日志。
5. **Independent checker**：单独的 checker 验证 solver 结果。
6. **Normalizer**：把结果统一成 `verified_pass / verified_fail / unknown / timeout / invalid_artifact`。
7. **Recorder**：写入 attempt ledger。

## 设计原则

- **solver 不能兼任裁判**。求解器自己说“我解出来了”没有任何价值。
- **artifact 必须可复放**。否则下一次连自己都骗不过。
- **partial progress 也要结构化**。比如更紧的下界、找到新反例、跑通更大规模边界，这些都该入账，但不能伪装成 solved。

## 4.4 Agent loop 的技术方案

核心状态机应该很丑，但要真能跑：

`queued -> planned -> running -> candidate_artifact -> verified_(pass/fail/unknown) -> recorded -> rescheduled`

## 建议架构

### 1）Task Registry
每道题定义：
- 问题描述
- verification profile
- verifier contract
- 允许的工具后端
- 成本预算

### 2）Planner
根据 profile 选策略：
- `proof_assistant` → Lean worker
- `computational` → SAT/SMT/search worker
- `mixed` → 先搜索后形式化 / 先分解后验证

### 3）Workers
真正执行尝试：
- LLM proof/formalization worker
- solver worker
- python experimentation worker
- decomposition worker

### 4）Verifier
唯一有资格给 verdict 的组件：
- Lean compiler
- SAT/SMT certificate checker
- Python checker / property-based test runner

### 5）Ledger / Attempt Store
每次尝试必须写入：
- run id
- problem id
- snapshot id
- model/tool versions
- prompt / config / seed
- artifacts 路径
- verifier output
- cost / runtime
- verdict

### 6）Scheduler
根据历史决定下轮预算：
- compile error 太多的，先降级成 statement-cleanup 任务
- 已多次 timeout 的，降低优先级
- 能稳定产出 partial progress 的，提高预算

## 最关键的产品原则

> **模型永远没有资格宣布自己成功，只有 verifier 有。**

纯机器闭环的可信度，全靠这条。

## 4.5 纯机器闭环的边界

必须承认三件事：

1. **tier_3 基本别碰**。`expert_review` 的东西不适合纯机器闭环。
2. **tier_2 也只能部分碰**。很多 `mixed` 任务只能拿 partial evidence，不会闭成“已解决”。
3. **V1 只能从一小撮题开始**。虽然仓库里纸面上有 `175` 个 `tier_1`，但因为 `solver_ready=true` 目前是 `0`，说明“机器可跑”还没被真正产品化。

换句话说，**V1 不应该是“312 题闭环”，而应该是“30–80 题真闭环”。**

---

# 5. V1 核心功能建议

如果只做 3 件事，就做下面这 3 件。别贪。

## 5.1 功能一：Machine-runnable Problem Registry

## 要做什么
把现在的 atlas 从“可读数据”升级成“可运行任务注册表”。

## MVP scope
- 只选 `30–80` 个问题。
- 只收三类：
  - `proof_assistant`
  - `computational`
  - 极少量 `mixed`
- 每题必须新增：
  - verifier contract
  - artifact schema
  - resource budget
  - 明确 success/failure semantics
- 明确标出：
  - `machine_closed_loop_supported: true/false`

## 为什么这是第一位
没有这个，后面所有 agent loop 都是在空气里跑。现在仓库的问题不是“题不够多”，而是**题没有被定义成可执行任务**。

---

## 5.2 功能二：Unified Verifier Runner

## 要做什么
做一个统一入口，把 Lean、SAT/SMT、Python checker 都接进来。

## MVP scope
- 支持 3 个 backend：
  - Lean 4
  - SAT/SMT（先从一个 solver 家族开始）
  - Python checker
- 统一输出：
  - `pass`
  - `fail`
  - `unknown`
  - `timeout`
  - `invalid_artifact`
- 所有执行都带：
  - logs
  - artifact paths
  - runtime
  - tool versions

## 为什么这是第二位
因为**verifier 才是产品核心，不是网页，不是文案，不是 collection 页面**。你不把裁判做好，闭环就是假的。

---

## 5.3 功能三：Attempt Ledger + Auto-run Baseline

## 要做什么
把 attempt 从“人工填写 YAML”升级成“流水线自动记账”。

## MVP scope
- 定义统一 run schema。
- 做一个简单 orchestrator：
  - 读任务
  - 调 worker
  - 跑 verifier
  - 写 ledger
- 至少提供两类 baseline：
  - formalization baseline
  - computational search baseline
- 自动生成 attempt 页面 / leaderboard / failure taxonomy。

## 为什么这是第三位
没有 ledger，所有失败都蒸发；没有 baseline，别人不知道怎么接；没有自动记录，仓库永远只有现在这种 `3` 条、全 `unverified` 的样板 attempt。

---

## 5.4 Absolutely NOT do

下面这些东西，V1 绝对不要做：

### 1）不要继续把“全学科 open problems”当目标
纯机器闭环不吃这一套。数学、理论 CS、少量可形式化/可计算验证的 math physics 足够了。

### 2）不要把 tier_2 / tier_3 强行塞进闭环
尤其 `expert_review`。那不是机器闭环，那是机器自嗨。

### 3）不要先做社区治理产品
issues、review flow、贡献表单这些在纯机器版本里都不是一号优先级。你先把 verifier 跑起来再说。

### 4）不要把“文献综述”当闭环成果主角
文献综述可以留在 evidence 层，但它不能成为机器闭环的核心结果。那只是信息整理，不是验证。

### 5）不要先做花哨 Explorer
静态站够用。真正该做的是 executable registry + verifier + ledger。先把发动机装上，再谈车漆。

### 6）不要营销“AI solves open problems”
这条最蠢，也最容易翻车。应该营销的是：

> **我们把 open problems 变成了 AI 和求解器可以稳定接入、自动验证、自动积累的任务系统。**

这句能活得久。前一句只会让你死得快。

---

# 最后结论

如果坚持**纯机器闭环**，这个项目应该立刻完成认知切换：

- **核心用户**不是“浏览问题的人”，而是“运行求解/验证/评测流水线的人和系统”。
- **产品本体**不是百科站，而是“任务注册表 + verifier + attempt ledger”。
- **公开打法**应该是 dataset 主路、tool 副路，不要再把自己包装成 list 或内容站。
- **技术路线**必须从小而硬的 machine-runnable 子集开始，而不是继续用整个 atlas 充门面。

说得更难听一点：

> **现在这个仓库最缺的不是更多问题，而是真正可执行的闭环。**

把这件事补上，它才是基础设施；补不上，它再漂亮也只是一个很认真的 open problem 网站。
