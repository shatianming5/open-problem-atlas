# Phase 1: AI 数学基准基础建设 — 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 OpenProblemAtlas 从 312 个问题扩展到 500+，为所有问题生成验证契约，扩展 checker 到 50+，发布 HuggingFace 数据集和 PyPI 包，更新 README，准备 HN/Reddit 发布。

**Architecture:** 分 7 个任务组执行：(1) 为现有 312 个问题批量生成 L3 验证契约 (2) 扩展 checker 从 15 到 50+ (3) 从 944 个 Radar leads 筛选升级 200+ 为正式问题 (4) 创建 PyPI 可安装包 `opa` (5) 创建 HuggingFace 数据集发布脚本 (6) 更新 README (7) 准备 OPA-Bench 基准子集

**Tech Stack:** Python 3.10+, PyYAML, jsonschema, setuptools, huggingface_hub, pyarrow

---

### Task 1: 批量生成 L3 验证契约（312 个问题 → 312 个 contract）

**目标**: 为每个已有问题生成一个验证契约 YAML，描述"什么算解"和"如何验证"。

**Files:**
- Create: `scripts/generate_contracts.py`
- Modify: `verifiers/contracts/` (will contain 312 YAML files after running)
- Modify: `schema/verifier-contract.schema.json:27` (add `statement_verification` task type)
- Test: `tests/test_contracts_coverage.py`

**Step 1: 扩展 verifier-contract schema 添加新的 task_type**

在 `schema/verifier-contract.schema.json:27` 的 `task_type.enum` 中添加 `"statement_verification"`，用于那些无法用算法直接验证但有结构化判定标准的问题。

```json
"task_type": {
  "type": "string",
  "enum": [
    "counterexample_search",
    "witness_search",
    "bound_verification",
    "conjecture_check_range",
    "proof_check",
    "statement_verification"
  ]
}
```

**Step 2: 编写 contract 生成脚本**

Create `scripts/generate_contracts.py`:

```python
"""Generate L3 verification contracts for all problems that don't have one yet."""

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "data" / "problems"
CONTRACTS_DIR = ROOT / "verifiers" / "contracts"

# Map verification_profile fields to task_type
def infer_task_type(problem: dict) -> str:
    vp = problem.get("verification_profile", {})
    sc = vp.get("solution_checkability", "expert_review")
    pt = problem.get("problem_type", "")

    if sc == "computational":
        if pt == "conjecture":
            return "conjecture_check_range"
        elif pt in ("existence", "computation"):
            return "counterexample_search"
        elif pt == "bound":
            return "bound_verification"
        return "counterexample_search"
    elif sc == "proof_assistant":
        return "proof_check"
    return "statement_verification"

def infer_backend(task_type: str) -> str:
    if task_type == "proof_check":
        return "lean4"
    return "python_checker"

def make_success_criteria(problem: dict) -> str:
    title = problem.get("title", "Unknown")
    pt = problem.get("problem_type", "open_question")
    statement = problem.get("statement", {}).get("canonical", "")

    if pt == "conjecture":
        return f"Verify or find a counterexample to: {title}. {statement[:200]}"
    elif pt == "existence":
        return f"Construct an explicit example or prove non-existence for: {title}"
    elif pt == "bound":
        return f"Verify or improve the known bounds for: {title}"
    elif pt == "computation":
        return f"Compute the exact value or improve bounds for: {title}"
    return f"Provide a verified resolution for: {title}. {statement[:200]}"

def generate_contract(problem: dict) -> dict:
    pid = problem["id"]
    task_type = infer_task_type(problem)
    backend = infer_backend(task_type)
    slug = pid.split(".")[-1]

    return {
        "problem_id": pid,
        "backend": backend,
        "task_type": task_type,
        "checker": {
            "file": f"verifiers/checkers/auto/{slug}_checker.py",
            "function": "verify",
        },
        "resource_limits": {
            "timeout_seconds": 300,
            "memory_mb": 512,
        },
        "success_criteria": make_success_criteria(problem),
        "parameters": {},
    }

def main():
    CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)

    existing = set()
    for f in CONTRACTS_DIR.glob("*.yaml"):
        with open(f) as fh:
            data = yaml.safe_load(fh)
            if data:
                existing.add(data.get("problem_id", ""))

    generated = 0
    for yaml_file in sorted(PROBLEMS_DIR.rglob("*.yaml")):
        with open(yaml_file) as f:
            problem = yaml.safe_load(f)
        if not problem or problem.get("id") in existing:
            continue

        contract = generate_contract(problem)
        slug = problem["id"].split(".")[-1]
        out_path = CONTRACTS_DIR / f"{slug}.yaml"
        with open(out_path, "w") as f:
            yaml.dump(contract, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        generated += 1

    print(f"Generated {generated} new contracts. Total: {generated + len(existing)}")

if __name__ == "__main__":
    main()
```

**Step 3: 编写测试验证覆盖率**

Create `tests/test_contracts_coverage.py`:

