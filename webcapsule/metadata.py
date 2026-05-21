"""
metadata.py - Extract and assemble structured metadata for a capsule.

Metadata is gathered from four sources (in order of trust):
  1. OpenGraph / Twitter Card <meta> tags  (most sites set these)
  2. Standard <meta> tags (description, author, keywords)
  3. JSON-LD structured data embedded in the page
  4. readability's own title / byline detection (fallback)

Everything ends up in a plain dict that gets serialised to metadata.json.
The format is intentionally simple so it can be read without any tooling.
"""

import json
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from bs4.element import Tag

from webcapsule.parser import ParsedPage


def extract(
    raw_html: str, url: str, page: ParsedPage, tags: list[str] | None = None
) -> dict[str, Any]:
    """Build a metadata dict for a capsule.

    Args:
        raw_html: Original HTML (used for meta-tag scraping).
        url:      Source URL.
        page:     Already-parsed content from :mod:`webcapsule.parser`.
        tags:     Optional user-supplied topic tags.

    Returns:
        A JSON-serialisable dict ready to write to ``metadata.json``.
    """
    soup = BeautifulSoup(raw_html, "html.parser")

    og = _og_tags(soup)
    standard = _standard_tags(soup)
    jsonld = _json_ld(soup)

    # Resolve each field with a clear priority order.
    title = og.get("title") or jsonld.get("headline") or standard.get("title") or page.title or ""
    description = (
        og.get("description") or jsonld.get("description") or standard.get("description") or ""
    )
    author = og.get("author") or jsonld.get("author") or standard.get("author") or page.byline or ""
    published = jsonld.get("datePublished") or og.get("published_time") or ""
    image = og.get("image") or jsonld.get("image") or ""
    site_name = og.get("site_name") or urlparse(url).netloc

    return {
        "title": title.strip(),
        "source_url": url,
        "site_name": site_name,
        "author": author.strip(),
        "description": description.strip(),
        "published_date": published,
        "archived_date": datetime.now(UTC).isoformat(),
        "tags": tags or [],
        "og_image": image,
        "word_count": len(page.text_content.split()),
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _og_tags(soup: BeautifulSoup) -> dict[str, str]:
    """Extract OpenGraph and Twitter Card meta properties."""
    result: dict[str, str] = {}
    for tag in soup.find_all("meta"):
        if not isinstance(tag, Tag):
            continue
        prop = _attr_as_str(tag.get("property")) or _attr_as_str(tag.get("name"))
        content = _attr_as_str(tag.get("content"))
        if not prop or not content:
            continue
        # Normalise: "og:title" -> "title", "twitter:description" -> "description"
        key = re.sub(r"^(og|twitter|article):", "", prop.lower())
        result.setdefault(key, content)
    return result


def _standard_tags(soup: BeautifulSoup) -> dict[str, str]:
    """Extract classic <meta name="..."> values."""
    result: dict[str, str] = {}

    title_tag = soup.find("title")
    if title_tag:
        result["title"] = title_tag.get_text(strip=True)

    for name in ("description", "author", "keywords"):
        tag = soup.find("meta", attrs={"name": name})
        if isinstance(tag, Tag):
            content = _attr_as_str(tag.get("content"))
            if content:
                result[name] = content

    return result


def _json_ld(soup: BeautifulSoup) -> dict[str, Any]:
    """Parse the first JSON-LD <script> block on the page."""
    script = soup.find("script", attrs={"type": "application/ld+json"})
    if not isinstance(script, Tag):
        return {}
    try:
        data = json.loads(script.string or "")
        # JSON-LD can nest inside @graph arrays
        if isinstance(data, list):
            data = data[0] if data else {}
        if isinstance(data, dict) and "@graph" in data:
            data = data["@graph"][0] if data["@graph"] else {}
        # Flatten author to a string
        if isinstance(data.get("author"), dict):
            data["author"] = data["author"].get("name", "")
        if isinstance(data.get("author"), list):
            data["author"] = ", ".join(
                a.get("name", "") if isinstance(a, dict) else str(a) for a in data["author"]
            )
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, AttributeError):
        return {}


def _attr_as_str(value: Any) -> str:
    """Return a BeautifulSoup attribute as a plain string."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return ""
