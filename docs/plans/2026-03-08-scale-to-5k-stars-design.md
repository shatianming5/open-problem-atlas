# OpenProblemAtlas: AI 数学基准路线 — 扩展至 5k Star 设计方案

**日期**: 2026-03-08
**状态**: 已批准
**核心定位**: AI 定理证明系统的标准靶场 — 唯一提供「未解决问题 + 机器验证」的数据集

---

## 一、战略定位

OpenProblemAtlas 的独特价值：**第一个将人类未解决的数学和计算科学问题以结构化、机器可读、可验证的方式组织的开放数据集。**

现有基准（MATH、GSM8K、MiniF2F、PutnamBench）全是已解决问题，无法测试 AI 的真正推理极限。OPA 填补这个空白。

---

## 二、模块 1：规模化问题收录 + 自动 Checker 生成

### 2.1 目标

从 312 个问题扩展到 2000+，每个问题都有某种形式的机器验证。

### 2.2 问题来源优先级

1. **现有 944 个 Radar leads** — 筛选、验证、补充 checker 后升级
2. **结构化来源批量导入**：
   - Open Problem Garden（~1000 个，已有 adapter）
   - Erdos Problems（~300 个，已有 adapter）
   - MathOverflow "open-problem" 标签帖子（~2000 个）
   - arXiv 论文 "open question" 段落（LLM 提取）
   - Google Formal Conjectures 数据集（已有 adapter）
3. **领域扩展**：ML 理论、统计力学、量子信息等

### 2.3 Checker 分层策略

| 层级 | 适用类型 | 内容 | 覆盖目标 |
|------|---------|------|---------|
| L1: 范围检查 | 算术/组合猜想 | Python checker 在有限范围验证 | ~30% |
| L2: 反例搜索 | 存在性/猜想 | 搜索反例的 Python/SAT 程序 | ~25% |
| L3: 验证契约 | 所有问题 | YAML 契约描述"什么算解"、判定逻辑 | 100% |
| L4: 形式化陈述 | 可形式化的 | Lean4/Coq 形式化 | ~15%（长期） |

### 2.4 自动化流水线

1. LLM 从 Radar lead 生成标准 YAML（按 schema）
2. LLM 根据问题类型生成 L3 验证契约
3. 对算术/组合类问题，LLM 生成 L1/L2 Python checker 草稿
4. Human review 确认质量
5. CI 自动运行 checker 验证

---

## 三、模块 2：分发渠道

### 3.1 HuggingFace 数据集（P0）

- 发布 `OpenProblemAtlas/open-problems`
- Parquet 格式，按 domain/status/tier 分 split
- 每月自动更新（与 `data/snapshots/` 同步）
- `load_dataset("OpenProblemAtlas/open-problems")` 一行接入

### 3.2 PyPI 包（P1）

```python
# pip install openproblem-atlas
from opa import atlas

problems = atlas.load(domain="mathematics", status="open")
p = atlas.get("opa.mathematics.number-theory.collatz-conjecture")
result = atlas.verify(p, candidate_solution=my_solution)
bench = atlas.benchmark(tier="tier_1", solver_ready=True)
```

### 3.3 REST API（P2）

- 只读 API（GitHub Pages / Cloudflare Workers）
- `GET /v1/problems?domain=mathematics&status=open`
- `GET /v1/problems/{id}`
- `POST /v1/verify/{id}` — 提交候选解验证

---

## 四、模块 3：OPA-Bench — AI 定理证明基准

### 4.1 核心设计

- 精选 50-100 个问题作为核心基准集
- 难度分级：Bronze / Silver / Gold
- 标准化输入/输出格式 + 验证 checker
- 排行榜：AI 系统的尝试结果和进展

### 4.2 与现有基准的差异

| 基准 | 问题类型 | 答案已知？ | 验证方式 |
|------|---------|-----------|---------|
| MATH | 竞赛数学 | 是 | 答案匹配 |
| GSM8K | 小学应用题 | 是 | 答案匹配 |
| MiniF2F | 形式化定理 | 是 | Lean/Isabelle |
| PutnamBench | 竞赛证明 | 是 | Lean |
| **OPA-Bench** | **开放问题** | **否** | **多层验证** |

