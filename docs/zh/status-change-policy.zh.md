> 本文档是 [English original](../status-change-policy.md) 的中文翻译。

# 状态变更策略

本文档定义了在 OpenProblemAtlas 中变更问题状态的流程。

## 状态标签

| 状态 | 含义 |
|------|------|
| `open` | 无已知解法 |
| `partially_solved` | 有重大进展但未完全解决 |
| `solved` | 存在完整的、被接受的解法 |
| `disproved` | 已知反例或反驳 |
| `conditional` | 在未证明的假设条件下已解决 |
| `independent` | 已证明独立于标准公理系统 |
| `ambiguous` | 问题描述不清晰或有争议 |
| `retired_duplicate` | 与另一条目重复 |

## 提议状态变更

1. **提交 issue**，使用 [报告状态变更](.github/ISSUE_TEMPLATE/report-status-change.yml) 模板。
2. 提供：
   - 问题 ID（例如 `opa.mathematics.number-theory.twin-prime-conjecture`）
   - 提议的新状态标签
   - 至少一个支持该变更的来源（论文、预印本或公告）
   - 所声明结果的简要摘要

## 审核流程

### 第 1 级：无争议的变更

社区共识明确的变更（例如经同行评审的期刊发表）：

- 单个领域专家审核者即可批准。
- 审核者更新 `status.label`、`status.confidence`、`status.last_reviewed_at`，并将来源添加到 `sources.status_evidence`。

### 第 2 级：近期或未验证的声明

基于近期预印本或未验证声明的变更：

- 将状态设为 `partially_solved` 或声明的状态，并设置 `confidence: low`。
- 添加 `review_state: needs_review`。
- 至少两位审核者必须独立评估后才能提高置信度。

### 第 3 级：有争议的或存在争论的

结果正在被积极争论的变更：

- 设置 `confidence: low`，并将声明和任何反驳都添加到 `sources.status_evidence`。
- 为 issue 添加 `status:disputed` 标签。
- 在争议解决之前，不要变更为 `solved` 或 `disproved`。

## 状态变更的必填字段

更新问题状态时，**必须**更新以下字段：

```yaml
status:
  label: <new_status>
  confidence: <high|medium|low>
  last_reviewed_at: "<YYYY-MM-DD>"
  review_state: human_verified
  reviewer: "<your_github_handle>"
  stale_after: "<YYYY-MM-DD>"  # 通常为审核后一年
```

并添加支持来源：

```yaml
sources:
  status_evidence:
    - source_id: src_<author>_<year>
      kind: paper
      title: "<paper title>"
      url: "<doi or arxiv url>"
      year: <year>
```

## 回退策略

如果已声明的解法后来被发现包含错误：

1. 将状态回退到先前的值。
2. 将尝试解法的来源保留在 `status_evidence` 中并附带注释。
3. 添加新的证据条目记录撤回或错误。
4. 设置 `review_state: needs_review` 直到重新评估。

## 自动化

- `stale_after` 字段触发定期的重新审核提醒。
- CI 检查验证所有状态变更都包含更新的 `last_reviewed_at`。
- 每月快照捕获状态时间线以进行历史追踪。
