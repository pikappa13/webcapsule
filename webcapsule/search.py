"""
search.py - Local full-text search using SQLite FTS5.

SQLite is used ONLY as a search index - it is never the primary store.
All actual content lives on the filesystem as plain files.
If the index is deleted, it can be rebuilt from the capsule directories.

The FTS5 virtual table supports:
  - phrase queries:   "climate change"
  - prefix queries:   clim*
  - boolean:          climate AND change
  - column filters:   title:python
"""

import json
import sqlite3
from pathlib import Path
from typing import Any

# Index lives next to the archive root so it travels with the archive.
_INDEX_FILENAME = "webcapsule.db"


def _connect(archive_root: Path) -> sqlite3.Connection:
    """Open (or create) the SQLite index at *archive_root*."""
    db_path = archive_root / _INDEX_FILENAME
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    _ensure_schema(con)
    return con


def _ensure_schema(con: sqlite3.Connection) -> None:
    """Create the FTS5 table and metadata store if they don't exist yet."""
    con.executescript("""
        CREATE TABLE IF NOT EXISTS capsules (
            id          INTEGER PRIMARY KEY,
            path        TEXT NOT NULL UNIQUE,
            url         TEXT NOT NULL,
            title       TEXT,
            author      TEXT,
            description TEXT,
            body        TEXT,
            tags        TEXT,
            archived    TEXT,
            word_count  INTEGER
        );

        -- FTS5 virtual table - indexes title, description, body text, and tags.
        CREATE VIRTUAL TABLE IF NOT EXISTS capsules_fts USING fts5(
            title,
            description,
            body,
            tags,
            content='capsules',
            content_rowid='id',
            tokenize='porter unicode61'
        );

        -- Triggers keep the FTS index in sync with the base table.
        CREATE TRIGGER IF NOT EXISTS capsules_ai AFTER INSERT ON capsules BEGIN
            INSERT INTO capsules_fts(rowid, title, description, body, tags)
            VALUES (new.id, new.title, new.description, new.body, new.tags);
        END;

        CREATE TRIGGER IF NOT EXISTS capsules_ad AFTER DELETE ON capsules BEGIN
            INSERT INTO capsules_fts(capsules_fts, rowid, title, description, body, tags)
            VALUES ('delete', old.id, old.title, old.description, old.body, old.tags);
        END;

        CREATE TRIGGER IF NOT EXISTS capsules_au AFTER UPDATE ON capsules BEGIN
            INSERT INTO capsules_fts(capsules_fts, rowid, title, description, body, tags)
            VALUES ('delete', old.id, old.title, old.description, old.body, old.tags);
            INSERT INTO capsules_fts(rowid, title, description, body, tags)
            VALUES (new.id, new.title, new.description, new.body, new.tags);
        END;
    """)
    con.commit()


def _read_body(capsule_dir: Path) -> str:
    """Read the plain-text body from content.md, stripping the YAML front matter."""
    content_file = capsule_dir / "content.md"
    if not content_file.exists():
        return ""
    text = content_file.read_text(encoding="utf-8", errors="ignore")
    # Strip YAML front matter (--- ... ---) if present.
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]
    return text.strip()


def index_capsule(archive_root: Path, capsule_dir: Path, metadata: dict[str, Any]) -> None:
    """Add or update a capsule entry in the search index.

    Args:
        archive_root: Root directory (where the DB lives).
        capsule_dir:  Path to the capsule folder being indexed.
        metadata:     Dict from :mod:`webcapsule.metadata`.
    """
    tags_str = " ".join(metadata.get("tags") or [])
    path_str = str(capsule_dir.resolve())
    body = _read_body(capsule_dir)

    con = _connect(archive_root)
    try:
        # ON CONFLICT DO UPDATE does not fire the AFTER UPDATE trigger in SQLite,
        # so we explicitly delete + reinsert to keep the FTS5 index in sync.
        existing = con.execute("SELECT id FROM capsules WHERE path = ?", (path_str,)).fetchone()

        if existing:
            con.execute("DELETE FROM capsules WHERE path = ?", (path_str,))

        con.execute(
            """
            INSERT INTO capsules (path, url, title, author, description, body, tags, archived, word_count)
            VALUES (:path, :url, :title, :author, :description, :body, :tags, :archived, :word_count)
        """,
            {
                "path": path_str,
                "url": metadata.get("source_url", ""),
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "description": metadata.get("description", ""),
                "body": body,
                "tags": tags_str,
                "archived": metadata.get("archived_date", ""),
                "word_count": metadata.get("word_count", 0),
            },
        )
        con.commit()
    finally:
        con.close()


def search(archive_root: Path, query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Full-text search across all indexed capsules.

    Args:
        archive_root: Root directory (where the DB lives).
        query:        FTS5 query string.
        limit:        Maximum number of results to return.

    Returns:
        List of result dicts with keys: title, url, path, archived, snippet.
    """
    con = _connect(archive_root)
    try:
        rows = con.execute(
            """
            SELECT
                c.title,
                c.url,
                c.path,
                c.archived,
                snippet(capsules_fts, 1, '[', ']', '...', 12) AS snippet
            FROM capsules_fts
            JOIN capsules c ON capsules_fts.rowid = c.id
            WHERE capsules_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """,
            (query, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()


def list_all(archive_root: Path, limit: int = 100) -> list[dict[str, Any]]:
    """Return all indexed capsules, newest first.

    Args:
        archive_root: Root directory.
        limit:        Maximum entries to return.

    Returns:
        List of dicts with capsule metadata.
    """
    con = _connect(archive_root)
    try:
        rows = con.execute(
            """
            SELECT title, url, path, author, archived, word_count, tags
            FROM capsules
            ORDER BY archived DESC
            LIMIT ?
        """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()


def rebuild_index(archive_root: Path) -> int:
    """Rebuild the index by scanning all capsule metadata.json files.

    Useful after manual edits or if the DB is deleted.

    Returns:
        Number of capsules indexed.
    """
    count = 0
    for meta_file in sorted(archive_root.rglob("metadata.json")):
        capsule_dir = meta_file.parent
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            index_capsule(archive_root, capsule_dir, meta)
            count += 1
        except Exception:
            # Skip corrupted capsules rather than aborting the whole rebuild.
            continue
    return count
