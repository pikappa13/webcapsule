# Web archiving use cases

WebCapsule is a local-first web archiver for people who need durable, searchable copies
of web pages. It is designed for personal research, journalism, digital preservation,
note-taking, education, and knowledge management.

## Save web pages as Markdown

WebCapsule converts article content into clean Markdown while also keeping the original
HTML snapshot. This makes it useful for Obsidian vaults, Markdown note systems, static
archives, research folders, and long-term reading workflows.

Common searches this project is meant to answer:

- save web pages as Markdown
- archive article to Markdown
- local-first web archiver
- offline web archive CLI
- personal web archive tool
- Python web archiving tool

## Preserve pages before link rot

Bookmarks only remember where a page used to be. WebCapsule stores what the page said:
the readable article, source URL, metadata, screenshot, and checksums. The archive stays
readable even if the original website disappears, changes its layout, or blocks old links.

## Build a searchable local knowledge archive

Each saved capsule can be indexed with SQLite full-text search. This lets you search
titles, descriptions, tags, and article body text without sending your archive to a cloud
service.

## Keep open, portable files

A WebCapsule archive is just folders and files:

- `content.md` for clean Markdown
- `original.html` for the raw source page
- `screenshot.png` for visual reference
- `metadata.json` for title, author, source URL, dates, tags, and word count
- `checksum.sha256` for integrity checks

No proprietary database is required to read the saved content.

## When to use another tool

Use the Internet Archive or Wayback Machine when you need public web preservation.
Use a self-hosted web archiving server when you need multi-user workflows, scheduled
crawls, or a browser-based archive dashboard.

Use WebCapsule when you want a small command-line tool that saves web pages locally in
open formats you can keep, search, back up, and read forever.
