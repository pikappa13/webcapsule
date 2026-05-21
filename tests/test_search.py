"""Tests for webcapsule.search."""

import json
from pathlib import Path

import pytest

from webcapsule import search as search_mod

_META = {
    "title": "Climate Change Effects",
    "source_url": "https://example.com/climate",
    "author": "Jane Doe",
    "description": "Ocean temperatures are rising due to climate change.",
    "archived_date": "2025-05-20T10:00:00+00:00",
    "tags": ["climate", "ocean"],
    "word_count": 10,
}

_META2 = {
    "title": "Python Tips",
    "source_url": "https://example.com/python",
    "author": "John Smith",
    "description": "Useful tips for Python developers.",
    "archived_date": "2025-05-19T10:00:00+00:00",
    "tags": ["python", "dev"],
    "word_count": 8,
}

_CONTENT_MD = """\
---
title: "Climate Change Effects"
source: https://example.com/climate
archived: 2025-05-20T10:00:00Z
---

Ocean temperatures are rising due to climate change. Coral reefs are bleaching.
"""

_CONTENT_MD2 = """\
---
title: "Python Tips"
source: https://example.com/python
archived: 2025-05-19T10:00:00Z
---

Useful tips for Python developers. List comprehensions, generators, and more.
"""


def _make_capsule(root: Path, name: str, meta: dict, content: str) -> Path:
    caps = root / "general" / name
    caps.mkdir(parents=True)
    (caps / "content.md").write_text(content, encoding="utf-8")
    (caps / "metadata.json").write_text(json.dumps(meta), encoding="utf-8")
    return caps


@pytest.fixture()
def archive(tmp_path):
    c1 = _make_capsule(tmp_path, "climate-article", _META, _CONTENT_MD)
    c2 = _make_capsule(tmp_path, "python-tips", _META2, _CONTENT_MD2)
    search_mod.index_capsule(tmp_path, c1, _META)
    search_mod.index_capsule(tmp_path, c2, _META2)
    return tmp_path


def test_search_finds_by_title(archive):
    results = search_mod.search(archive, "Climate")
    assert len(results) >= 1
    assert any("Climate" in r["title"] for r in results)


def test_search_finds_by_body_text(archive):
    results = search_mod.search(archive, "bleaching")
    assert len(results) >= 1


def test_search_finds_by_description(archive):
    results = search_mod.search(archive, "coral")
    # "coral" only appears in the body; this validates full-text body indexing
    assert len(results) >= 1


def test_search_no_results_returns_empty(archive):
    results = search_mod.search(archive, "zxqwerty12345")
    assert results == []


def test_search_result_has_expected_keys(archive):
    results = search_mod.search(archive, "Climate")
    assert results
    r = results[0]
    for key in ("title", "url", "path", "archived"):
        assert key in r


def test_list_all_returns_all_capsules(archive):
    all_caps = search_mod.list_all(archive)
    assert len(all_caps) == 2


def test_list_all_newest_first(archive):
    all_caps = search_mod.list_all(archive)
    assert all_caps[0]["archived"] >= all_caps[1]["archived"]


def test_reindex_same_capsule_does_not_duplicate(archive):
    caps_path = archive / "general" / "climate-article"
    search_mod.index_capsule(archive, caps_path, _META)
    search_mod.index_capsule(archive, caps_path, _META)
    all_caps = search_mod.list_all(archive)
    climate_entries = [c for c in all_caps if "Climate" in (c["title"] or "")]
    assert len(climate_entries) == 1


def test_rebuild_index(tmp_path):
    _make_capsule(tmp_path, "climate-article", _META, _CONTENT_MD)
    _make_capsule(tmp_path, "python-tips", _META2, _CONTENT_MD2)
    count = search_mod.rebuild_index(tmp_path)
    assert count == 2
    all_caps = search_mod.list_all(tmp_path)
    assert len(all_caps) == 2


def test_read_body_strips_front_matter(tmp_path):
    caps = tmp_path / "test-caps"
    caps.mkdir()
    (caps / "content.md").write_text(_CONTENT_MD, encoding="utf-8")
    body = search_mod._read_body(caps)
    assert "---" not in body
    assert "bleaching" in body


def test_read_body_missing_file_returns_empty(tmp_path):
    caps = tmp_path / "empty-caps"
    caps.mkdir()
    assert search_mod._read_body(caps) == ""
