# Contributing to WebCapsule

First off — thank you. Seriously.

WebCapsule is a small project with a focused goal: make web archiving simple, durable, and human-friendly. If you're here, you probably care about at least one of those things.

---

## The one rule

> **Don't sacrifice simplicity.**

Every feature, every abstraction, every dependency added to this project must clear that bar. If a change makes WebCapsule harder to understand, harder to install, or harder to use — it's probably not the right change, no matter how clever it is.

---

## How to contribute

### Found a bug?

Open an issue. Include:
- What you ran (the exact command)
- What you expected
- What actually happened
- Your OS and Python version

### Have a feature idea?

Open an issue first and describe the use case. We'll talk about it before anyone writes code. This saves everyone time.

### Want to write code?

1. Fork the repo and create a branch (`git checkout -b my-feature`)
2. Make your changes
3. Run the tests (`pytest`)
4. Run the linter (`ruff check .`)
5. Open a pull request with a clear description of what changed and why

---

## Setting up a dev environment

```bash
git clone https://github.com/your-org/webcapsule.git
cd webcapsule

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install the headless browser (one-time)
playwright install chromium
```

---

## Project structure

```
webcapsule/
  __init__.py       — package metadata
  fetcher.py        — retrieve HTML from URLs
  parser.py         — extract readable content
  markdown_gen.py   — convert to Markdown
  metadata.py       — extract structured metadata
  screenshot.py     — take full-page screenshots
  archive.py        — write capsule folders
  search.py         — SQLite FTS5 index
  cli.py            — Typer command-line interface

tests/
  test_fetcher.py
  test_parser.py
  ...
```

Each module does one thing. If you're touching more than two modules for a single feature, it might be worth pausing and checking the design.

---

## Code style

- Format with [ruff](https://docs.astral.sh/ruff/) (`ruff format .`)
- Lint with ruff (`ruff check .`)
- Type hints on all public functions
- Comments only when the **why** is non-obvious — never explain *what* the code does

---

## Commit messages

Use the conventional commits style:

```
feat: add --pdf flag for PDF snapshot
fix: handle missing og:title gracefully
docs: update README install section
refactor: extract _slug helper from archive.py
```

---

## What we probably won't accept

- Dependencies that require an account or external service
- Features that only make sense with cloud infrastructure
- Anything that makes the archive less readable without the app
- Abstraction for its own sake

If you're unsure, open an issue and ask. We'd rather have the conversation early.

---

## License

By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers this project.
