"""SEO edge-case tests for metadata extraction."""

import pytest
from webcapsule.metadata import extract
from webcapsule.parser import ParsedPage

PAGE = ParsedPage(title="Fallback", byline="", html_content="<p>x</p>", text_content="hello world")


def test_twitter_card_title():
    html = """<html><head>
  <meta name="twitter:title" content="Twitter Title"/>
  <meta name="twitter:description" content="Twitter desc"/>
  <meta name="twitter:image" content="https://cdn.example.com/tw.jpg"/>
</head><body></body></html>"""
    r = extract(html, "https://x.com/page", PAGE)
    assert r["title"] == "Twitter Title"
    assert r["description"] == "Twitter desc"
    assert r["og_image"] == "https://cdn.example.com/tw.jpg"


def test_jsonld_graph_nesting():
    html = """<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
  {"@type":"Article","headline":"Graph Headline","description":"Graph desc",
   "author":{"@type":"Person","name":"Alice"},"datePublished":"2024-06-01"}
]}
</script>
</head><body></body></html>"""
    r = extract(html, "https://blog.com/post", PAGE)
    assert r["title"] == "Graph Headline"
    assert r["author"] == "Alice"
    assert r["published_date"] == "2024-06-01"


def test_jsonld_multi_author():
    html = """<html><head>
<script type="application/ld+json">
{"@type":"Article","headline":"Multi",
 "author":[{"@type":"Person","name":"Bob"},{"@type":"Person","name":"Carol"}]}
</script>
</head><body></body></html>"""
    r = extract(html, "https://blog.com/multi", PAGE)
    assert r["author"] == "Bob, Carol"


def test_jsonld_date_beats_og_published_time():
    """JSON-LD datePublished should take priority over article:published_time."""
    html = """<html><head>
  <meta property="article:published_time" content="2020-01-01T00:00:00Z"/>
<script type="application/ld+json">
{"@type":"Article","headline":"P","datePublished":"2024-12-01"}
</script>
</head><body></body></html>"""
    r = extract(html, "https://blog.com/priority", PAGE)
    assert r["published_date"] == "2024-12-01"


def test_site_name_falls_back_to_netloc():
    html = "<html><head><title>T</title></head><body></body></html>"
    r = extract(html, "https://example.org/path/to/page", PAGE)
    assert r["site_name"] == "example.org"


def test_jsonld_image_field():
    html = """<html><head>
<script type="application/ld+json">
{"@type":"Article","headline":"Img","image":"https://cdn.example.com/hero.jpg"}
</script>
</head><body></body></html>"""
    r = extract(html, "https://blog.com/img", PAGE)
    assert r["og_image"] == "https://cdn.example.com/hero.jpg"


def test_og_beats_jsonld_for_title():
    """OG title should win over JSON-LD headline."""
    html = """<html><head>
  <meta property="og:title" content="OG Wins"/>
<script type="application/ld+json">
{"@type":"Article","headline":"JSON-LD Loses"}
</script>
</head><body></body></html>"""
    r = extract(html, "https://blog.com/og-wins", PAGE)
    assert r["title"] == "OG Wins"


def test_empty_html_does_not_crash():
    r = extract("", "https://example.com/", PAGE)
    assert r["title"] == "Fallback"
    assert r["source_url"] == "https://example.com/"


def test_malformed_jsonld_does_not_crash():
    html = """<html><head>
<script type="application/ld+json">{ invalid json }</script>
</head><body></body></html>"""
    r = extract(html, "https://example.com/", PAGE)
    assert isinstance(r, dict)
    assert r["title"] == "Fallback"
