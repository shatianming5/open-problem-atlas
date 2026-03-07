"""Open Problem Garden adapter.

Ingests open problems from https://www.openproblemgarden.org by scraping the
HTML problem listing pages.
"""

import logging
import re
from urllib.parse import urljoin

import httpx

from .base import BaseAdapter, CandidateProblem, RawSourceRecord

logger = logging.getLogger(__name__)

BASE_URL = "https://www.openproblemgarden.org"
# The site organises problems under /category/ pages; the main listing is at:
PROBLEMS_LIST_URL = f"{BASE_URL}/open-problems"


class OpenProblemGardenAdapter(BaseAdapter):
    """Adapter for Open Problem Garden (openproblemgarden.org).

    The site provides a curated collection of open problems in mathematics,
    graph theory, combinatorics and related fields.  Problems are listed on
    HTML pages with metadata such as category and importance (star rating).
    """

    def __init__(self):
        self.client = httpx.Client(
            timeout=30,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "OpenQuestionBot/1.0 "
                    "(+https://github.com/openquestion; research use)"
                ),
            },
        )

    # ------------------------------------------------------------------
    # BaseAdapter interface
    # ------------------------------------------------------------------

    @property
    def source_name(self) -> str:
        return "OpenProblemGarden"

    @property
    def source_tier(self) -> int:
        return 1

    # ------------------------------------------------------------------
    # Lightweight HTML helpers (no BeautifulSoup dependency)
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_links(html: str, pattern: str) -> list[dict]:
        """Return ``[{href, text}]`` for ``<a>`` tags whose *href* matches
        *pattern*."""
        link_re = re.compile(
            r'<a\s[^>]*href=["\']([^"\']*' + pattern + r'[^"\']*)["\'][^>]*>'
            r"(.*?)</a>",
            re.IGNORECASE | re.DOTALL,
        )
        results = []
        for m in link_re.finditer(html):
            href = m.group(1).strip()
            text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if text:
                results.append({"href": href, "text": text})
        return results

    @staticmethod
    def _extract_meta_text(html: str, label: str) -> str:
        """Attempt to extract a metadata value that follows *label* in the
        HTML (e.g. ``Category: <value>``)."""
        pat = re.compile(
            re.escape(label) + r"\s*:?\s*</?\w[^>]*>\s*(.*?)\s*<",
            re.IGNORECASE | re.DOTALL,
        )
        m = pat.search(html)
        return m.group(1).strip() if m else ""

    @staticmethod
    def _extract_importance(html: str) -> str:
        """Heuristic to extract an importance/star rating from the page HTML."""
        # Many garden pages use "★" or star images to indicate importance.
        star_count = html.count("\u2605")  # ★
        if star_count:
            return f"{star_count}-star"
        # Fallback: look for text like "Importance: High"
        m = re.search(
            r"(?:importance|priority)\s*:?\s*(\w+)", html, re.IGNORECASE
        )
        return m.group(1).strip() if m else ""

    @staticmethod
    def _extract_body_text(html: str) -> str:
        """Very rough HTML-to-text: strip tags and collapse whitespace."""
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ------------------------------------------------------------------
    # Internal fetching
    # ------------------------------------------------------------------

    def _fetch_listing_page(self, url: str) -> str:
        """Download a single listing page and return its HTML."""
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
            return resp.text
        except httpx.HTTPError as exc:
            logger.warning("Failed to fetch listing page %s: %s", url, exc)
            return ""

    def _discover_problem_urls(self, max_pages: int = 10) -> list[dict]:
        """Crawl the listing pages and collect individual problem URLs."""
        all_links: list[dict] = []
        seen_hrefs: set[str] = set()

        url = PROBLEMS_LIST_URL
        for page_num in range(max_pages):
            html = self._fetch_listing_page(url)
            if not html:
                break

            # Problem links typically match /op/<slug> or /node/<id>.
            links = self._extract_links(html, r"/op/|/node/")
            for link in links:
                abs_href = urljoin(BASE_URL, link["href"])
                if abs_href not in seen_hrefs:
                    seen_hrefs.add(abs_href)
                    all_links.append({"href": abs_href, "text": link["text"]})

            # Find a "next page" link.
            next_links = self._extract_links(html, r"page=")
            next_url = None
            for nl in next_links:
                if "next" in nl["text"].lower() or ">" in nl["text"]:
                    next_url = urljoin(BASE_URL, nl["href"])
                    break
            if next_url and next_url != url:
                url = next_url
            else:
                break

        logger.info(
            "Discovered %d problem URLs from OpenProblemGarden", len(all_links)
        )
        return all_links

    def _fetch_problem_page(self, url: str) -> str:
        """Download a single problem detail page."""
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
            return resp.text
        except httpx.HTTPError as exc:
            logger.warning("Failed to fetch problem page %s: %s", url, exc)
            return ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch(
        self, max_pages: int = 10, max_problems: int = 200, **kwargs
    ) -> list[RawSourceRecord]:
        """Fetch problem records from Open Problem Garden.

        Args:
            max_pages: Maximum number of listing pages to crawl.
            max_problems: Maximum number of individual problem pages to
                download.

        Returns:
            A list of ``RawSourceRecord`` instances.
        """
        problem_links = self._discover_problem_urls(max_pages)
        records: list[RawSourceRecord] = []

        for link in problem_links[:max_problems]:
            href = link["href"]
            title = link["text"]
            html = self._fetch_problem_page(href)
            if not html:
                continue

            body_text = self._extract_body_text(html)
            category = self._extract_meta_text(html, "Category")
            importance = self._extract_importance(html)
            slug = href.rstrip("/").rsplit("/", 1)[-1]

            record = RawSourceRecord(
                source_id=f"opg_{slug}",
                source_kind="problem_list",
                source_tier=self.source_tier,
                title=title,
                url=href,
                content_sections=[
                    {"type": "description", "text": body_text},
                ],
                metadata={
                    "category": category,
                    "importance": importance,
                    "slug": slug,
                },
            )
            records.append(record)

        logger.info(
            "Fetched %d records from OpenProblemGarden", len(records)
        )
        return records

    def extract_candidates(
        self, records: list[RawSourceRecord]
    ) -> list[CandidateProblem]:
        """Extract candidate open problems from scraped Garden pages."""
        candidates: list[CandidateProblem] = []

        for record in records:
            description = ""
            for section in record.content_sections:
                if section.get("type") == "description":
                    description = section.get("text", "")
                    break

            importance = record.metadata.get("importance", "")
            # Assign higher confidence to problems with an explicit importance
            # rating.
            confidence = 0.8 if importance else 0.65

            candidate = CandidateProblem(
                title=record.title,
                statement=description[:2000] if description else record.title,
                source_id=record.source_id,
                source_locator=record.url or "",
                domain_hint="mathematics",
                subdomain_hint=record.metadata.get("category", ""),
                problem_type_hint="open_problem",
                confidence=confidence,
                raw_text=description,
                extraction_method="opg_html_scrape",
            )
            candidates.append(candidate)

        logger.info(
            "Extracted %d candidates from %d OpenProblemGarden records",
            len(candidates),
            len(records),
        )
        return candidates
