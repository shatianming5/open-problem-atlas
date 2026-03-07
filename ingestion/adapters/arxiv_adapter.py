"""arXiv adapter for discovering papers with open problems."""

import logging
import xml.etree.ElementTree as ET

import httpx

from .base import BaseAdapter, CandidateProblem, RawSourceRecord

logger = logging.getLogger(__name__)

ARXIV_API = "http://export.arxiv.org/api/query"

# arXiv categories relevant to our domains
CATEGORIES = [
    "math.NT",  # Number Theory
    "math.CO",  # Combinatorics
    "math.GR",  # Group Theory
    "math.AG",  # Algebraic Geometry
    "math.AT",  # Algebraic Topology
    "math.AP",  # Analysis of PDEs
    "cs.CC",    # Computational Complexity
    "cs.DS",    # Data Structures and Algorithms
    "cs.DM",    # Discrete Mathematics
    "quant-ph", # Quantum Physics
    "math-ph",  # Mathematical Physics
]

NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


class ArxivAdapter(BaseAdapter):
    """Adapter for arXiv API to find papers discussing open problems."""

    def __init__(self):
        self.client = httpx.Client(timeout=30)

    @property
    def source_name(self) -> str:
        return "arXiv"

    @property
    def source_tier(self) -> int:
        return 1  # arXiv papers are primary sources

    def _search(self, query: str, category: str, max_results: int = 20) -> list[dict]:
        """Search arXiv API."""
        search_query = f"all:{query} AND cat:{category}"
        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            resp = self.client.get(ARXIV_API, params=params)
            resp.raise_for_status()
            return self._parse_response(resp.text)
        except httpx.HTTPError as e:
            logger.warning("arXiv search failed for '%s' in %s: %s", query, category, e)
            return []

    def _parse_response(self, xml_text: str) -> list[dict]:
        """Parse arXiv Atom XML response."""
        root = ET.fromstring(xml_text)
        entries = []

        for entry in root.findall("atom:entry", NS):
            arxiv_id_el = entry.find("atom:id", NS)
            title_el = entry.find("atom:title", NS)
            summary_el = entry.find("atom:summary", NS)

            if arxiv_id_el is None or title_el is None:
                continue

            arxiv_id = arxiv_id_el.text.strip().split("/abs/")[-1]
            authors = []
            for author in entry.findall("atom:author", NS):
                name_el = author.find("atom:name", NS)
                if name_el is not None:
                    authors.append(name_el.text.strip())

            categories = []
            for cat in entry.findall("arxiv:primary_category", NS):
                term = cat.get("term")
                if term:
                    categories.append(term)

            published = entry.find("atom:published", NS)
            year = None
            if published is not None and published.text:
                year = int(published.text[:4])

            entries.append({
                "arxiv_id": arxiv_id,
                "title": " ".join(title_el.text.strip().split()),
                "summary": summary_el.text.strip() if summary_el is not None else "",
                "authors": authors,
                "categories": categories,
                "year": year,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
            })

        return entries

    def fetch(
        self,
        queries: list[str] | None = None,
        categories: list[str] | None = None,
        max_results: int = 20,
    ) -> list[RawSourceRecord]:
        """Fetch papers from arXiv matching open-problem queries."""
        queries = queries or ["open problem", "conjecture", "unsolved"]
        categories = categories or CATEGORIES[:5]  # Start with top categories
        records = []
        seen_ids = set()

        for category in categories:
            for query in queries:
                entries = self._search(query, category, max_results)
                for entry in entries:
                    aid = entry["arxiv_id"]
                    if aid in seen_ids:
                        continue
                    seen_ids.add(aid)

                    record = RawSourceRecord(
                        source_id=f"arxiv_{aid.replace('.', '_').replace('/', '_')}",
                        source_kind="preprint",
                        source_tier=self.source_tier,
                        title=entry["title"],
                        authors=entry["authors"],
                        year=entry["year"],
                        url=entry["url"],
                        content_sections=[{"type": "abstract", "text": entry["summary"]}],
                        metadata={
                            "arxiv_id": aid,
                            "categories": entry["categories"],
                        },
                    )
                    records.append(record)

        logger.info("Fetched %d records from arXiv", len(records))
        return records

    def extract_candidates(self, records: list[RawSourceRecord]) -> list[CandidateProblem]:
        """Extract candidate problems from arXiv abstracts.

        This is a basic extraction based on abstract keywords.
        Full extraction requires downloading and parsing the paper PDF.
        """
        candidates = []
        keywords = ["conjecture", "open problem", "open question", "we ask whether", "it remains open"]

        for record in records:
            abstract = ""
            for section in record.content_sections:
                if section.get("type") == "abstract":
                    abstract = section.get("text", "")
                    break

            abstract_lower = abstract.lower()
            if any(kw in abstract_lower for kw in keywords):
                candidate = CandidateProblem(
                    title=record.title,
                    statement=abstract,
                    source_id=record.source_id,
                    domain_hint=self._guess_domain(record),
                    confidence=0.4,
                    raw_text=abstract,
                    extraction_method="arxiv_abstract_keyword",
                )
                candidates.append(candidate)

        logger.info("Extracted %d candidates from %d arXiv records", len(candidates), len(records))
        return candidates

    def _guess_domain(self, record: RawSourceRecord) -> str:
        """Guess domain from arXiv categories."""
        cats = set(record.metadata.get("categories", []))
        if cats & {"math.NT", "math.CO", "math.AG", "math.AT", "math.GR", "math.AP"}:
            return "mathematics"
        if cats & {"cs.CC", "cs.DS", "cs.DM"}:
            return "theoretical-cs"
        if cats & {"quant-ph", "math-ph", "hep-th"}:
            return "mathematical-physics"
        return ""
