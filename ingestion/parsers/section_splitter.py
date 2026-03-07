"""Split document text into sections, identifying open-problem-relevant parts."""

import re
from dataclasses import dataclass


@dataclass
class Section:
    """A section extracted from a document."""

    heading: str
    text: str
    section_type: str  # "open_problems", "conjectures", "future_work", "discussion", "other"
    start_pos: int = 0
    end_pos: int = 0


# Patterns that indicate open-problem-relevant sections
SECTION_PATTERNS = {
    "open_problems": [
        r"(?i)open\s+problem",
        r"(?i)unsolved\s+problem",
        r"(?i)open\s+question",
        r"(?i)outstanding\s+problem",
    ],
    "conjectures": [
        r"(?i)conjecture",
        r"(?i)hypothesis",
        r"(?i)unproven",
    ],
    "future_work": [
        r"(?i)future\s+work",
        r"(?i)future\s+direction",
        r"(?i)open\s+direction",
        r"(?i)further\s+research",
    ],
    "discussion": [
        r"(?i)discussion",
        r"(?i)concluding\s+remark",
        r"(?i)conclusion",
    ],
}


def classify_section(heading: str, text: str) -> str:
    """Classify a section based on its heading and content."""
    combined = f"{heading} {text[:500]}"

    for section_type, patterns in SECTION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, combined):
                return section_type

    return "other"


def split_by_headings(text: str) -> list[Section]:
    """Split text into sections by markdown-style headings."""
    heading_pattern = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)
    matches = list(heading_pattern.finditer(text))

    if not matches:
        section_type = classify_section("", text)
        return [Section(heading="", text=text.strip(), section_type=section_type)]

    sections = []

    # Text before first heading
    if matches[0].start() > 0:
        pre_text = text[: matches[0].start()].strip()
        if pre_text:
            sections.append(Section(
                heading="",
                text=pre_text,
                section_type=classify_section("", pre_text),
                start_pos=0,
                end_pos=matches[0].start(),
            ))

    for i, match in enumerate(matches):
        heading = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()

        section_type = classify_section(heading, body)
        sections.append(Section(
            heading=heading,
            text=body,
            section_type=section_type,
            start_pos=match.start(),
            end_pos=end,
        ))

    return sections


def extract_relevant_sections(text: str) -> list[Section]:
    """Extract only the sections relevant to open problems."""
    sections = split_by_headings(text)
    return [s for s in sections if s.section_type != "other"]
