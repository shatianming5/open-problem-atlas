"""Publish OpenProblemAtlas dataset to HuggingFace Hub.

Usage:
    pip install -e ".[publish]"
    huggingface-cli login
    python scripts/publish_huggingface.py
"""

import json
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "data" / "problems"
DATASET_CARD = ROOT / "dataset_card.md"

REPO_ID = "Tommysha/open-problem-atlas"


def load_all_problems() -> list[dict]:
    problems = []
    for yaml_file in sorted(PROBLEMS_DIR.rglob("*.yaml")):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
            if data and isinstance(data, dict) and "id" in data:
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
                    "statement_precision": data.get("verification_profile", {}).get(
                        "statement_precision", ""
                    ),
                    "solution_checkability": data.get("verification_profile", {}).get(
                        "solution_checkability", ""
                    ),
                    "machine_actionability": data.get("verification_profile", {}).get(
                        "machine_actionability", ""
                    ),
                    "impact": data.get("scores", {}).get("impact", 0),
                    "underexplored": data.get("scores", {}).get("underexplored", 0),
                    "toolability": data.get("scores", {}).get("toolability", 0),
                    "formality": data.get("scores", {}).get("formality", 0),
                    "ai_fit": data.get("scores", {}).get("ai_fit", 0),
                    "full_yaml": yaml.dump(
                        data, default_flow_style=False, allow_unicode=True
                    ),
                }
                problems.append(flat)
    return problems


def main():
    problems = load_all_problems()

    # Save as parquet
    try:
        import pandas as pd

        output_dir = ROOT / "data" / "snapshots" / "huggingface"
        output_dir.mkdir(parents=True, exist_ok=True)
        parquet_path = output_dir / "problems.parquet"
        df = pd.DataFrame(problems)
        df.to_parquet(parquet_path, index=False)
        print(f"Parquet: {parquet_path} ({len(problems)} problems)")
    except ImportError:
        print("pandas not installed, skipping parquet export")
        parquet_path = None

    # Save full JSON
    output_dir = ROOT / "data" / "snapshots" / "huggingface"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "problems.json"
    with open(json_path, "w") as f:
        json.dump(problems, f, indent=2, ensure_ascii=False)
    print(f"JSON: {json_path}")

    # Upload to HuggingFace Hub
    try:
        from huggingface_hub import HfApi

        api = HfApi()
        api.create_repo(REPO_ID, repo_type="dataset", exist_ok=True)

        if parquet_path and parquet_path.exists():
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
    except ImportError:
        print("huggingface_hub not installed. Install with: pip install -e '.[publish]'")
    except Exception as e:
        print(f"HuggingFace upload failed: {e}")
        print("Data files saved locally. Upload manually or run again after 'huggingface-cli login'")


if __name__ == "__main__":
    main()
