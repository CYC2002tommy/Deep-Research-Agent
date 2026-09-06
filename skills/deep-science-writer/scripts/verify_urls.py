"""
URL/Evidence Verification Script for Phase 4.5.
Requires: pip install duckduckgo_search requests

Usage: Modify the 'queries' list, then run this script to fetch real URLs and verify their liveness (HTTP Status).
Note for Windows MSYS bash: Always enclose the script path in double quotes when executing via an absolute python path to prevent backslash stripping.

DOI Resolution Strategy:
1. Preferred: CrossRef API (https://api.crossref.org/works/{doi}) — direct, fast, no rate limits for moderate usage.
2. Fallback: DuckDuckGo search — used when the DOI cannot be resolved via Crossref (e.g., non-DOI queries).

Search Backend (optional):
By default, queries run through DuckDuckGo (duckduckgo_search). Set the YDC_API_KEY
environment variable to switch the search backend to the You.com Search API
(https://api.you.com) — the key is available at https://you.com/platform/api-keys.
If YDC_API_KEY is set but a You.com request fails (timeout, HTTP error, malformed
response), the script warns on stderr and falls back to DuckDuckGo for that query.
No dependency or behavior changes occur when YDC_API_KEY is unset.
"""
import os

import requests
from duckduckgo_search import DDGS
import json
import sys

# Default timeout for HTTP requests (seconds).
# Redirect chains may take longer than a simple HEAD request, so we allow
# generous headroom. Pass `timeout=N` to verify_urls() to override.
DEFAULT_TIMEOUT = 10

# You.com Search API (only used when YDC_API_KEY is set in the environment).
YDC_SEARCH_URL = "https://api.you.com/api/search"


def _ydc_search(query: str, max_results: int, timeout: int):
    """Run a text search through the You.com Search API.

    Requires YDC_API_KEY in the environment. Returns a list of results in the
    same shape as duckduckgo_search's `.text()` output: dicts with 'href',
    'title', and 'body' keys. Raises on request failure, non-200 responses,
    or malformed payloads so callers can fall back.
    """
    api_key = os.environ.get("YDC_API_KEY", "")
    if not api_key:
        raise RuntimeError("YDC_API_KEY is not set")
    resp = requests.get(
        YDC_SEARCH_URL,
        params={"q": query},
        headers={"X-API-KEY": api_key, "User-Agent": "Mozilla/5.0"},
        timeout=timeout,
    )
    if resp.status_code != 200:
        resp.raise_for_status()
    hits = (resp.json() or {}).get("hits", [])
    results = []
    for hit in hits[:max_results]:
        # 'thumbnail_url' is the source page URL in You.com web search results.
        url = hit.get("url") or hit.get("thumbnail_url")
        if not url:
            continue
        results.append({
            "href": url,
            "title": hit.get("title") or "",
            "body": hit.get("description") or "",
        })
    return results


def _search(query: str, max_results: int, timeout: int):
    """Dispatch a text search to You.com when YDC_API_KEY is set, else DuckDuckGo.

    A failing You.com request warns on stderr and falls back to DuckDuckGo for
    that query, so a keyless or degraded You.com path never breaks verification.
    """
    if os.environ.get("YDC_API_KEY"):
        try:
            return _ydc_search(query, max_results, timeout)
        except Exception as e:
            print(
                f"[WARN] verify_urls: You.com search for '{query}' failed "
                f"({e}); falling back to DuckDuckGo.",
                file=sys.stderr,
            )
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))


def verify_doi(doi: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Resolve a DOI via the Crossref API.
    Returns a dict with keys: 'doi', 'title', 'url', 'status'.
    Status is 'Verified Alive' on success (HTTP 200), else the HTTP status code string.
    This is the *preferred* method for DOI validation — it is direct, authoritative,
    and does not count toward DuckDuckGo rate limits.
    """
    url = f"https://api.crossref.org/works/{doi}"
    try:
        resp = requests.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            data = resp.json()
            title = (data.get('message', {}).get('title') or ['Unknown'])[0]
            doi_url = f"https://doi.org/{doi}"
            return {'doi': doi, 'title': title, 'url': doi_url, 'status': 'Verified Alive'}
        else:
            return {'doi': doi, 'title': 'Unknown', 'url': f"https://doi.org/{doi}", 'status': str(resp.status_code)}
    except Exception as e:
        print(f"[WARN] verify_urls: Crossref DOI resolution for '{doi}' failed: {e}", file=sys.stderr)
        return {'doi': doi, 'title': 'Unknown', 'url': f"https://doi.org/{doi}", 'status': 'Failed'}


def verify_urls(queries, timeout: int = DEFAULT_TIMEOUT):
    """
    For each query string, attempt to find a live URL via DuckDuckGo search,
    then verify HTTP liveness.
    
    Parameters:
        queries: list of search query strings.
        timeout: HTTP request timeout in seconds (default 10).
                 Increase if dealing with slow redirect chains.
    """
    results = []
    for q in queries:
        try:
            # Fetch top 2-3 results to find at least one working link
            for r in _search(q, max_results=3, timeout=timeout):
                url = r['href']
                title = r['title']
                try:
                    res = requests.get(
                        url, timeout=timeout,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    status_code = res.status_code
                    if status_code < 400:
                        status = 'Verified Alive'
                    elif status_code == 403:
                        status = 'exists_restricted'
                    else:
                        status = str(status_code)
                except Exception as e:
                    print(f"[WARN] verify_urls: HTTP check for '{url}' failed: {e}", file=sys.stderr)
                    status = 'Failed'

                # 403 often means Cloudflare block but the link itself exists
                if status in ('Verified Alive', 'exists_restricted'):
                    results.append({
                        'query': q, 'title': title,
                        'url': url, 'status': status
                    })
                    break  # Found a valid link, move to next query
        except Exception as e:
            print(f"[WARN] verify_urls: query '{q}' failed: {e}", file=sys.stderr)
            continue

    print('---JSON_START---')
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print('---JSON_END---')
    return results


if __name__ == "__main__":
    # Default placeholder, easily modified by the agent before execution
    queries = [
        "Example query 1",
        "Example query 2"
    ]
    verify_urls(queries)
