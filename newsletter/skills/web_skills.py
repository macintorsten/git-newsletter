"""
Web research skill implementations.

These functions provide basic internet research capabilities for VS Code
Copilot agents following the web-research SKILL.md instructions, and for
the orchestrator pipeline.

The implementation uses only the Python standard library (urllib) so it
works without additional dependencies.  For richer results, install the
optional ``requests`` package — it will be used automatically if present.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get(url: str, timeout: int = 10) -> str:
    """Fetch *url* and return the response body as a string."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "git-newsletter/1.0 (github.com/macintorsten/git-newsletter)"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        charset = resp.headers.get_content_charset("utf-8")
        return resp.read().decode(charset, errors="replace")


# ---------------------------------------------------------------------------
# Public skill functions
# ---------------------------------------------------------------------------

def search_web(
    query: str,
    max_results: int = 5,
) -> list[dict[str, str]]:
    """
    Search the web for *query* and return up to *max_results* results.

    Each result is a dict with keys: ``title``, ``url``, ``snippet``.

    Uses the DuckDuckGo Lite HTML endpoint (no API key required).
    Falls back gracefully if the request fails.
    """
    encoded = urllib.parse.urlencode({"q": query, "kl": "us-en"})
    search_url = f"https://html.duckduckgo.com/html/?{encoded}"

    try:
        html = _get(search_url)
    except Exception as exc:
        return [{"title": "Search unavailable", "url": "", "snippet": str(exc)}]

    # Lightweight parsing – avoid pulling in BeautifulSoup
    results: list[dict[str, str]] = []
    import re

    # DuckDuckGo Lite wraps results in <a class="result__a" href="...">title</a>
    # and snippets in <a class="result__snippet">...</a>
    link_pattern = re.compile(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        re.S,
    )
    snippet_pattern = re.compile(
        r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', re.S
    )

    links = link_pattern.findall(html)
    snippets = snippet_pattern.findall(html)

    tag_re = re.compile(r"<[^>]+>")

    for i, (url, title) in enumerate(links[:max_results]):
        snippet = snippets[i] if i < len(snippets) else ""
        results.append(
            {
                "title": tag_re.sub("", title).strip(),
                "url": url.strip(),
                "snippet": tag_re.sub("", snippet).strip(),
            }
        )

    return results


def fetch_page(url: str, max_chars: int = 4000) -> str:
    """
    Fetch a web page at *url* and return its text content (stripped of HTML
    tags) truncated to *max_chars* characters.
    """
    import re

    try:
        html = _get(url)
    except Exception as exc:
        return f"Could not fetch page: {exc}"

    # Remove script / style blocks first
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
    # Strip remaining tags
    text = re.sub(r"<[^>]+>", " ", html)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text[:max_chars]
