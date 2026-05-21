"""Tests for webcapsule.parser."""

from webcapsule.parser import ParsedPage, parse

SIMPLE_ARTICLE = """
<html>
<head><title>Test Article</title></head>
<body>
  <article>
    <h1>Hello World</h1>
    <p>This is a paragraph with enough content to pass the readability threshold.
    It contains multiple sentences so that readability can extract it properly.
    The quick brown fox jumps over the lazy dog. Again and again.</p>
    <p>Second paragraph to make the article longer and trigger proper extraction.</p>
  </article>
</body>
</html>
"""

MINIMAL_HTML = "<html><head><title>Tiny</title></head><body><p>Hi</p></body></html>"

EMPTY_HTML = "<html><body></body></html>"


def test_parse_returns_parsed_page():
    result = parse(SIMPLE_ARTICLE)
    assert isinstance(result, ParsedPage)


def test_parse_extracts_title():
    result = parse(SIMPLE_ARTICLE)
    assert "Test Article" in result.title or "Hello World" in result.title


def test_parse_extracts_text_content():
    result = parse(SIMPLE_ARTICLE)
    assert "Hello World" in result.text_content or "paragraph" in result.text_content


def test_parse_html_content_is_string():
    result = parse(SIMPLE_ARTICLE)
    assert isinstance(result.html_content, str)
    assert len(result.html_content) > 0


def test_parse_minimal_html_does_not_crash():
    result = parse(MINIMAL_HTML)
    assert isinstance(result, ParsedPage)


def test_parse_empty_body_does_not_crash():
    result = parse(EMPTY_HTML)
    assert isinstance(result, ParsedPage)
    assert isinstance(result.title, str)
    assert isinstance(result.text_content, str)
