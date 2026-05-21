"""
screenshot.py - Capture a full-page PNG screenshot of a URL.

Playwright renders the page in a headless Chromium browser, scrolls to
trigger lazy-loaded images, then takes a full-page screenshot.

The resulting PNG is human-inspectable and needs no special software to open.
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

# Viewport width in pixels. 1280px covers most desktop layouts without
# triggering mobile breakpoints that might hide content.
_VIEWPORT_WIDTH = 1280
_VIEWPORT_HEIGHT = 900

# A realistic User-Agent (same as fetcher.py - keep them in sync if changing).
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def capture(url: str, output_path: Path) -> Path:
    """Take a full-page screenshot of *url* and save it to *output_path*.

    Args:
        url:         The page to screenshot.
        output_path: Destination file (will be created or overwritten).
                     Should have a ``.png`` extension.

    Returns:
        The resolved path of the saved screenshot.

    Raises:
        RuntimeError: If Playwright cannot load or screenshot the page.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=_USER_AGENT,
            viewport={"width": _VIEWPORT_WIDTH, "height": _VIEWPORT_HEIGHT},
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=30_000)

            # Scroll slowly to the bottom so lazy-loaded images reveal themselves.
            _scroll_to_bottom(page)

            page.screenshot(path=str(output_path), full_page=True)
        finally:
            browser.close()

    return output_path.resolve()


def _scroll_to_bottom(page) -> None:
    """Scroll the page incrementally to trigger lazy-load placeholders."""
    page.evaluate("""
        () => new Promise(resolve => {
            let total = 0;
            const step = 400;
            const interval = setInterval(() => {
                window.scrollBy(0, step);
                total += step;
                if (total >= document.body.scrollHeight) {
                    clearInterval(interval);
                    window.scrollTo(0, 0);
                    resolve();
                }
            }, 50);
        })
    """)
