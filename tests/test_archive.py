"""Tests for webcapsule.archive."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from webcapsule.archive import _slugify, find_recent_capsule, write_capsule
from webcapsule.parser import ParsedPage

_PAGE = ParsedPage(
    title="My Test Article",
    byline="Jane Doe",
    html_content="<p>Hello world.</p>",
    text_content="Hello world.",
)

_META = {
    "title": "My Test Article",
    "source_url": "https://example.com/article",
    "site_name": "example.com",
    "author": "Jane Doe",
    "description": "A test article.",
    "published_date": "2025-01-01",
    "archived_date": "2025-05-20T10:00:00+00:00",
    "tags": ["test"],
    "og_image": "",
    "word_count": 2,
}

_MARKDOWN = '---\ntitle: "My Test Article"\nsource: https://example.com/article\narchived: 2025-05-20T10:00:00Z\n---\n\nHello world.'

_RAW_HTML = "<html><body><p>Hello world.</p></body></html>"


@pytest.fixture()
def capsule_dir(tmp_path):
    return write_capsule(
        archive_root=tmp_path,
        collection="tests",
        url="https://example.com/article",
        raw_html=_RAW_HTML,
        page=_PAGE,
        markdown=_MARKDOWN,
        metadata=_META,
        screenshot_data=None,
    )


def test_write_capsule_returns_path(capsule_dir):
    assert isinstance(capsule_dir, Path)
    assert capsule_dir.exists()


def test_write_capsule_creates_content_md(capsule_dir):
    assert (capsule_dir / "content.md").exists()


def test_write_capsule_creates_original_html(capsule_dir):
    assert (capsule_dir / "original.html").exists()


def test_write_capsule_creates_metadata_json(capsule_dir):
    assert (capsule_dir / "metadata.json").exists()


def test_write_capsule_creates_readme(capsule_dir):
    assert (capsule_dir / "README.md").exists()


def test_write_capsule_creates_checksum(capsule_dir):
    assert (capsule_dir / "checksum.sha256").exists()


def test_write_capsule_no_screenshot_file_when_none(capsule_dir):
    assert not (capsule_dir / "screenshot.png").exists()


def test_write_capsule_creates_screenshot_when_provided(tmp_path):
    caps = write_capsule(
        archive_root=tmp_path,
        collection="tests",
        url="https://example.com/article",
        raw_html=_RAW_HTML,
        page=_PAGE,
        markdown=_MARKDOWN,
        metadata=_META,
        screenshot_data=b"\x89PNG\r\n\x1a\n",  # minimal PNG header
    )
    assert (caps / "screenshot.png").exists()


def test_metadata_json_is_valid(capsule_dir):
    data = json.loads((capsule_dir / "metadata.json").read_text(encoding="utf-8"))
    assert data["title"] == "My Test Article"
    assert data["source_url"] == "https://example.com/article"


def test_checksum_covers_all_files(capsule_dir):
    checksum_text = (capsule_dir / "checksum.sha256").read_text(encoding="utf-8")
    file_names = {line.split("  ")[1] for line in checksum_text.strip().splitlines()}
    assert "content.md" in file_names
    assert "original.html" in file_names
    assert "metadata.json" in file_names
    assert "README.md" in file_names
    assert "checksum.sha256" not in file_names


def test_capsule_dir_under_collection(tmp_path):
    caps = write_capsule(
        archive_root=tmp_path,
        collection="science",
        url="https://example.com/article",
        raw_html=_RAW_HTML,
        page=_PAGE,
        markdown=_MARKDOWN,
        metadata=_META,
    )
    assert caps.parent.name == "science"


def test_slugify_basic():
    assert _slugify("Hello World!") == "hello-world"


def test_slugify_special_chars():
    assert _slugify("Python 3.11 - What's New?") == "python-311-whats-new"


def test_slugify_empty():
    assert _slugify("") == "untitled"


def test_find_recent_capsule_returns_recent_match(tmp_path):
    caps = tmp_path / "general" / "recent"
    caps.mkdir(parents=True)
    meta = {
        "source_url": "https://example.com/article",
        "archived_date": datetime.now(UTC).isoformat(),
    }
    (caps / "metadata.json").write_text(json.dumps(meta), encoding="utf-8")

    assert find_recent_capsule(tmp_path, "https://example.com/article") == caps


def test_find_recent_capsule_ignores_old_match(tmp_path):
    caps = tmp_path / "general" / "old"
    caps.mkdir(parents=True)
    meta = {
        "source_url": "https://example.com/article",
        "archived_date": (datetime.now(UTC) - timedelta(hours=25)).isoformat(),
    }
    (caps / "metadata.json").write_text(json.dumps(meta), encoding="utf-8")

    assert find_recent_capsule(tmp_path, "https://example.com/article") is None