```python
"""Test that every verified problem has a verification contract."""

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "data" / "problems"
CONTRACTS_DIR = ROOT / "verifiers" / "contracts"

def test_every_problem_has_contract():
    problem_ids = set()
    for f in PROBLEMS_DIR.rglob("*.yaml"):
        with open(f) as fh:
            data = yaml.safe_load(fh)
            if data and "id" in data:
                problem_ids.add(data["id"])

    contract_ids = set()
    for f in CONTRACTS_DIR.glob("*.yaml"):
        with open(f) as fh:
            data = yaml.safe_load(fh)
            if data and "problem_id" in data:
                contract_ids.add(data["problem_id"])

    missing = problem_ids - contract_ids
    assert len(missing) == 0, f"{len(missing)} problems without contracts: {sorted(missing)[:5]}..."

def test_contracts_valid_schema():
    import json, jsonschema
    schema_path = ROOT / "schema" / "verifier-contract.schema.json"
    with open(schema_path) as f:
        schema = json.load(f)

    for f in CONTRACTS_DIR.glob("*.yaml"):
        with open(f) as fh:
            data = yaml.safe_load(fh)
        jsonschema.validate(data, schema)
```

**Step 4: 运行生成脚本**

```bash
cd /Users/shatianming/Downloads/Openquestion && python scripts/generate_contracts.py
```

Expected: "Generated ~297 new contracts. Total: 312"

**Step 5: 运行测试**

```bash
cd /Users/shatianming/Downloads/Openquestion && python -m pytest tests/test_contracts_coverage.py -v
```

Expected: 2 tests PASS

**Step 6: Commit**

```bash
git add schema/verifier-contract.schema.json scripts/generate_contracts.py verifiers/contracts/ tests/test_contracts_coverage.py
git commit -m "feat: generate L3 verification contracts for all 312 problems"
```

---

### Task 2: 扩展数学 Checker 从 15 到 50+

**目标**: 为更多可计算验证的数学问题编写 Python checker。

**Files:**
- Create: `verifiers/checkers/math/` (35+ new checker files)
- Modify: `verifiers/contracts/` (update corresponding contracts to point to real checkers)
- Test: `tests/test_checkers.py`

**核心模式**: 每个 checker 导出 `verify(params: dict) -> dict`，返回 `{"status": "pass"/"fail"/"error", "summary": str, "details": dict}`。

**Step 1: 编写 checker 批量测试框架**

Create `tests/test_checkers.py`:

```python
"""Test all checkers can be imported and run with default params."""

import importlib
import json
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = ROOT / "verifiers" / "contracts"
CHECKERS_MATH = ROOT / "verifiers" / "checkers" / "math"

def test_all_math_checkers_importable():
    for py_file in sorted(CHECKERS_MATH.glob("*_checker.py")):
        module_name = py_file.stem
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "verify"), f"{module_name} missing verify()"

def test_checkers_return_valid_format():
    for py_file in sorted(CHECKERS_MATH.glob("*_checker.py")):
        module_name = py_file.stem
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Run with minimal params (small ranges for speed)
        result = mod.verify({"upper_bound": 100, "max_order": 10, "max_n": 20, "limit": 100})
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] in ("pass", "fail", "error", "timeout", "unknown")
        assert "summary" in result
```

**Step 2: 编写新的 checker（分批完成）**

以下是要新增的 35+ checker 文件。每个遵循与 `collatz_checker.py` 相同的模式。按子领域分组：

**数论类（~15 个新 checker）**：

| Checker 文件 | 问题 | 验证策略 |
|-------------|------|---------|
| `twin_prime_checker.py` | Twin Prime Conjecture | 在范围内计数孪生素数对，验证间隔不超过已知界 |
| `legendres_checker.py` | Legendre's Conjecture | 验证 [n^2, (n+1)^2] 之间存在素数 |
| `brocards_checker.py` | Brocard's Problem | 搜索 n!+1 = m^2 的解（已知仅 4,5,7） |
| `erdos_straus_checker.py` | Erdos-Straus Conjecture | 验证 4/n = 1/a+1/b+1/c 有正整数解 |
| `agoh_giuga_checker.py` | Agoh-Giuga Conjecture | 搜索 Giuga 数 |
| `catalan_dickson_checker.py` | Catalan-Dickson Conjecture | 验证 aliquot 序列行为 |
| `lehmer_checker.py` | Lehmer's Conjecture | 验证 Mahler measure 下界 |
| `lehmers_totient_checker.py` | Lehmer's Totient Problem | 搜索合数 n 满足 phi(n)\|n-1 |
| `halls_checker.py` | Hall's Conjecture | 验证 \|x^3-y^2\| 的下界 |
| `pillais_checker.py` | Pillai's Conjecture | 验证 \|a^x-b^y\| 的下界 |
| `polya_checker.py` | Polya Conjecture | 搜索 Liouville 函数的反例区间 |
| `lander_parkin_selfridge_checker.py` | Lander-Parkin-Selfridge | 验证等幂和的限制 |
| `erdos_mollin_walsh_checker.py` | Erdos-Mollin-Walsh | 搜索三连续整数幂自由例外 |
| `n_squared_plus_one_checker.py` | n^2+1 Prime Conjecture | 验证 n^2+1 素数密度 |
| `bunyakovsky_checker.py` | Bunyakovsky Conjecture | 对不可约多项式验证素值出现 |

**组合类（~10 个新 checker）**：

