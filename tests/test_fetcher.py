"""Tests for webcapsule.fetcher (HTTP path only - no browser spawned)."""

from unittest.mock import MagicMock, patch

from webcapsule import fetcher

FULL_HTML = "<html><body>" + "x" * 600 + "</body></html>"
SHORT_HTML = "<html><body>tiny</body></html>"


def _mock_response(text: str, status: int = 200):
    resp = MagicMock()
    resp.text = text
    resp.raise_for_status = MagicMock()
    if status >= 400:
        import httpx

        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=MagicMock()
        )
    return resp


def test_fetch_simple_returns_html():
    with patch("webcapsule.fetcher.httpx.get", return_value=_mock_response(FULL_HTML)):
        result = fetcher.fetch("https://example.com/article")
    assert result == FULL_HTML


def test_fetch_falls_back_to_browser_when_response_too_short():
    with (
        patch("webcapsule.fetcher.httpx.get", return_value=_mock_response(SHORT_HTML)),
        patch("webcapsule.fetcher._fetch_browser", return_value=FULL_HTML) as mock_browser,
    ):
        result = fetcher.fetch("https://example.com/spa")
    mock_browser.assert_called_once()
    assert result == FULL_HTML


def test_fetch_force_browser_skips_httpx():
    with (
        patch("webcapsule.fetcher.httpx.get") as mock_get,
        patch("webcapsule.fetcher._fetch_browser", return_value=FULL_HTML),
    ):
        fetcher.fetch("https://example.com/spa", force_browser=True)
    mock_get.assert_not_called()


def test_fetch_falls_back_to_browser_when_httpx_raises():
    with (
        patch("webcapsule.fetcher.httpx.get", side_effect=Exception("timeout")),
        patch("webcapsule.fetcher._fetch_browser", return_value=FULL_HTML) as mock_browser,
    ):
        result = fetcher.fetch("https://example.com/article")
    mock_browser.assert_called_once()
    assert result == FULL_HTML
