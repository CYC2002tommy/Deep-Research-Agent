"""
Tests for skills/deep-science-writer/scripts/verify_urls.py

Covers:
- Verify URL with HTTP 200 (alive)
- Verify URL with HTTP 403 (restricted)
- Verify URL with connection failure
- Verify DOI via Crossref (alive)
- Test timeout parameter is passed through
"""
import json
import sys
from unittest.mock import patch, MagicMock
import pytest

# Ensure the script module is importable
sys.path.insert(0, "skills/deep-science-writer/scripts")
import verify_urls


class MockResponse:
    """Minimal mock requests.Response substitute."""
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


def test_verify_alive():
    """A URL returning < 400 should be marked 'Verified Alive'."""
    queries = ["test query"]
    with patch("verify_urls.DDGS") as mock_ddgs_cls, \
         patch("verify_urls.requests.get") as mock_get:
        # Mock DuckDuckGo to return one result
        mock_ddgs = MagicMock()
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
        mock_ddgs.text.return_value = [
            {"href": "https://example.com/paper", "title": "Test Paper"}
        ]
        # Mock requests.get to return 200
        mock_get.return_value = MockResponse(200)

        results = verify_urls.verify_urls(queries)

    assert len(results) == 1
    assert results[0]["status"] == "Verified Alive"
    assert results[0]["url"] == "https://example.com/paper"


def test_verify_403():
    """A URL returning 403 should be marked 'exists_restricted'."""
    queries = ["restricted query"]
    with patch("verify_urls.DDGS") as mock_ddgs_cls, \
         patch("verify_urls.requests.get") as mock_get:
        mock_ddgs = MagicMock()
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
        mock_ddgs.text.return_value = [
            {"href": "https://example.com/blocked", "title": "Blocked"}
        ]
        mock_get.return_value = MockResponse(403)

        results = verify_urls.verify_urls(queries)

    assert len(results) == 1
    assert results[0]["status"] == "exists_restricted"


def test_verify_failed():
    """A URL that raises an exception should be skipped; query with no valid
    results returns empty list."""
    queries = ["failing query"]
    with patch("verify_urls.DDGS") as mock_ddgs_cls, \
         patch("verify_urls.requests.get") as mock_get:
        mock_ddgs = MagicMock()
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
        mock_ddgs.text.return_value = [
            {"href": "https://example.com/broken", "title": "Broken"}
        ]
        mock_get.side_effect = ConnectionError("DNS failure")

        results = verify_urls.verify_urls(queries)

    # No result collected because no status was Verified Alive or exists_restricted
    assert len(results) == 0


def test_verify_doi_alive():
    """Crossref DOI resolution returning 200 should be 'Verified Alive'."""
    doi = "10.1000/xyz123"
    with patch("verify_urls.requests.get") as mock_get:
        mock_get.return_value = MockResponse(
            200,
            {"message": {"title": ["My Research Paper"]}}
        )
        result = verify_urls.verify_doi(doi)

    assert result["status"] == "Verified Alive"
    assert result["doi"] == doi
    assert "My Research Paper" in result["title"]


def test_verify_doi_failed():
    """Crossref DOI resolution raising an exception returns status 'Failed'."""
    doi = "10.1000/bad-doi"
    with patch("verify_urls.requests.get") as mock_get:
        mock_get.side_effect = ConnectionError("Timeout")
        result = verify_urls.verify_doi(doi)

    assert result["status"] == "Failed"


def test_custom_timeout():
    """The timeout parameter should be passed through to requests.get."""
    queries = ["timeout test"]
    with patch("verify_urls.DDGS") as mock_ddgs_cls, \
         patch("verify_urls.requests.get") as mock_get:
        mock_ddgs = MagicMock()
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
        mock_ddgs.text.return_value = [
            {"href": "https://example.com/test", "title": "Test"}
        ]
        mock_get.return_value = MockResponse(200)

        verify_urls.verify_urls(queries, timeout=20)

        # Verify requests.get was called with the custom timeout
        _, kwargs = mock_get.call_args
        assert kwargs.get("timeout") == 20


def test_ydc_backend_used_when_key_set(monkeypatch):
    """With YDC_API_KEY set, _search should call the You.com API and
    normalize its results into the same shape as DDGS."""
    monkeypatch.setenv("YDC_API_KEY", "test-key")

    ydc_response = MockResponse(
        200,
        {"hits": [
            {"url": "https://example.com/ydc", "title": "YDC Paper",
             "description": "A paper found via You.com"}
        ]},
    )
    with patch("verify_urls.DDGS") as mock_ddgs_cls, \
         patch("verify_urls.requests.get") as mock_get:
        mock_ddgs_cls.return_value.__enter__.return_value = MagicMock()
        # First requests.get call is the You.com search; second is the liveness check.
        mock_get.side_effect = [ydc_response, MockResponse(200)]

        results = verify_urls.verify_urls(["ydc query"])

    assert len(results) == 1
    assert results[0]["url"] == "https://example.com/ydc"
    assert results[0]["status"] == "Verified Alive"
    # The DuckDuckGo backend must not have been used.
    mock_ddgs_cls.return_value.__enter__.return_value.text.assert_not_called()


def test_ydc_backend_falls_back_on_error(monkeypatch):
    """A failing You.com request should warn and fall back to DuckDuckGo
    for that query instead of dropping it."""
    monkeypatch.setenv("YDC_API_KEY", "test-key")

    ddgs = MagicMock()
    ddgs.text.return_value = [
        {"href": "https://example.com/fallback", "title": "Fallback"}
    ]
    with patch("verify_urls.DDGS") as mock_ddgs_cls, \
         patch("verify_urls.requests.get") as mock_get:
        mock_ddgs_cls.return_value.__enter__.return_value = ddgs
        # First requests.get call (You.com search) raises; second (liveness) returns 200.
        mock_get.side_effect = [ConnectionError("YDC down"), MockResponse(200)]

        results = verify_urls.verify_urls(["fallback query"])

    assert len(results) == 1
    assert results[0]["url"] == "https://example.com/fallback"
    assert results[0]["status"] == "Verified Alive"
    ddgs.text.assert_called_once()


def test_ydc_search_no_key_raises():
    """_ydc_search must raise when YDC_API_KEY is unset (internal guard)."""
    import os
    saved = os.environ.pop("YDC_API_KEY", None)
    try:
        with pytest.raises(RuntimeError):
            verify_urls._ydc_search("q", 3, 10)
    finally:
        if saved is not None:
            os.environ["YDC_API_KEY"] = saved


def test_ydc_backend_skipped_when_key_unset():
    """Without YDC_API_KEY, _search must use DuckDuckGo directly (default
    behavior unchanged)."""
    import os
    saved = os.environ.pop("YDC_API_KEY", None)
    try:
        ddgs = MagicMock()
        ddgs.text.return_value = [
            {"href": "https://example.com/ddg", "title": "DDG Paper"}
        ]
        with patch("verify_urls.DDGS") as mock_ddgs_cls, \
             patch("verify_urls.requests.get") as mock_get:
            mock_ddgs_cls.return_value.__enter__.return_value = ddgs
            mock_get.return_value = MockResponse(200)

            results = verify_urls.verify_urls(["ddg query"])

        assert len(results) == 1
        assert results[0]["url"] == "https://example.com/ddg"
        # Only the liveness-check call was made against requests.get;
        # no You.com search call happened first.
        assert mock_get.call_count == 1
    finally:
        if saved is not None:
            os.environ["YDC_API_KEY"] = saved
