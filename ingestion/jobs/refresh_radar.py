"""Refresh radar leads from configured sources."""

import logging
import os
from datetime import date
from pathlib import Path

import yaml

from ingestion.adapters.arxiv_adapter import ArxivAdapter
from ingestion.adapters.openalex import OpenAlexAdapter

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent
LEADS_DIR = ROOT / "data" / "leads"


def generate_lead_yaml(candidate, source_adapter_name: str) -> dict:
    """Convert a CandidateProblem to a lead YAML structure."""
    return {
        "title": candidate.title,
        "statement": candidate.statement[:500] if candidate.statement else "",
        "source_id": candidate.source_id,
        "source_locator": candidate.source_locator,
        "domain_hint": candidate.domain_hint,
        "subdomain_hint": candidate.subdomain_hint,
        "confidence": candidate.confidence,
        "extraction_method": candidate.extraction_method,
        "discovered_by": source_adapter_name,
        "discovered_at": date.today().isoformat(),
        "status": "lead_unverified",
    }


def save_lead(lead: dict, index: int):
    """Save a lead to the leads directory."""
    LEADS_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    filename = f"{today}_{index:04d}.yaml"
    path = LEADS_DIR / filename

    with open(path, "w") as f:
        yaml.dump(lead, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    logger.info("Saved lead: %s", path)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    email = os.environ.get("OPENALEX_EMAIL")
    candidates = []

    # Run arXiv adapter
    logger.info("Running arXiv adapter...")
    try:
        arxiv = ArxivAdapter()
        arxiv_candidates = arxiv.run(max_results=10)
        candidates.extend(arxiv_candidates)
        logger.info("arXiv: %d candidates", len(arxiv_candidates))
    except Exception as e:
        logger.warning("arXiv adapter failed: %s", e)

    # Run OpenAlex adapter
    if email:
        logger.info("Running OpenAlex adapter...")
        try:
            openalex = OpenAlexAdapter(email=email)
            oa_candidates = openalex.run(per_page=10)
            candidates.extend(oa_candidates)
            logger.info("OpenAlex: %d candidates", len(oa_candidates))
        except Exception as e:
            logger.warning("OpenAlex adapter failed: %s", e)
    else:
        logger.info("Skipping OpenAlex (no OPENALEX_EMAIL set)")

    # Save leads
    logger.info("Total candidates: %d", len(candidates))
    for i, candidate in enumerate(candidates):
        lead = generate_lead_yaml(candidate, candidate.extraction_method)
        save_lead(lead, i)

    logger.info("Radar refresh complete.")


if __name__ == "__main__":
    main()
