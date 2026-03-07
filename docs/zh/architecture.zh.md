> 本文档是 [English original](../architecture.md) 的中文翻译。

# 架构

## 概述

OpenProblemAtlas 是一个包含四个逻辑层的单体仓库：

```
┌─────────────────────────────────────────┐
│           Explorer / Site               │  ← 展示层
├─────────────────────────────────────────┤
│  Atlas（已验证） │  Radar（线索）       │  ← 数据层
│  Lab（尝试）     │  Collections         │
├─────────────────────────────────────────┤
│         Ingestion + Extraction          │  ← 管道层
├─────────────────────────────────────────┤
│     Schema + Validators + CI            │  ← 质量层
└─────────────────────────────────────────┘
```

## 数据流

```
Source Adapters → Raw Source Records → Section Splitter → Candidate Extractor
    → Status Classifier → Alias Linker → Dedupe → Reviewer Queue → Publish Build
```

### 管道阶段

1. **源适配器（Source Adapter）**：将外部内容转换为统一的 `source` 记录
2. **章节拆分器（Section Splitter）**：识别相关章节（开放问题、猜想、未来工作）
3. **候选提取器（Candidate Extractor）**：使用规则 + 大语言模型提取候选问题描述
4. **状态分类器（Status Classifier）**：将候选项分类为 open/solved/future-work/vague/non-problem
5. **别名链接器（Alias Linker）**：合并同一问题的不同名称
6. **去重（Dedupe）**：防止跨来源的重复条目
7. **审核队列（Reviewer Queue）**：在提升至 Atlas 之前的人工审核关卡
8. **发布构建（Publish Build）**：从规范数据生成站点、搜索索引和发布产物

## 存储策略

### 仓库内存储

- 规范 YAML 数据文件（问题、线索、尝试、集合）
- 用于验证的 JSON Schema
- 代码（适配器、提取器、验证器、站点）
- 配置和 CI/CD

### 不存储在仓库中

- 原始全文 PDF
- 缓存的网页
- 大型二进制产物
- API 密钥或凭证

## 技术选型

| 组件 | 技术 | 理由 |
|------|------|------|
| 数据格式 | YAML | 人类可读，对贡献者友好 |
| 模式定义 | JSON Schema | 标准化，工具丰富 |
| 验证 | Python + jsonschema | 简单，可扩展 |
| CI/CD | GitHub Actions | GitHub 原生集成 |
| 站点 | 静态站点（Jinja2 + 原生 JS） | 无需服务器，免费托管 |
| API | 静态 JSON 文件 | 零基础设施成本 |
| 数据摄取 | Python + httpx | 支持异步，代码简洁 |
| 数据提取 | Python + LLM API | 灵活的模型选择 |

## 可扩展性路径

v1 目标：
- 约 300 个已验证问题 -- 存储为 git 中的 YAML 文件
- 约 1000 个线索 -- 存储为 git 中的 YAML 文件
- GitHub Pages 上的静态站点

如果增长需要：
- 将数据迁移至 SQLite 或 PostgreSQL
- 添加服务端 API
- 使用 CDN 加速站点
- 将提取任务迁移至云端 Worker
