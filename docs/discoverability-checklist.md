# Discoverability checklist

Use this checklist when publishing or updating WebCapsule on GitHub, PyPI, and search
engines. These fields are outside the Python package itself, so they need to be set in
the hosting platform.

## GitHub repository settings

Recommended repository description:

> Local-first web archiver that saves pages as Markdown, HTML, screenshots, metadata, and searchable offline archives.

Recommended website / homepage:

> https://github.com/pikappa13/webcapsule#readme

Recommended GitHub topics:

- web-archiver
- web-archive
- local-first
- offline-first
- markdown
- digital-preservation
- link-rot
- personal-archive
- knowledge-base
- html-to-markdown
- screenshot
- sqlite-fts5
- python
- cli

## PyPI publishing

Before publishing:

```bash
python -m build
python -m twine check dist/*
```

The package metadata in `pyproject.toml` is written to target searches such as:

- web archiver python
- local-first web archive
- save web pages as markdown
- offline web archive CLI
- personal archive tool
- link rot preservation

## Search positioning

The project name `WebCapsule` is already used by other web projects, so discovery should
lead with the specific category:

- local-first web archiver
- save web pages as Markdown
- searchable offline web archive
- Python web archiving CLI

Use these phrases in release notes, GitHub discussions, posts, and package descriptions.
