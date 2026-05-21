"""
markdown_gen.py - Convert a parsed page into clean, portable Markdown.

The output is intentionally minimal: a YAML-like front-matter block with
key metadata, followed by the article body converted from HTML to Markdown.
This makes every capsule readable in any text editor, Git viewer, or
Obsidian-style knowledge base without any extra tooling.
"""

from datetime import UTC, datetime

import markdownify

from webcapsule.parser import ParsedPage


def generate(page: ParsedPage, url: str, tags: list[str] | None = None) -> str:
    """Produce a Markdown string for *page*.

    Args:
        page:  Parsed content from :mod:`webcapsule.parser`.
        url:   Original source URL (stored verbatim for traceability).
        tags:  Optional list of user-supplied topic tags.

    Returns:
        A UTF-8-safe Markdown string ready to write to ``content.md``.
    """
    front_matter = _build_front_matter(page, url, tags or [])
    body = _html_to_markdown(page.html_content)
    return f"{front_matter}\n\n---\n\n{body}\n"


def _build_front_matter(page: ParsedPage, url: str, tags: list[str]) -> str:
    """Produce a fenced YAML front-matter block."""
    archived_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    tag_line = ", ".join(tags) if tags else ""

    lines = [
        "---",
        f'title: "{_escape(page.title)}"',
        f"source: {url}",
        f"archived: {archived_at}",
    ]
    if page.byline:
        lines.append(f'author: "{_escape(page.byline)}"')
    if tag_line:
        lines.append(f"tags: [{tag_line}]")
    lines.append("---")

    return "\n".join(lines)


def _html_to_markdown(html: str) -> str:
    """Convert cleaned HTML to readable Markdown via markdownify."""
    return markdownify.markdownify(
        html,
        heading_style=markdownify.ATX,  # Use # headings, not underline style
        strip=["script", "style", "iframe", "noscript"],
    ).strip()


def _escape(text: str) -> str:
    """Escape double-quotes inside YAML string values."""
    return text.replace('"', '\\"')
