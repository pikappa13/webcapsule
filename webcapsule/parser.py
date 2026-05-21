"""
parser.py - Extract clean, readable content from raw HTML.

Uses readability-lxml as the primary extraction engine (same algorithm as
Firefox Reader View), then falls back to a BeautifulSoup heuristic that
grabs the largest <article> or <main> block if readability returns too little.
"""

from dataclasses import dataclass

from bs4 import BeautifulSoup
from readability import Document

# If readability extracts fewer characters than this, the page probably
# has no long-form article - fall back to the BS4 heuristic.
_MIN_READABILITY_CHARS = 200


@dataclass
class ParsedPage:
    """Clean content extracted from a web page."""

    title: str
    byline: str  # Author name(s) if detected
    html_content: str  # Cleaned HTML (still HTML, suitable for further conversion)
    text_content: str  # Plain-text version (whitespace-normalised)


def parse(raw_html: str) -> ParsedPage:
    """Extract readable content from *raw_html*.

    Args:
        raw_html: Full HTML string as returned by the fetcher.

    Returns:
        A :class:`ParsedPage` with title, byline, and cleaned content.
    """
    doc = Document(raw_html)
    title = doc.title() or ""
    byline = doc.author() if hasattr(doc, "author") else ""
    clean_html = doc.summary(html_partial=True)
    text = _html_to_text(clean_html)

    if len(text) < _MIN_READABILITY_CHARS:
        # readability found very little - try the BS4 fallback
        clean_html, text = _bs4_fallback(raw_html)

    return ParsedPage(
        title=title.strip(),
        byline=(byline or "").strip(),
        html_content=clean_html,
        text_content=text,
    )


def _html_to_text(html: str) -> str:
    """Strip tags and normalise whitespace."""
    soup = BeautifulSoup(html, "html.parser")
    return " ".join(soup.get_text(separator=" ").split())


def _bs4_fallback(raw_html: str) -> tuple[str, str]:
    """Return (html, text) from the largest semantic block in *raw_html*."""
    soup = BeautifulSoup(raw_html, "html.parser")

    # Prefer <article> or <main>; fall back to the whole <body>.
    for tag in ("article", "main", "body"):
        block = soup.find(tag)
        if block:
            html = str(block)
            text = " ".join(block.get_text(separator=" ").split())
            if text:
                return html, text

    return raw_html, _html_to_text(raw_html)
