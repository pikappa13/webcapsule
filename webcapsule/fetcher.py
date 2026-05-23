"""
fetcher.py - Retrieve raw HTML from a URL.

Tries a lightweight httpx request first.
Falls back to Playwright for JavaScript-heavy pages that need a real browser.
"""

import httpx
from playwright.sync_api import sync_playwright

# A realistic User-Agent so servers don't serve degraded pages.
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Pages longer than this hint are probably fully server-rendered;
# use the fast path without spinning up a browser.
_MIN_CONTENT_LENGTH = 500


def fetch(url: str, force_browser: bool = False) -> str:
    """Return the full HTML of *url* as a string.

    Args:
        url: The target page URL.
        force_browser: Skip the fast path and always use Playwright.

    Returns:
        Raw HTML string.

    Raises:
        RuntimeError: If neither strategy succeeds.
    """
    if not force_browser:
        html = _fetch_simple(url)
        if html and len(html) >= _MIN_CONTENT_LENGTH:
            return html

    # The page is likely JavaScript-rendered - use a real browser.
    try:
        return _fetch_browser(url)
    except Exception as exc:
        raise RuntimeError(
            f"Could not fetch {url}. The HTTP response was missing or too short, "
            "and the browser fallback failed."
        ) from exc


def _fetch_simple(url: str) -> str | None:
    """Fast path: plain HTTP request via httpx."""
    try:
        headers = {"User-Agent": _USER_AGENT}
        response = httpx.get(url, headers=headers, follow_redirects=True, timeout=20)
        response.raise_for_status()
        return response.text
    except Exception:
        return None


def _fetch_browser(url: str) -> str:
    """Slow path: headless Chromium via Playwright."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(user_agent=_USER_AGENT)

        # Wait until network is mostly idle so dynamic content has loaded.
        page.goto(url, wait_until="networkidle", timeout=30_000)
        html = page.content()

        browser.close()
        return html
