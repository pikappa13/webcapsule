"""Tests for webcapsule.markdown_gen."""

from webcapsule.markdown_gen import generate
from webcapsule.parser import ParsedPage

_PAGE = ParsedPage(
    title="Test Article",
    byline="Jane Doe",
    html_content="<h1>Hello</h1><p>This is the body.</p>",
    text_content="Hello This is the body.",
)

_PAGE_NO_BYLINE = ParsedPage(
    title="No Author",
    byline="",
    html_content="<p>Content.</p>",
    text_content="Content.",
)


def test_generate_returns_string():
    result = generate(_PAGE, "https://example.com/article")
    assert isinstance(result, str)


def test_generate_contains_front_matter():
    result = generate(_PAGE, "https://example.com/article")
    assert result.startswith("---")
    assert "---" in result[3:]


def test_generate_front_matter_has_title():
    result = generate(_PAGE, "https://example.com/article")
    assert 'title: "Test Article"' in result


def test_generate_front_matter_has_source():
    url = "https://example.com/article"
    result = generate(_PAGE, url)
    assert f"source: {url}" in result


def test_generate_front_matter_has_archived():
    result = generate(_PAGE, "https://example.com/article")
    assert "archived:" in result


def test_generate_front_matter_has_author_when_present():
    result = generate(_PAGE, "https://example.com/article")
    assert 'author: "Jane Doe"' in result


def test_generate_no_author_line_when_empty():
    result = generate(_PAGE_NO_BYLINE, "https://example.com/article")
    assert "author:" not in result


def test_generate_tags_in_front_matter():
    result = generate(_PAGE, "https://example.com/article", tags=["python", "cli"])
    assert "tags: [python, cli]" in result


def test_generate_body_contains_content():
    result = generate(_PAGE, "https://example.com/article")
    assert "Hello" in result
    assert "body" in result.lower() or "This is the body" in result


def test_generate_uses_separator():
    result = generate(_PAGE, "https://example.com/article")
    assert "\n\n---\n\n" in result


def test_generate_archived_is_utc_iso():
    result = generate(_PAGE, "https://example.com/article")
    import re

    assert re.search(r"archived: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", result)