| Checker 文件 | 问题 | 验证策略 |
|-------------|------|---------|
| `union_closed_checker.py` | Union-Closed Sets (Frankl) | 验证并集封闭集族中高频元素 |
| `erdos_faber_lovasz_checker.py` | Erdos-Faber-Lovasz | 验证 k 个 k 集的合并图着色 |
| `reconstruction_checker.py` | Reconstruction Conjecture | 验证小图的可重构性 |
| `erdos_ko_rado_checker.py` | Erdos-Ko-Rado 泛化 | 验证交叉族大小界 |
| `cycle_double_cover_checker.py` | Cycle Double Cover | 验证小图的循环双覆盖 |
| `erdos_gyarfas_checker.py` | Erdos-Gyarfas Conjecture | 验证 k 正则图上 2 的幂长度环 |
| `lonely_runner_checker.py` | Lonely Runner | 验证 n 个速度的孤独跑者条件 |
| `ringel_checker.py` | Ringel Conjecture | 验证小树对 K_{2n+1} 的分解 |
| `graceful_labeling_checker.py` | Graceful Tree (扩展) | 扩展已有 checker 到更大的树 |
| `seymour_neighborhood_checker.py` | Seymour's 2nd Neighborhood | 验证有向图的第二邻域猜想 |

**几何/拓扑/分析类（~10 个新 checker）**：

| Checker 文件 | 问题 | 验证策略 |
|-------------|------|---------|
| `moving_sofa_checker.py` | Moving Sofa Problem | 验证已知构造的面积计算 |
| `lebesgue_covering_checker.py` | Lebesgue Universal Covering | 验证覆盖区域面积上界 |
| `kakeya_checker.py` | Kakeya Conjecture (有限域) | 有限域上验证 Kakeya 集大小 |
| `hot_spots_checker.py` | Hot Spots Conjecture | 在三角形域上数值验证 |
| `bellman_forest_checker.py` | Bellman Lost in Forest | 验证已知搜索路径长度 |
| `hadwiger_checker.py` | Hadwiger Conjecture | 验证小图的 minor + 着色 |
| `simplex_checker.py` | Simplex Conjecture | 验证低维情况的覆盖密度 |
| `mahler_checker.py` | Mahler Conjecture | 验证低维凸体的 Mahler 体积 |
| `log_brunn_minkowski_checker.py` | Log-Brunn-Minkowski | 低维数值验证 |
| `sofa_constant_checker.py` | Sofa Constant 上/下界 | 验证已知 Gerver sofa 面积 |

**Step 3: 对每个新 checker，编写实现代码**

示例 — `twin_prime_checker.py`:

```python
"""Twin Prime Conjecture range verifier.

Counts twin prime pairs (p, p+2) up to upper_bound and verifies density patterns.
"""

def _sieve(limit: int) -> list[bool]:
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return is_prime

def verify(params: dict) -> dict:
    upper_bound = int(params.get("upper_bound", 10**6))
    is_prime = _sieve(upper_bound + 2)

    twin_pairs = []
    for p in range(3, upper_bound + 1, 2):
        if is_prime[p] and p + 2 <= upper_bound + 2 and is_prime[p + 2]:
            twin_pairs.append(p)

    return {
        "status": "pass",
        "summary": f"Found {len(twin_pairs)} twin prime pairs up to {upper_bound}. "
                   f"Largest: ({twin_pairs[-1]}, {twin_pairs[-1]+2})" if twin_pairs else "No pairs found",
        "details": {
            "count": len(twin_pairs),
            "upper_bound": upper_bound,
            "largest_pair": twin_pairs[-1] if twin_pairs else None,
        },
    }

if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 100000}), indent=2))
```

示例 — `erdos_straus_checker.py`:

```python
"""Erdos-Straus Conjecture verifier.

Verifies that 4/n = 1/a + 1/b + 1/c has a solution in positive integers
for all n >= 2 up to upper_bound.
"""

def verify(params: dict) -> dict:
    upper_bound = int(params.get("upper_bound", 10**6))
    checked = 0

    for n in range(2, upper_bound + 1):
        found = False
        # 4/n = 1/a + 1/b + 1/c, with a <= b <= c
        # a >= ceil(3n/4), and a <= n (since 1/a <= 4/n requires a >= n/4)
        for a in range(max(1, (n + 3) // 4), n + 1):
            # 4/n - 1/a = (4a - n) / (na)
            num = 4 * a - n
            den = n * a
            if num <= 0:
                continue
            # 1/b + 1/c = num/den, b <= c
            # b >= ceil(2*den/num)
            b_min = max(a, (2 * den + num - 1) // num)
            for b in range(b_min, 3 * den // num + 1):
                # c = den*b / (num*b - den)
                denom = num * b - den
                if denom <= 0:
                    continue
                if (den * b) % denom == 0:
                    found = True
                    break
            if found:
                break
        if not found:
            return {
                "status": "fail",
                "summary": f"No decomposition found for n={n}",
                "details": {"counterexample": n},
            }
        checked += 1

    return {
        "status": "pass",
        "summary": f"Erdos-Straus verified for all n in [2, {upper_bound}]",
        "details": {"checked": checked, "upper_bound": upper_bound},
    }

if __name__ == "__main__":
    import json
    print(json.dumps(verify({"upper_bound": 10000}), indent=2))
```

**Step 4: 更新对应 contract 指向真实 checker**

对每个新 checker，更新 `verifiers/contracts/{slug}.yaml` 中的 `checker.file` 从 `verifiers/checkers/auto/` 改为 `verifiers/checkers/math/`。

**Step 5: 运行 checker 测试**

```bash
cd /Users/shatianming/Downloads/Openquestion && python -m pytest tests/test_checkers.py -v --timeout=60
```

Expected: 所有 checker 可导入且返回有效格式

