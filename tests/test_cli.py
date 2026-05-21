"""Tests for the WebCapsule command-line interface."""

import json
from pathlib import Path

from typer.testing import CliRunner

from webcapsule.cli import app

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
