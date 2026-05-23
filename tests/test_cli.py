"""Tests for the WebCapsule command-line interface."""

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from webcapsule.cli import app
from webcapsule.parser import ParsedPage

runner = CliRunner()

_META = {
    "title": "Climate Change Effects",
    "source_url": "https://example.com/climate",
    "author": "Jane Doe",
    "description": "Ocean temperatures are rising due to climate change.",
    "archived_date": "2025-05-20T10:00:00+00:00",
    "tags": ["climate", "ocean"],
    "word_count": 10,
}

_CONTENT_MD = """\
---
title: "Climate Change Effects"
source: https://example.com/climate
archived: 2025-05-20T10:00:00Z
---

Ocean temperatures are rising due to climate change. Coral reefs are bleaching.
"""


def _make_capsule(root: Path, name: str = "climate-article") -> Path:
    capsule = root / "general" / name
    capsule.mkdir(parents=True)
    (capsule / "content.md").write_text(_CONTENT_MD, encoding="utf-8")
    (capsule / "metadata.json").write_text(json.dumps(_META), encoding="utf-8")
    return capsule


def test_cli_version():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "WebCapsule 0.1.0" in result.output


def test_cli_list_empty_archive(tmp_path, monkeypatch):
    monkeypatch.setenv("WEBCAPSULE_ARCHIVE", str(tmp_path))

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "No capsules archived yet" in result.output


def test_cli_rebuild_index(tmp_path, monkeypatch):
    monkeypatch.setenv("WEBCAPSULE_ARCHIVE", str(tmp_path))
    _make_capsule(tmp_path)

    result = runner.invoke(app, ["rebuild-index"])

    assert result.exit_code == 0
    assert "Indexed 1 capsule" in result.output


def test_cli_search_indexed_archive(tmp_path, monkeypatch):
    monkeypatch.setenv("WEBCAPSULE_ARCHIVE", str(tmp_path))
    _make_capsule(tmp_path)
    rebuild = runner.invoke(app, ["rebuild-index"])
    assert rebuild.exit_code == 0

    result = runner.invoke(app, ["search", "bleaching"])

    assert result.exit_code == 0
    assert "Climate Change Effects" in result.output


def test_cli_open_uses_readme_for_capsule_directory(tmp_path):
    capsule = _make_capsule(tmp_path)
    readme = capsule / "README.md"
    readme.write_text("# Climate Change Effects", encoding="utf-8")

    with patch("webcapsule.cli._open_path") as mock_open:
        result = runner.invoke(app, ["open", str(capsule)])

    assert result.exit_code == 0
    mock_open.assert_called_once_with(readme)
    assert "Opened" in result.output


def test_cli_open_missing_path_fails(tmp_path):
    result = runner.invoke(app, ["open", str(tmp_path / "missing")])

    assert result.exit_code == 1
    assert "path does not exist" in result.output


def test_cli_save_dry_run_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("WEBCAPSULE_ARCHIVE", str(tmp_path))
    page = ParsedPage(
        title="Dry Run Article",
        byline="",
        html_content="<p>Hello world</p>",
        text_content="Hello world",
    )

    with (
        patch("webcapsule.cli.fetcher.fetch", return_value="<html><body>Hello world</body></html>"),
        patch("webcapsule.cli.parser.parse", return_value=page),
    ):
        result = runner.invoke(app, ["save", "https://example.com/dry", "--dry-run"])

    assert result.exit_code == 0
    assert "Dry run complete" in result.output
    assert "No files written" in result.output
    assert not list(tmp_path.rglob("metadata.json"))


def test_cli_save_skips_recent_duplicate(tmp_path, monkeypatch):
    monkeypatch.setenv("WEBCAPSULE_ARCHIVE", str(tmp_path))
    capsule = _make_capsule(tmp_path)
    meta = dict(_META, archived_date=datetime.now(UTC).isoformat())
    (capsule / "metadata.json").write_text(json.dumps(meta), encoding="utf-8")

    with patch("webcapsule.cli.fetcher.fetch") as mock_fetch:
        result = runner.invoke(app, ["save", "https://example.com/climate"])

    assert result.exit_code == 0
    assert "Skipped" in result.output
    mock_fetch.assert_not_called()