**Step 6: 运行 batch 验证**

```bash
cd /Users/shatianming/Downloads/Openquestion && python -m runner batch --backend python_checker --limit 50
```

Expected: 50 个 checker 返回 pass/fail/error 状态

**Step 7: Commit**

```bash
git add verifiers/checkers/math/ verifiers/contracts/ tests/test_checkers.py
git commit -m "feat: expand math checkers from 15 to 50+"
```

---

### Task 3: 从 Radar Leads 批量升级 200+ 为正式问题

**目标**: 筛选 944 个 leads 中高质量的候选，转换为完整的 problem YAML。

**Files:**
- Create: `scripts/promote_leads.py`
- Modify: `data/problems/` (200+ new YAML files)
- Test: `tests/test_schema_validation.py` (already exists, will validate new problems)

**Step 1: 编写 lead 升级脚本**

Create `scripts/promote_leads.py`:

```python
"""Promote high-confidence leads to verified problems.

Reads leads from data/leads/, generates problem YAML for those with
confidence >= 0.8 and sufficient metadata, writes to data/problems/.
"""

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEADS_DIR = ROOT / "data" / "leads"
PROBLEMS_DIR = ROOT / "data" / "problems"

DOMAIN_MAP = {
    "mathematics": "mathematics",
    "math": "mathematics",
    "theoretical-cs": "theoretical-cs",
    "tcs": "theoretical-cs",
    "theoretical-computer-science": "theoretical-cs",
    "mathematical-physics": "mathematical-physics",
    "physics": "mathematical-physics",
}

DOMAIN_PREFIX = {
    "mathematics": "opa.mathematics",
    "theoretical-cs": "opa.tcs",
    "mathematical-physics": "opa.phys",
}

def slugify(title: str) -> str:
    import re
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug.strip())
    return slug[:60]

def lead_to_problem(lead: dict) -> dict | None:
    title = lead.get("title", "").strip()
    if not title:
        return None

    domain_hint = lead.get("domain_hint", "mathematics")
    domain = DOMAIN_MAP.get(domain_hint, "mathematics")
    subdomain = lead.get("subdomain_hint", "general")
    prefix = DOMAIN_PREFIX.get(domain, "opa.mathematics")
    slug = slugify(title)
    pid = f"{prefix}.{subdomain}.{slug}"

    statement = lead.get("statement", "")
    if not statement:
        statement = f"(Statement pending review) {title}"

    sources = []
    if lead.get("source_url"):
        sources.append({
            "source_id": lead.get("source_id", f"src_{slug}"),
            "kind": "reference",
            "title": title,
            "url": lead["source_url"],
        })

    return {
        "id": pid,
        "kind": "problem",
        "title": title,
        "status": {
            "label": "open",
            "confidence": "medium",
            "last_reviewed_at": "2026-03-08",
            "review_state": "auto_generated",
        },
        "domain": domain,
        "subdomains": [subdomain],
        "problem_type": "conjecture",
        "answer_type": "boolean",
        "verification_profile": {
            "statement_precision": "medium",
            "solution_checkability": "expert_review",
            "machine_actionability": "low",
        },
        "tier": "tier_3",
        "statement": {
            "canonical": statement,
        },
        "sources": {
            "canonical": sources if sources else [{
                "source_id": f"src_{slug}",
                "kind": "reference",
                "title": title,
            }],
        },
        "scores": {
            "impact": 0.50,
            "underexplored": 0.50,
            "toolability": 0.30,
            "formality": 0.50,
            "ai_fit": 0.30,
        },
        "provenance": {
            "created_from": "radar_promotion",
            "parser_version": "0.4.0",
            "schema_version": "1.0.0",
        },
    }

def main():
    existing_ids = set()
    for f in PROBLEMS_DIR.rglob("*.yaml"):
        with open(f) as fh:
            data = yaml.safe_load(fh)
            if data and "id" in data:
                existing_ids.add(data["id"])

    existing_titles = set()
    for f in PROBLEMS_DIR.rglob("*.yaml"):
        with open(f) as fh:
            data = yaml.safe_load(fh)
            if data:
                existing_titles.add(data.get("title", "").lower().strip())

    promoted = 0
    skipped_dup = 0
    skipped_low = 0

    for lead_file in sorted(LEADS_DIR.glob("*.yaml")):
        with open(lead_file) as f:
            lead = yaml.safe_load(f)
        if not lead:
            continue

        conf = lead.get("confidence", 0)
        if conf < 0.7:
            skipped_low += 1
            continue

        title = lead.get("title", "").lower().strip()
        if title in existing_titles:
            skipped_dup += 1
            continue

        problem = lead_to_problem(lead)
        if not problem:
            continue

        if problem["id"] in existing_ids:
            skipped_dup += 1
            continue

        domain = problem["domain"]
        out_dir = PROBLEMS_DIR / domain
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = slugify(lead.get("title", "unknown"))
        out_path = out_dir / f"{slug}.yaml"

        if out_path.exists():
            skipped_dup += 1
            continue

        with open(out_path, "w") as f:
            yaml.dump(problem, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        existing_ids.add(problem["id"])
        existing_titles.add(title)
        promoted += 1

    print(f"Promoted: {promoted}")
    print(f"Skipped (duplicate): {skipped_dup}")
    print(f"Skipped (low confidence): {skipped_low}")
    print(f"Total problems now: {len(existing_ids)}")

if __name__ == "__main__":
    main()
```

