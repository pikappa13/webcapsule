"""Tests for webcapsule.metadata."""

from webcapsule.metadata import extract
from webcapsule.parser import ParsedPage

_PAGE = ParsedPage(
    title="Fallback Title",
    byline="Fallback Author",
    html_content="<p>content</p>",
    text_content="content word1 word2 word3",
)

OG_HTML = """
<html>
<head>
  <meta property="og:title" content="OG Title" />
  <meta property="og:description" content="OG description here." />
  <meta property="og:site_name" content="Example Site" />
  <meta property="article:author" content="Jane Doe" />
  <meta property="og:image" content="https://example.com/img.png" />
</head>
<body></body>
</html>
"""

JSONLD_HTML = """
<html>
<head>
<script type="application/ld+json">
{
  "@type": "Article",
  "headline": "JSON-LD Headline",
  "description": "JSON-LD description.",
  "author": {"@type": "Person", "name": "John Smith"},
  "datePublished": "2025-01-15"
}
</script>
</head>
<body></body>
</html>
"""

BARE_HTML = "<html><head><title>Bare Title</title></head><body></body></html>"


def test_extract_returns_dict():
    result = extract(OG_HTML, "https://example.com/article", _PAGE)
    assert isinstance(result, dict)


def test_extract_og_title():
    result = extract(OG_HTML, "https://example.com/article", _PAGE)
    assert result["title"] == "OG Title"


def test_extract_og_description():
    result = extract(OG_HTML, "https://example.com/article", _PAGE)
    assert result["description"] == "OG description here."


def test_extract_og_author():
    result = extract(OG_HTML, "https://example.com/article", _PAGE)
    assert result["author"] == "Jane Doe"


def test_extract_jsonld_title():
    result = extract(JSONLD_HTML, "https://example.com/article", _PAGE)
    assert result["title"] == "JSON-LD Headline"


def test_extract_jsonld_author():
    result = extract(JSONLD_HTML, "https://example.com/article", _PAGE)
    assert result["author"] == "John Smith"


def test_extract_jsonld_published_date():
    result = extract(JSONLD_HTML, "https://example.com/article", _PAGE)
    assert result["published_date"] == "2025-01-15"


def test_extract_fallback_title_from_page():
    result = extract(BARE_HTML, "https://example.com/article", _PAGE)
    assert result["title"] in ("Bare Title", "Fallback Title")


def test_extract_source_url():
    url = "https://example.com/article"
    result = extract(BARE_HTML, url, _PAGE)
    assert result["source_url"] == url


def test_extract_tags_stored():
    result = extract(BARE_HTML, "https://example.com/", _PAGE, tags=["python", "cli"])
    assert result["tags"] == ["python", "cli"]


def test_extract_word_count():
    result = extract(BARE_HTML, "https://example.com/", _PAGE)
    assert result["word_count"] == 4  # "content word1 word2 word3"


def test_extract_archived_date_present():
    result = extract(BARE_HTML, "https://example.com/", _PAGE)
    assert "archived_date" in result
    assert result["archived_date"]  # non-empty
