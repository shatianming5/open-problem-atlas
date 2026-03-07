"""Semantic Scholar adapter for discovering papers with open problems.

Uses the Semantic Scholar Academic Graph API
(https://api.semanticscholar.org/graph/v1/) to search for papers whose
abstracts discuss open problems or conjectures.
"""

import logging

import httpx

from .base import BaseAdapter, CandidateProblem, RawSourceRecord

logger = logging.getLogger(__name__)

S2_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# Default search queries targeted at discovering open problems.
DEFAULT_QUERIES = [
    "open problems mathematics",
    "unsolved conjectures",
    "open questions combinatorics",
    "open problems number theory",
    "open problems computational complexity",
]

# Fields to request from the Semantic Scholar API.
S2_FIELDS = (
    "paperId,externalIds,title,abstract,year,authors,fieldsOfStudy,"
    "citationCount,url"
)


class SemanticScholarAdapter(BaseAdapter):
    """Adapter for the Semantic Scholar Academic Graph API.

    Searches for papers related to open problems and extracts candidate
    problems from their abstracts.
    """

    def __init__(self, api_key: str | None = None):
        """Initialise the adapter.

        Args:
            api_key: Optional Semantic Scholar API key.  Providing a key grants
                higher rate limits (100 requests/sec vs. 100 requests/5 min for
                unauthenticated access).
        """
        headers: dict[str, str] = {}
        if api_key:
            headers["x-api-key"] = api_key
        self.client = httpx.Client(timeout=30, headers=headers)

    # ------------------------------------------------------------------
    # BaseAdapter interface
    # ------------------------------------------------------------------

    @property
    def source_name(self) -> str:
        return "SemanticScholar"

    @property
    def source_tier(self) -> int:
        return 2

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _search(
        self, query: str, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        """Execute a single search against the Semantic Scholar API."""
        params: dict[str, str | int] = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "fields": S2_FIELDS,
        }

        try:
            resp = self.client.get(S2_SEARCH_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])
        except httpx.HTTPError as exc:
            logger.warning(
                "Semantic Scholar search failed for '%s': %s", query, exc
            )
            return []
        except (KeyError, ValueError) as exc:
            logger.warning("Semantic Scholar response parse error: %s", exc)
            return []

    @staticmethod
    def _parse_paper(paper: dict) -> dict:
        """Normalise a single Semantic Scholar paper object."""
        authors = [
            a.get("name", "") for a in paper.get("authors", []) if a.get("name")
        ]
        external_ids = paper.get("externalIds", {}) or {}
        doi = external_ids.get("DOI", "")
        arxiv_id = external_ids.get("ArXiv", "")
        fields = paper.get("fieldsOfStudy") or []
        url = paper.get("url", "")
        if not url and doi:
            url = f"https://doi.org/{doi}"

        return {
            "paper_id": paper.get("paperId", ""),
            "title": paper.get("title", ""),
            "abstract": paper.get("abstract", "") or "",
            "authors": authors,
            "year": paper.get("year"),
            "doi": doi,
            "arxiv_id": arxiv_id,
            "url": url,
            "fields_of_study": fields,
            "citation_count": paper.get("citationCount", 0),
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch(
        self,
        queries: list[str] | None = None,
        limit_per_query: int = 20,
        **kwargs,
    ) -> list[RawSourceRecord]:
        """Search Semantic Scholar for papers related to open problems.

        Args:
            queries: Search query strings. Defaults to ``DEFAULT_QUERIES``.
            limit_per_query: Maximum results per query.

        Returns:
            A list of ``RawSourceRecord`` instances.
        """
        queries = queries or DEFAULT_QUERIES
        records: list[RawSourceRecord] = []
        seen_ids: set[str] = set()

        for query in queries:
            papers = self._search(query, limit=limit_per_query)
            for paper in papers:
                parsed = self._parse_paper(paper)
                pid = parsed["paper_id"]
                if not pid or pid in seen_ids:
                    continue
                seen_ids.add(pid)

                record = RawSourceRecord(
                    source_id=f"s2_{pid}",
                    source_kind="paper",
                    source_tier=self.source_tier,
                    title=parsed["title"],
                    authors=parsed["authors"],
                    year=parsed["year"],
                    url=parsed["url"],
                    doi=parsed["doi"] or None,
                    content_sections=[
                        {"type": "abstract", "text": parsed["abstract"]},
                    ],
                    metadata={
                        "paper_id": pid,
                        "arxiv_id": parsed["arxiv_id"],
                        "fields_of_study": parsed["fields_of_study"],
                        "citation_count": parsed["citation_count"],
                        "query": query,
                    },
                )
                records.append(record)

        logger.info("Fetched %d records from SemanticScholar", len(records))
        return records

    def extract_candidates(
        self, records: list[RawSourceRecord]
    ) -> list[CandidateProblem]:
        """Identify candidate open problems from Semantic Scholar paper abstracts.

        Uses keyword matching on titles and abstracts.  Papers with higher
        citation counts receive a small confidence boost, as highly cited
        survey papers are more likely to contain well-known open problems.
        """
        keywords = [
            "open problem",
            "open question",
            "conjecture",
            "unsolved",
            "unresolved",
            "remains open",
            "still open",
            "we pose",
            "we ask",
        ]
        candidates: list[CandidateProblem] = []

        for record in records:
            abstract = ""
            for section in record.content_sections:
                if section.get("type") == "abstract":
                    abstract = section.get("text", "")
                    break

            searchable = f"{record.title} {abstract}".lower()
            matched_kws = [kw for kw in keywords if kw in searchable]
            if not matched_kws:
                continue

            # Base confidence from keyword hits.
            confidence = min(0.3 + 0.1 * len(matched_kws), 0.7)
            # Small boost for highly cited papers.
            citation_count = record.metadata.get("citation_count", 0)
            if citation_count and citation_count > 50:
                confidence = min(confidence + 0.05, 0.8)

            fields = record.metadata.get("fields_of_study", [])
            domain_hint = ""
            if "Mathematics" in fields:
                domain_hint = "mathematics"
            elif "Computer Science" in fields:
                domain_hint = "theoretical-cs"
            elif "Physics" in fields:
                domain_hint = "mathematical-physics"

            candidate = CandidateProblem(
                title=record.title,
                statement=abstract if abstract else record.title,
                source_id=record.source_id,
                source_locator=record.url or "",
                domain_hint=domain_hint,
                subdomain_hint=", ".join(fields[:3]),
                problem_type_hint="survey_mention",
                confidence=confidence,
                raw_text=abstract,
                extraction_method="s2_abstract_keyword",
            )
            candidates.append(candidate)

        logger.info(
            "Extracted %d candidates from %d SemanticScholar records",
            len(candidates),
            len(records),
        )
        return candidates
