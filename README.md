# WebCapsule - Local-first web archiver

> **Save web pages as Markdown, HTML, screenshots, metadata, and searchable local archives.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status: MVP](https://img.shields.io/badge/status-MVP-orange)]()

---

WebCapsule is a **local-first web archiving CLI** for researchers, writers, journalists,
students, and digital preservation workflows. It turns any URL into a durable,
offline-readable folder with clean Markdown, original HTML, metadata, a full-page
screenshot, checksums, and SQLite full-text search.

Use it when bookmarks are not enough: archive articles, preserve web pages, save online
research, build a personal knowledge base, or keep link rot from destroying your notes.
Everything stays on your own machine. No cloud. No account. No lock-in.

If WebCapsule disappears tomorrow, your archive stays readable forever.

**Keywords:** web archiver, local web archive, offline web archive, save web pages as
Markdown, website screenshot CLI, personal archive, digital preservation, link rot,
Python archiving tool, searchable article archive.

---

## Why WebCapsule?

| Bookmarks | WebCapsule |
|-----------|-----------|
| Save *where* something was | Save *what* it said |
| Break when links die | Survive forever on your disk |
| Need the original site | Need nothing but a file explorer |
| Format changes whenever a platform wants | Markdown and JSON - always the same |

---

## What WebCapsule is good for

- Saving web pages as Markdown for Obsidian, notes, research, and long-term reading
- Preserving articles before links break, pages disappear, or platforms change
- Creating a local, searchable archive without a hosted service
- Capturing full-page screenshots plus original HTML for reference
- Keeping citation-friendly metadata such as title, author, date, source URL, and tags
- Exporting an archive in portable ZIP or TAR formats

---

## How it compares

WebCapsule is not a public crawler like the Wayback Machine and it is not a read-it-later
cloud service like Pocket or Instapaper. It is closer to a personal, local alternative to
bookmarking: one command saves the content itself in open formats.

If you need a self-hosted web archiving server, tools such as ArchiveBox may be a better
fit. If you want a small Python CLI that produces human-readable Markdown folders you can
keep forever, WebCapsule is built for that.

---

## What's inside a capsule?

```
archives/
  climate/
    2026-05-20-the-great-barrier-reef-article/
      README.md         <- open this first - human-friendly summary
      content.md        <- full article in clean Markdown
      original.html     <- exact HTML snapshot
      screenshot.png    <- full-page screenshot
      metadata.json     <- structured metadata (title, author, date...)
      checksum.sha256   <- file integrity hashes
```

Every file is readable without WebCapsule. Open `content.md` in any text editor. Done.

---

## Installation

From a local checkout:

```bash
pip install -e ".[dev]"
playwright install chromium   # one-time browser download (~150 MB)
```

After a PyPI release, regular users will be able to install with `pip install webcapsule`.

---

## Usage

### Save a page

```bash
webcapsule save https://example.com/article
```

With options:

```bash
# Assign to a collection and add tags
webcapsule save https://example.com/article --collection climate --tag science --tag ocean

# Force headless browser rendering (for JavaScript-heavy sites)
webcapsule save https://example.com/spa --browser

# Skip screenshot (faster)
webcapsule save https://example.com/article --no-screenshot

# Check what would be archived without writing files
webcapsule save https://example.com/article --dry-run

# Save the same URL again even if it was archived recently
webcapsule save https://example.com/article --force
```

By default, WebCapsule skips re-saving the same URL if it was archived in the last 24 hours.

### Search your archive

```bash
webcapsule search "climate change"
webcapsule search "title:python"        # column-filtered search
webcapsule search "ocean AND reef"      # boolean operators
```

### List all saved capsules

```bash
webcapsule list
webcapsule list --limit 10
```

### Open a capsule

```bash
webcapsule open ~/webcapsule/general/2026-05-20-example-article
```

If the path is a capsule folder, WebCapsule opens its `README.md`.

### Export your archive

```bash
webcapsule export ~/backups/my-archive.zip
webcapsule export ~/backups/my-archive --format tar
```

### Rebuild the search index

```bash
webcapsule rebuild-index
```

---

## Archive location

By default, capsules are saved to `~/webcapsule/`.

Change it with an environment variable:

```bash
export WEBCAPSULE_ARCHIVE=/mnt/external-drive/my-archive
```

---

## Design principles

1. **Local-first** - everything stays on your machine
2. **Offline-first** - works without any internet after saving
3. **Open formats** - Markdown, JSON, HTML, PNG - readable anywhere
4. **No vendor lock-in** - no accounts, no subscriptions, no APIs
5. **Human-readable** - a non-technical person can open and understand the archive
6. **AI optional** - never required, never forced
7. **Useful even if abandoned** - the archive outlives the tool

---

## Architecture

WebCapsule is intentionally modular. Each concern lives in its own file:

| Module | Responsibility |
|--------|---------------|
| `fetcher.py` | Retrieve HTML (httpx fast path, Playwright fallback) |
| `parser.py` | Extract readable content (readability-lxml + BeautifulSoup) |
| `markdown_gen.py` | Convert parsed HTML to Markdown |
| `metadata.py` | Scrape OpenGraph, JSON-LD, and meta tags |
| `screenshot.py` | Full-page PNG via Playwright |
| `archive.py` | Write the capsule folder and compute checksums |
| `search.py` | SQLite FTS5 local search index, including body text |
| `cli.py` | Typer-powered command-line interface |

---

## Tech stack

- **Python 3.11+**
- [Playwright](https://playwright.dev/python/) - headless browser for JS-heavy pages and screenshots
- [readability-lxml](https://github.com/buriy/python-readability) - article extraction (same algorithm as Firefox Reader View)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing fallback and metadata scraping
- [markdownify](https://github.com/matthewwithanm/python-markdownify) - HTML to Markdown conversion
- [httpx](https://www.python-httpx.org/) - fast HTTP client
- [Typer](https://typer.tiangolo.com/) + [Rich](https://rich.readthedocs.io/) - CLI and pretty output
- **SQLite FTS5** - local full-text search (no external search server)

---

## Ethical use

WebCapsule is built for:

- Personal research and note-taking
- Journalism and fact-checking
- Education and study
- Cultural preservation
- Digital memory

It is **not** designed to bypass paywalls, violate `robots.txt`, or enable mass scraping. Archive responsibly.

---

## More resources

- [Web archiving use cases](docs/web-archiving-use-cases.md)
- [Discoverability checklist](docs/discoverability-checklist.md)

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the full plan.

Short version:

- [x] MVP CLI (save, search, list, export)
- [x] Full-page screenshots
- [x] SQLite full-text search
- [x] Full-body text indexing
- [x] Checksum integrity
- [x] Recent-URL deduplication
- [ ] Browser extension
- [ ] Obsidian vault export
- [ ] Wayback Machine integration
- [ ] WARC support
- [ ] Local web UI
- [ ] Citation generation (APA, MLA, Chicago)
- [ ] Archive deduplication

---

## Contributing

Contributions are welcome - see [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

The single guiding rule: **don't sacrifice simplicity**.

---

## License

MIT - see [LICENSE](LICENSE).