---

## 五、模块 4：发布与传播策略

### 5.1 第一波：HN + Reddit（目标 500 星）

- HN 标题：`Show HN: Machine-readable atlas of 300+ unsolved math problems with verifiers`
- 发布时间：UTC 13:00-15:00，周二至周四
- Reddit 同步：r/math, r/MachineLearning, r/compsci
- 首评重点：为什么现有列表不够用、唯一的未解决问题 AI 基准、一行代码接入

### 5.2 第二波：arXiv 论文（目标 2000 星）

- 论文：*"OpenProblemAtlas: A Machine-Verifiable Benchmark of Unsolved Problems for AI Mathematical Reasoning"*
- 投稿：NeurIPS 2026 Datasets & Benchmarks / ICML AI for Math Workshop
- 内容：数据集统计、与现有基准对比、AI 系统初步评估

### 5.3 第三波：社区连接（目标 5000 星）

- Twitter/X 标记 Terence Tao、Kevin Buzzard、DeepSeek 团队
- 联系 AI lab 使用 OPA-Bench 评估
- 「Problem Solved!」事件驱动传播
- 月度数据快照发布

---

## 六、模块 5：技术架构升级

1. **Checker 框架标准化**：统一接口，支持 LLM 生成的 checker 自动集成
2. **CI/CD 增强**：PR 新问题时自动 schema + checker 验证
3. **排行榜系统**：静态生成的排行榜页面
4. **数据导出**：自动 Parquet/JSON + HuggingFace 同步
5. **网站升级**：搜索 API、关系图交互、AI 尝试展示

---

## 七、实施阶段

### Phase 1（第 1 个月）：基础建设 → 0-500 星

- [ ] 现有 312 个问题全部生成 L3 验证契约
- [ ] 扩展 checker 从 15 个到 50+（算术/组合类）
- [ ] 发布 HuggingFace 数据集
- [ ] 发布 PyPI 包
- [ ] 更新 README（badge、截图、定位说明）
- [ ] Radar leads 中筛选 200+ 升级为正式问题
- [ ] HN Show HN + Reddit 发布

### Phase 2（第 2-3 个月）：扩展 → 500-2000 星

- [ ] 问题总量扩展到 1000+
- [ ] 创建 OPA-Bench 核心子集
- [ ] 撰写 arXiv 论文
- [ ] REST API 上线
- [ ] AI 尝试排行榜
- [ ] 联系 AI lab 和形式化社区

### Phase 3（第 4-6 个月）：生态系统 → 2000-5000 星

- [ ] 问题总量扩展到 2000+
- [ ] NeurIPS 投稿
- [ ] 月度快照 + 状态更新推送
- [ ] 教育工作流集成
- [ ] Lean4 形式化陈述覆盖 15%+ 问题

---

## 八、成功指标

| 指标 | 当前 | Phase 1 | Phase 2 | Phase 3 |
|------|------|---------|---------|---------|
| 验证问题数 | 312 | 500+ | 1000+ | 2000+ |
| 有 checker 的问题 | 15 | 100+ | 300+ | 600+ |
| 有验证契约的问题 | 15 | 500+ | 1000+ | 2000+ |
| GitHub Stars | 0 | 500 | 2000 | 5000 |
| HuggingFace 下载 | 0 | 1000+ | 5000+ | 20000+ |
| PyPI 月下载 | 0 | 500+ | 2000+ | 5000+ |
| AI 尝试记录 | 3 | 50+ | 200+ | 500+ |
| 贡献者 | 1 | 10+ | 30+ | 50+ |

---

## 九、关键参考项目

| 项目 | Stars | 启示 |
|------|-------|------|
| awesome-math | ~12.2k | 策展列表的天花板，OPA 更结构化 |
| mathlib4 | ~3k | 形式化社区的忠诚度 |
| hendrycks/math | ~1.3k | 学术论文驱动的基准影响力 |
| openproblems-bio | 中等 | Nature Biotechnology 论文 + 基准测试模式 |
| Papers With Code | 高流量 | 论文+代码+基准的生态模式 |