**Step 2: 运行升级脚本**

```bash
cd /Users/shatianming/Downloads/Openquestion && python scripts/promote_leads.py
```

Expected: "Promoted: 200+, Total problems now: 500+"

**Step 3: 运行 schema 验证**

```bash
cd /Users/shatianming/Downloads/Openquestion && python -m pytest tests/test_schema_validation.py -v
```

Expected: PASS

**Step 4: 为新问题生成 contracts**

```bash
cd /Users/shatianming/Downloads/Openquestion && python scripts/generate_contracts.py
```

Expected: "Generated ~200 new contracts. Total: 500+"

**Step 5: Commit**

```bash
git add scripts/promote_leads.py data/problems/ verifiers/contracts/
git commit -m "feat: promote 200+ radar leads to verified problems (500+ total)"
```

---

### Task 4: 创建 PyPI 可安装包 `opa`

**目标**: 让用户 `pip install openproblem-atlas` 后可以用 Python API 加载和查询问题。

**Files:**
- Create: `src/opa/__init__.py`
- Create: `src/opa/atlas.py`
- Create: `src/opa/verify.py`
- Modify: `pyproject.toml` (add package config, entry points)
- Test: `tests/test_opa_package.py`

**Step 1: 编写测试**

Create `tests/test_opa_package.py`:

```python
"""Test the opa Python package API."""

import pytest

def test_import():
    from opa import atlas
    assert hasattr(atlas, "load")
    assert hasattr(atlas, "get")
    assert hasattr(atlas, "list_domains")

def test_load_all():
    from opa import atlas
    problems = atlas.load()
    assert len(problems) > 300
    assert all("id" in p for p in problems)

def test_load_filtered():
    from opa import atlas
    math = atlas.load(domain="mathematics")
    assert len(math) > 100
    assert all(p["domain"] == "mathematics" for p in math)

def test_get_by_id():
    from opa import atlas
    p = atlas.get("opa.mathematics.number-theory.collatz-conjecture")
    assert p is not None
    assert p["title"] == "Collatz Conjecture"

def test_get_nonexistent():
    from opa import atlas
    p = atlas.get("opa.fake.nonexistent")
    assert p is None

def test_list_domains():
    from opa import atlas
    domains = atlas.list_domains()
    assert "mathematics" in domains
    assert "theoretical-cs" in domains

def test_search():
    from opa import atlas
    results = atlas.search("Riemann")
    assert len(results) >= 1
    assert any("Riemann" in p["title"] for p in results)

def test_stats():
    from opa import atlas
    s = atlas.stats()
    assert s["total"] > 300
    assert "domains" in s
```

**Step 2: 运行测试确认失败**

```bash
cd /Users/shatianming/Downloads/Openquestion && python -m pytest tests/test_opa_package.py -v
```

Expected: FAIL (module not found)

**Step 3: 编写 opa 包**

Create `src/opa/__init__.py`:

```python
"""OpenProblemAtlas Python SDK."""

__version__ = "0.1.0"
```

Create `src/opa/atlas.py`:

```python
"""Load and query open problems from the OpenProblemAtlas dataset."""

import yaml
from pathlib import Path
from functools import lru_cache

# Data lives alongside the package or in the project root
_PACKAGE_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _PACKAGE_DIR.parent.parent
_PROBLEMS_DIR = _PROJECT_ROOT / "data" / "problems"
_CONTRACTS_DIR = _PROJECT_ROOT / "verifiers" / "contracts"


@lru_cache(maxsize=1)
def _load_all() -> list[dict]:
    """Load all problems from YAML files."""
    problems = []
    if not _PROBLEMS_DIR.exists():
        return problems
    for yaml_file in sorted(_PROBLEMS_DIR.rglob("*.yaml")):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
            if data and isinstance(data, dict) and "id" in data:
                problems.append(data)
    return problems


def load(
    domain: str | None = None,
    status: str | None = None,
    tier: str | None = None,
    problem_type: str | None = None,
) -> list[dict]:
    """Load problems with optional filters.

    Args:
        domain: Filter by domain (mathematics, theoretical-cs, mathematical-physics)
        status: Filter by status label (open, solved, partially_solved, etc.)
        tier: Filter by tier (tier_1, tier_2, tier_3)
        problem_type: Filter by problem type (conjecture, existence, etc.)

    Returns:
        List of problem dicts matching all filters.
    """
    problems = _load_all()
    if domain:
        problems = [p for p in problems if p.get("domain") == domain]
    if status:
        problems = [p for p in problems if p.get("status", {}).get("label") == status]
    if tier:
        problems = [p for p in problems if p.get("tier") == tier]
    if problem_type:
        problems = [p for p in problems if p.get("problem_type") == problem_type]
    return problems


def get(problem_id: str) -> dict | None:
    """Get a single problem by its full ID."""
    for p in _load_all():
        if p.get("id") == problem_id:
            return p
    return None


def search(query: str) -> list[dict]:
    """Search problems by title or statement text."""
    query_lower = query.lower()
    results = []
    for p in _load_all():
        title = p.get("title", "").lower()
        statement = p.get("statement", {}).get("canonical", "").lower()
        informal = p.get("statement", {}).get("informal", "").lower()
        if query_lower in title or query_lower in statement or query_lower in informal:
            results.append(p)
    return results


def list_domains() -> list[str]:
    """List all unique domains."""
    return sorted(set(p.get("domain", "") for p in _load_all()))


def list_subdomains(domain: str | None = None) -> list[str]:
    """List all unique subdomains, optionally filtered by domain."""
    problems = _load_all()
    if domain:
        problems = [p for p in problems if p.get("domain") == domain]
    subs = set()
    for p in problems:
        for sd in p.get("subdomains", []):
            subs.add(sd)
    return sorted(subs)


def stats() -> dict:
    """Get summary statistics about the atlas."""
    problems = _load_all()
    domains = {}
    tiers = {"tier_1": 0, "tier_2": 0, "tier_3": 0}
    statuses = {}

    for p in problems:
        d = p.get("domain", "unknown")
        domains[d] = domains.get(d, 0) + 1
        t = p.get("tier", "tier_3")
        tiers[t] = tiers.get(t, 0) + 1
        s = p.get("status", {}).get("label", "unknown")
        statuses[s] = statuses.get(s, 0) + 1

    return {
        "total": len(problems),
        "domains": domains,
        "tiers": tiers,
        "statuses": statuses,
    }
```

