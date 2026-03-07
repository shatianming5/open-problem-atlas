"""OpenAlex adapter for discovering papers with open problems."""

import logging
from urllib.parse import quote

import httpx

from .base import BaseAdapter, CandidateProblem, RawSourceRecord

logger = logging.getLogger(__name__)

OPENALEX_API = "https://api.openalex.org"

# Concepts related to open problems in our target domains
SEARCH_QUERIES = [
    "open problem conjecture unsolved",
    "open questions number theory",
    "open problems graph theory",
    "open problems complexity theory",
    "conjectures combinatorics",
]


class OpenAlexAdapter(BaseAdapter):
    """Adapter for OpenAlex API to find papers discussing open problems."""

    def __init__(self, email: str | None = None):
        self.email = email
        self.client = httpx.Client(timeout=30)

    @property
    def source_name(self) -> str:
        return "OpenAlex"

    @property
    def source_tier(self) -> int:
        return 2  # Papers found via OpenAlex are supporting sources

    def _headers(self) -> dict:
        headers = {"Accept": "application/json"}
        if self.email:
            headers["User-Agent"] = f"OpenProblemAtlas/0.1 (mailto:{self.email})"
        return headers

    def _search_works(self, query: str, per_page: int = 25) -> list[dict]:
        """Search OpenAlex works API."""
        url = f"{OPENALEX_API}/works"
        params = {
            "search": query,
            "filter": "type:article,is_oa:true",
            "sort": "cited_by_count:desc",
            "per_page": per_page,
        }
        if self.email:
            params["mailto"] = self.email

        try:
            resp = self.client.get(url, params=params, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
            return data.get("results", [])
        except httpx.HTTPError as e:
            logger.warning("OpenAlex search failed for '%s': %s", query, e)
            return []

    def fetch(self, queries: list[str] | None = None, per_page: int = 25) -> list[RawSourceRecord]:
        """Fetch papers from OpenAlex matching open-problem queries."""
        queries = queries or SEARCH_QUERIES
        records = []
        seen_ids = set()

        for query in queries:
            works = self._search_works(query, per_page)
            for work in works:
                oa_id = work.get("id", "")
                if oa_id in seen_ids:
                    continue
                seen_ids.add(oa_id)

                authors = []
                for authorship in work.get("authorships", []):
                    name = authorship.get("author", {}).get("display_name")
                    if name:
                        authors.append(name)

                record = RawSourceRecord(
                    source_id=f"openalex_{oa_id.split('/')[-1]}",
                    source_kind="paper",
                    source_tier=self.source_tier,
                    title=work.get("title", ""),
                    authors=authors,
                    year=work.get("publication_year"),
                    url=work.get("doi") or work.get("id"),
                    doi=work.get("doi"),
                    metadata={
                        "openalex_id": oa_id,
                        "cited_by_count": work.get("cited_by_count", 0),
                        "concepts": [
                            c.get("display_name")
                            for c in work.get("concepts", [])[:5]
                        ],
                    },
                )
                records.append(record)

        logger.info("Fetched %d records from OpenAlex", len(records))
        return records

    def extract_candidates(self, records: list[RawSourceRecord]) -> list[CandidateProblem]:
        """Extract candidate problems from OpenAlex records.

        Note: Full extraction requires downloading and parsing paper content.
        This adapter only provides metadata-level candidates that need further
        processing by the extraction pipeline.
        """
        candidates = []
        for record in records:
            candidate = CandidateProblem(
                title=record.title,
                statement="",  # Needs full-text extraction
                source_id=record.source_id,
                source_locator="",
                domain_hint=self._guess_domain(record),
                confidence=0.3,  # Low confidence without full text
                extraction_method="openalex_metadata",
            )
            candidates.append(candidate)
        return candidates

    def _guess_domain(self, record: RawSourceRecord) -> str:
        """Heuristic domain guess from OpenAlex concepts."""
        concepts = {c.lower() for c in record.metadata.get("concepts", [])}
        if concepts & {"mathematics", "number theory", "combinatorics", "graph theory", "algebra"}:
            return "mathematics"
        if concepts & {"computer science", "complexity", "algorithm", "cryptography"}:
            return "theoretical-cs"
        if concepts & {"physics", "quantum", "statistical mechanics"}:
            return "mathematical-physics"
        return ""
