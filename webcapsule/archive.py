"""
archive.py - Write a complete knowledge capsule to the filesystem.

A capsule is just a folder.  No database required to read it.
Every file inside is a plain, open format (Markdown, JSON, HTML, PNG).

Folder structure created by this module:

    <archive_root>/
      <collection>/
        <YYYY-MM-DD>-<slug>/
          README.md         - human-friendly summary (open this first)
          content.md        - full article in Markdown
          original.html     - raw HTML snapshot
          screenshot.png    - full-page screenshot
          metadata.json     - structured metadata
          checksum.sha256   - file integrity hashes
"""

import hashlib
import json
import re
import textwrap
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from webcapsule.parser import ParsedPage


def write_capsule(
    *,
    archive_root: Path,
    collection: str,
    url: str,
    raw_html: str,
    page: ParsedPage,
    markdown: str,
    metadata: dict[str, Any],
    screenshot_data: bytes | None = None,
) -> Path:
    """Write all capsule files and return the capsule directory path.

    Args:
        archive_root:    Root directory for all archives (e.g. ``~/webcapsule``).
        collection:      Logical collection name (e.g. ``"climate"``).
        url:             Source URL - used to derive the folder slug.
        raw_html:        Original HTML to preserve.
        page:            Parsed content (title used in README).
        markdown:        Generated Markdown from :mod:`webcapsule.markdown_gen`.
        metadata:        Dict from :mod:`webcapsule.metadata`.
        screenshot_data: Raw PNG bytes, or ``None`` if screenshot was skipped.

    Returns:
        Path to the newly created capsule directory.
    """
    capsule_dir = _capsule_dir(archive_root, collection, page.title, url)
    capsule_dir.mkdir(parents=True, exist_ok=True)

    # Write each file in the capsule.
    (capsule_dir / "content.md").write_text(markdown, encoding="utf-8")
    (capsule_dir / "original.html").write_text(raw_html, encoding="utf-8")
    (capsule_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if screenshot_data:
        (capsule_dir / "screenshot.png").write_bytes(screenshot_data)

    # The README is a human-friendly entry point - write it last so it can
    # reference the other files that have just been created.
    readme = _build_readme(page, metadata, capsule_dir)
    (capsule_dir / "README.md").write_text(readme, encoding="utf-8")

    # Checksums let users verify nothing was corrupted or tampered with.
    checksums = _compute_checksums(capsule_dir)
    (capsule_dir / "checksum.sha256").write_text(checksums, encoding="utf-8")

    return capsule_dir


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _capsule_dir(root: Path, collection: str, title: str, url: str) -> Path:
    """Derive a deterministic, filesystem-safe directory name."""
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    slug = _slugify(title or url)[:60]
    return root / _slugify(collection) / f"{today}-{slug}"


def _slugify(text: str) -> str:
    """Convert *text* to a lowercase, hyphen-separated filesystem slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)  # strip punctuation
    text = re.sub(r"[\s_]+", "-", text)  # spaces -> hyphens
    text = re.sub(r"-+", "-", text).strip("-")  # collapse runs
    return text or "untitled"


def _build_readme(page: ParsedPage, meta: dict[str, Any], capsule_dir: Path) -> str:
    """Generate the human-readable README.md for a capsule."""
    files = [p.name for p in sorted(capsule_dir.iterdir())]
    files_list = "\n".join(f"- `{f}`" for f in files)
    tags = ", ".join(meta.get("tags") or []) or "-"

    summary_text = meta.get("description") or ""
    if summary_text:
        summary_text = textwrap.fill(summary_text, width=80)

    return f"""\
# {meta.get("title") or page.title}

| Field        | Value |
|--------------|-------|
| **Source**   | {meta.get("source_url", "-")} |
| **Archived** | {meta.get("archived_date", "-")} |
| **Author**   | {meta.get("author") or "-"} |
| **Published**| {meta.get("published_date") or "-"} |
| **Tags**     | {tags} |
| **Words**    | {meta.get("word_count", "-")} |

## Summary

{summary_text or "_No description available._"}

## Files in this capsule

{files_list}

---
*Archived with [WebCapsule](https://github.com/webcapsule/webcapsule) - open formats, no lock-in.*
"""


def _compute_checksums(capsule_dir: Path) -> str:
    """Return SHA-256 checksums for every file in *capsule_dir* (except itself)."""
    lines: list[str] = []
    for filepath in sorted(capsule_dir.iterdir()):
        if filepath.name == "checksum.sha256":
            continue
        digest = hashlib.sha256(filepath.read_bytes()).hexdigest()
        lines.append(f"{digest}  {filepath.name}")
    return "\n".join(lines) + "\n"