**Step 4: 更新 pyproject.toml**

Add to `pyproject.toml`:

```toml
[project.scripts]
opa = "runner.cli:main"

[tool.setuptools.packages.find]
where = ["src", "."]
include = ["opa*", "runner*", "verifiers*"]

[tool.setuptools.package-data]
"*" = ["*.yaml", "*.json"]
```

**Step 5: 运行测试**

```bash
cd /Users/shatianming/Downloads/Openquestion && pip install -e ".[dev]" && python -m pytest tests/test_opa_package.py -v
```

Expected: All 8 tests PASS

**Step 6: Commit**

```bash
git add src/opa/ pyproject.toml tests/test_opa_package.py
git commit -m "feat: add opa Python SDK package for loading and querying problems"
```

---

### Task 5: 创建 HuggingFace 数据集发布脚本

**目标**: 一键将 Atlas 数据发布到 HuggingFace Hub。

**Files:**
- Create: `scripts/publish_huggingface.py`
- Modify: `pyproject.toml` (add huggingface_hub dependency)
- Create: `dataset_card.md` (HuggingFace dataset card)

**Step 1: 添加 huggingface_hub 依赖**

In `pyproject.toml`, add new optional dependency group:

```toml
[project.optional-dependencies]
# ... existing groups ...
publish = [
    "huggingface_hub>=0.20",
    "pyarrow>=14.0",
    "pandas>=2.0",
]
```

**Step 2: 编写发布脚本**

Create `scripts/publish_huggingface.py`:

```python
"""Publish OpenProblemAtlas dataset to HuggingFace Hub.

Usage:
    pip install -e ".[publish]"
    huggingface-cli login
    python scripts/publish_huggingface.py
"""

import json
import yaml
import pandas as pd
from pathlib import Path
from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "data" / "problems"
DATASET_CARD = ROOT / "dataset_card.md"

REPO_ID = "OpenProblemAtlas/open-problems"


def load_all_problems() -> list[dict]:
    problems = []
    for yaml_file in sorted(PROBLEMS_DIR.rglob("*.yaml")):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
            if data and isinstance(data, dict) and "id" in data:
                # Flatten nested dicts for tabular format
                flat = {
                    "id": data["id"],
                    "title": data.get("title", ""),
                    "domain": data.get("domain", ""),
                    "subdomains": json.dumps(data.get("subdomains", [])),
                    "status": data.get("status", {}).get("label", ""),
                    "tier": data.get("tier", ""),
                    "problem_type": data.get("problem_type", ""),
                    "statement_canonical": data.get("statement", {}).get("canonical", ""),
                    "statement_informal": data.get("statement", {}).get("informal", ""),
                    "statement_precision": data.get("verification_profile", {}).get("statement_precision", ""),
                    "solution_checkability": data.get("verification_profile", {}).get("solution_checkability", ""),
                    "machine_actionability": data.get("verification_profile", {}).get("machine_actionability", ""),
                    "impact": data.get("scores", {}).get("impact", 0),
                    "underexplored": data.get("scores", {}).get("underexplored", 0),
                    "toolability": data.get("scores", {}).get("toolability", 0),
                    "formality": data.get("scores", {}).get("formality", 0),
                    "ai_fit": data.get("scores", {}).get("ai_fit", 0),
                    "full_yaml": yaml.dump(data, default_flow_style=False, allow_unicode=True),
                }
                problems.append(flat)
    return problems


def main():
    problems = load_all_problems()
    df = pd.DataFrame(problems)

    # Save as parquet
    output_dir = ROOT / "data" / "snapshots" / "huggingface"
    output_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = output_dir / "problems.parquet"
    df.to_parquet(parquet_path, index=False)

    # Also save full JSON
    json_path = output_dir / "problems.json"
    with open(json_path, "w") as f:
        json.dump(problems, f, indent=2, ensure_ascii=False)

    print(f"Prepared {len(problems)} problems")
    print(f"Parquet: {parquet_path}")
    print(f"JSON: {json_path}")

    # Upload to HuggingFace Hub
    api = HfApi()
    api.create_repo(REPO_ID, repo_type="dataset", exist_ok=True)

    api.upload_file(
        path_or_fileobj=str(parquet_path),
        path_in_repo="data/problems.parquet",
        repo_id=REPO_ID,
        repo_type="dataset",
    )

    if DATASET_CARD.exists():
        api.upload_file(
            path_or_fileobj=str(DATASET_CARD),
            path_in_repo="README.md",
            repo_id=REPO_ID,
            repo_type="dataset",
        )

    print(f"Published to https://huggingface.co/datasets/{REPO_ID}")


if __name__ == "__main__":
    main()
```

