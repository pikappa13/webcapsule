# WebCapsule - Roadmap

> This document tracks what's done, what's in progress, and what's planned.
> It's a living document - priorities shift, items get added, items get dropped.
> The single constraint: **simplicity is never negotiable**.

---

## Milestone 0 - Foundation (done)

The absolute minimum needed to call this a tool, not a script.

- [x] Project structure as an installable Python package
- [x] `fetcher.py` - HTTP + Playwright dual strategy
- [x] `parser.py` - readability-lxml + BeautifulSoup fallback
- [x] `markdown_gen.py` - HTML to Markdown with YAML front matter
- [x] `metadata.py` - OpenGraph, JSON-LD, standard meta tags
- [x] `screenshot.py` - full-page PNG via Playwright
- [x] `archive.py` - capsule folder structure + SHA-256 checksums
- [x] `search.py` - SQLite FTS5 index with rebuild support
- [x] `cli.py` - `save`, `search`, `list`, `export`, `rebuild-index` via Typer + Rich
- [x] `pyproject.toml` - installable via `pip install .`
- [x] `README.md` - clear, human-first documentation
- [x] `CONTRIBUTING.md` - onboarding guide for contributors
- [x] `LICENSE` - MIT
- [x] `.gitignore`

---

## Milestone 1 - Polish & Stability

Making the MVP production-grade for real daily use.

- [x] Automated pytest suite (module coverage + CLI smoke tests)
- [x] GitHub Actions CI (lint + test on Python 3.11, 3.12, 3.13)
- [x] Pre-commit hooks (ruff, mypy)
- [x] `webcapsule rebuild-index` command to re-index from scratch
- [x] `webcapsule open PATH` command to open a capsule in the default application
- [x] Graceful error messages (network timeout, JS render failure, etc.)
- [x] `--dry-run` flag for `save` (fetch and parse without writing)
- [x] Progress indicator for exports
- [x] Capsule deduplication (skip re-saving the same URL within 24 hours)
- [ ] Publish to PyPI

---

## Milestone 2 - Smarter Archiving

Better content extraction and richer metadata.

- [ ] Automatic language detection (store in metadata)
- [ ] Reading-time estimate in capsule README
- [ ] PDF snapshot alongside PNG screenshot (`--pdf` flag)
- [ ] Dark mode screenshot option
- [ ] Configurable viewport size for screenshots
- [ ] Respect `robots.txt` by default (with `--ignore-robots` escape hatch)
- [ ] Extract all in-page links for reference (store in `links.json`)
- [ ] `webcapsule update URL` - re-fetch and diff against saved version

---

## Milestone 3 - Search & Discovery

Make it easy to find what you've saved.

- [x] Full-body text indexing
- [ ] Date-range filter: `webcapsule search "ocean" --from 2025-01 --to 2025-06`
- [ ] Collection filter: `webcapsule search "ocean" --collection climate`
- [ ] `webcapsule stats` - archive statistics (total capsules, total words, collections)
- [ ] Fuzzy search fallback when FTS5 finds nothing
- [ ] Sort results by word count or date

---

## Milestone 4 - Export & Integration

Getting your archive out into the tools you already use.

- [ ] **Obsidian export** - generate a vault-compatible folder with backlinks
- [ ] **Citation generation** - APA, MLA, Chicago format output per capsule
- [ ] **WARC support** - save/load Web ARChive format (interop with Wayback Machine)
- [ ] **Wayback Machine fallback** - if a page is already gone, try archive.org
- [ ] **Markdown book export** - compile a collection into a single readable document
- [ ] **JSON Lines export** - machine-readable stream for piping into other tools

---

## Milestone 5 - Browser Extension

The friction-free way to save pages while browsing.

- [ ] Chrome/Edge extension (Manifest V3)
- [ ] Firefox extension (Manifest V2 + V3)
- [ ] One-click save from the toolbar
- [ ] Tag and collection picker in the popup
- [ ] Native Messaging bridge to the local `webcapsule` binary

---

## Milestone 6 - Local Web UI

An optional, lightweight local interface - still no cloud, still no account.

- [ ] Read-only web UI served on `localhost` (`webcapsule serve`)
- [ ] Grid / list view of capsules
- [ ] Full-text search in the browser
- [ ] Side-by-side view: original HTML vs Markdown
- [ ] Built with a minimal stack (FastAPI + htmx or similar - no Node.js required)

---

## Never (by design)

These will never be part of WebCapsule:

- Cloud sync or cloud storage
- User accounts or authentication
- Social features (sharing, comments, likes)
- Proprietary formats
- Paywall bypassing
- AI that is required for core functionality

---

## How priorities are decided

1. Does it make the core archive more durable? -> High priority.
2. Does it reduce friction for saving? -> Medium priority.
3. Does it add complexity without clear user benefit? -> Skip it.
4. Does it require an external service? -> Only as opt-in, never required.