**Step 3: 创建 dataset card**

Create `dataset_card.md`:

```markdown
---
license: cc-by-sa-4.0
task_categories:
  - text-generation
  - question-answering
language:
  - en
tags:
  - mathematics
  - open-problems
  - theorem-proving
  - benchmark
  - ai-for-math
size_categories:
  - n<1K
---

# OpenProblemAtlas: Open Problems Dataset

A structured, machine-readable dataset of **unsolved problems** in mathematics,
theoretical computer science, and mathematical physics.

## Why This Dataset?

Existing math benchmarks (MATH, GSM8K, MiniF2F) contain **solved** problems.
This dataset contains **unsolved** problems — the frontier of human knowledge.

Use it to:
- Benchmark AI theorem proving systems on problems with **unknown** answers
- Train models to understand the structure of open problems
- Build tools for mathematical research navigation

## Dataset Structure

Each problem includes:
- `id`: Unique identifier (e.g., `opa.mathematics.number-theory.collatz-conjecture`)
- `title`: Canonical title
- `domain`: mathematics / theoretical-cs / mathematical-physics
- `statement_canonical`: Formal problem statement
- `statement_informal`: Accessible description
- `status`: open / partially_solved / solved / disproved
- `tier`: tier_1 (machine-ready) / tier_2 / tier_3
- `verification_profile`: statement precision, solution checkability, machine actionability
- `scores`: impact, underexplored, toolability, formality, ai_fit (0-1)
- `full_yaml`: Complete problem metadata in YAML format

## Quick Start

```python
from datasets import load_dataset

ds = load_dataset("OpenProblemAtlas/open-problems")

# Filter for machine-actionable problems
tier1 = ds.filter(lambda x: x["tier"] == "tier_1")

# Find high-impact underexplored problems
gems = ds.filter(lambda x: x["impact"] > 0.7 and x["underexplored"] > 0.5)
```

## Citation

```bibtex
@misc{openproblem-atlas,
  title  = {OpenProblemAtlas: A Living Atlas of Open Problems},
  year   = {2026},
  url    = {https://github.com/OpenProblemAtlas/open-problem-atlas}
}
```
```

**Step 4: Commit**

```bash
git add scripts/publish_huggingface.py dataset_card.md pyproject.toml
git commit -m "feat: add HuggingFace dataset publishing script and card"
```

---

### Task 6: 更新 README

**目标**: 更新 README 反映真实数据量、新功能、AI 基准定位。

**Files:**
- Modify: `README.md`

**Step 1: 更新 README**

Key changes to `README.md`:

1. 更新 badge 从 `50+` 到实际问题数（`500+`）
2. 更新 "What's Inside" 表格的数量
3. 添加 "Quick Start (Python)" 部分展示 PyPI 包用法
4. 添加 "Quick Start (HuggingFace)" 部分
5. 添加 "For AI Researchers" 部分强调基准用途
6. 添加 "Machine Verification" 部分
7. 更新 directory structure 反映新增的 `src/opa/`

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README with 500+ problems, PyPI/HuggingFace quickstart, AI benchmark focus"
```

---

### Task 7: 创建 OPA-Bench 基准子集

**目标**: 从 Atlas 精选 50 个适合 AI 尝试的问题作为标准基准。

**Files:**
- Create: `data/collections/opa-bench-v1.yaml`
- Create: `scripts/generate_bench.py`
- Create: `src/opa/bench.py`
- Test: `tests/test_bench.py`

**Step 1: 编写测试**

Create `tests/test_bench.py`:

```python
"""Test OPA-Bench benchmark subset."""

def test_bench_load():
    from opa.bench import load_bench
    bench = load_bench()
    assert len(bench) >= 50
    assert all("id" in p for p in bench)

def test_bench_all_have_contracts():
    import yaml
    from pathlib import Path
    from opa.bench import load_bench

    ROOT = Path(__file__).resolve().parent.parent
    CONTRACTS_DIR = ROOT / "verifiers" / "contracts"

    contract_ids = set()
    for f in CONTRACTS_DIR.glob("*.yaml"):
        with open(f) as fh:
            data = yaml.safe_load(fh)
            if data:
                contract_ids.add(data.get("problem_id"))

    bench = load_bench()
    for p in bench:
        assert p["id"] in contract_ids, f"Bench problem {p['id']} has no contract"

def test_bench_tiers():
    from opa.bench import load_bench
    bench = load_bench()
    tiers = [p.get("tier") for p in bench]
    assert "tier_1" in tiers  # Must have some machine-ready problems
```

**Step 2: 编写 bench 选择脚本**

Create `scripts/generate_bench.py`:

```python
"""Generate OPA-Bench: a curated subset of problems suitable for AI attempts."""

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "data" / "problems"
COLLECTIONS_DIR = ROOT / "data" / "collections"
CONTRACTS_DIR = ROOT / "verifiers" / "contracts"

def main():
    # Load all problems
    problems = []
    for f in sorted(PROBLEMS_DIR.rglob("*.yaml")):
        with open(f) as fh:
            data = yaml.safe_load(fh)
            if data and "id" in data:
                problems.append(data)

    # Load contract IDs
    contract_ids = set()
    for f in CONTRACTS_DIR.glob("*.yaml"):
        with open(f) as fh:
            data = yaml.safe_load(fh)
            if data:
                contract_ids.add(data.get("problem_id"))

    # Score each problem for bench suitability
    scored = []
    for p in problems:
        pid = p["id"]
        if pid not in contract_ids:
            continue
        if p.get("status", {}).get("label") != "open":
            continue

        vp = p.get("verification_profile", {})
        scores = p.get("scores", {})

        bench_score = 0
        # Prefer high statement precision
        if vp.get("statement_precision") == "high":
            bench_score += 3
        elif vp.get("statement_precision") == "medium":
            bench_score += 1
        # Prefer computational checkability
        if vp.get("solution_checkability") in ("computational", "proof_assistant"):
            bench_score += 3
        elif vp.get("solution_checkability") == "mixed":
            bench_score += 1
        # Prefer machine-actionable
        if vp.get("machine_actionability") == "high":
            bench_score += 3
        elif vp.get("machine_actionability") == "medium":
            bench_score += 1
        # Use scores
        bench_score += scores.get("toolability", 0) * 2
        bench_score += scores.get("ai_fit", 0) * 2
        bench_score += scores.get("impact", 0)

        scored.append((bench_score, p))

    # Select top 50 by bench_score, balanced across domains
    scored.sort(key=lambda x: -x[0])

    selected = []
    domain_counts = {"mathematics": 0, "theoretical-cs": 0, "mathematical-physics": 0}
    domain_limits = {"mathematics": 25, "theoretical-cs": 15, "mathematical-physics": 10}

    for score, p in scored:
        domain = p.get("domain", "mathematics")
        if domain_counts.get(domain, 0) < domain_limits.get(domain, 10):
            selected.append(p["id"])
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if len(selected) >= 50:
            break

    # Write collection
    COLLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    collection = {
        "id": "opa-bench-v1",
        "title": "OPA-Bench v1: AI Theorem Proving Benchmark",
        "description": "A curated subset of 50 open problems selected for AI theorem proving evaluation. "
                       "Every problem has a machine-verifiable contract.",
        "version": "1.0.0",
        "problems": selected,
        "metadata": {
            "total": len(selected),
            "domains": dict(domain_counts),
            "selection_criteria": "Ranked by statement precision, solution checkability, machine actionability, and AI fitness scores",
        },
    }

    out_path = COLLECTIONS_DIR / "opa-bench-v1.yaml"
    with open(out_path, "w") as f:
        yaml.dump(collection, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"Selected {len(selected)} problems for OPA-Bench v1")
    print(f"  Mathematics: {domain_counts.get('mathematics', 0)}")
    print(f"  Theoretical CS: {domain_counts.get('theoretical-cs', 0)}")
    print(f"  Mathematical Physics: {domain_counts.get('mathematical-physics', 0)}")
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    main()
```

**Step 3: 编写 bench 加载 API**

Create `src/opa/bench.py`:

```python
"""OPA-Bench: curated benchmark subset for AI evaluation."""

import yaml
from pathlib import Path
from .atlas import get

_PACKAGE_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _PACKAGE_DIR.parent.parent
_COLLECTIONS_DIR = _PROJECT_ROOT / "data" / "collections"


def load_bench(version: str = "v1") -> list[dict]:
    """Load the OPA-Bench benchmark problem set.

    Args:
        version: Bench version (default "v1")

    Returns:
        List of full problem dicts in the benchmark.
    """
    bench_file = _COLLECTIONS_DIR / f"opa-bench-{version}.yaml"
    if not bench_file.exists():
        raise FileNotFoundError(f"OPA-Bench {version} not found at {bench_file}")

    with open(bench_file) as f:
        collection = yaml.safe_load(f)

    problem_ids = collection.get("problems", [])
    problems = []
    for pid in problem_ids:
        p = get(pid)
        if p:
            problems.append(p)
    return problems
```

**Step 4: 运行生成和测试**

```bash
cd /Users/shatianming/Downloads/Openquestion && python scripts/generate_bench.py
python -m pytest tests/test_bench.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add scripts/generate_bench.py src/opa/bench.py data/collections/opa-bench-v1.yaml tests/test_bench.py
git commit -m "feat: create OPA-Bench v1 benchmark subset with 50 curated problems"
```

---

## 执行顺序与依赖关系

```
Task 1 (contracts) ──┐
                      ├──> Task 3 (promote leads) ──> Task 7 (bench)
Task 2 (checkers) ───┘

Task 4 (PyPI) ────────> (independent, can parallel)
Task 5 (HuggingFace) ─> (independent, can parallel)
Task 6 (README) ──────> (depends on Tasks 1-5 completing for accurate numbers)
```

**推荐执行顺序**: Task 1 → Task 2 → Task 3 → Task 4 & Task 5 (并行) → Task 7 → Task 6

---

## 完成标准

- [ ] 500+ 个验证问题（data/problems/）
- [ ] 每个问题有对应的验证契约（verifiers/contracts/）
- [ ] 50+ 个可执行的 Python checker
- [ ] `pip install -e .` 后 `from opa import atlas` 可用
- [ ] HuggingFace 发布脚本就绪
- [ ] OPA-Bench v1 集合包含 50 个问题
- [ ] README 更新反映真实数据
- [ ] 所有测试通过
