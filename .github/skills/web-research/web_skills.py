"""
Web research skill implementations — CLI fallback layer.

In the **agent runtime** (VS Code Copilot, GitHub Copilot coding agent) the
built-in ``web_fetch`` tool should be used directly by the agent — no Python
code is needed.  See ``.github/skills/web-research/SKILL.md`` for the
agent-facing instructions.

This module exists purely as a **CLI fallback** so that the ``python -m
newsletter`` pipeline can perform basic web lookups without relying on the
agent runtime.  It is intentionally simple — production-quality research is
expected to come from an agent that has access to ``web_fetch`` and can reason
about the results.

The functions below are also available as callable tools for any Python-based
orchestrator that wants to pass search results into an LLM prompt.
"""

from __future__ import annotations

import urllib.parse
import urllib.request
from typing import Any


# ---------------------------------------------------------------------------
# Internal HTTP helper
# ---------------------------------------------------------------------------

def _http_get(url: str, timeout: int = 10) -> str:
    """
    Fetch *url* via HTTP GET and return the response body as a string.

    Prefers the ``requests`` library if installed (handles redirects and
    encoding more robustly); falls back to ``urllib`` from the standard
    library.
    """
    headers = {
        "User-Agent": "git-newsletter/1.0"
    }
    try:
        import requests  # optional dependency

        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except ImportError:
        pass

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        charset = resp.headers.get_content_charset("utf-8")
        return resp.read().decode(charset, errors="replace")


# ---------------------------------------------------------------------------
# Public skill functions (CLI fallback)
# ---------------------------------------------------------------------------

def search_web(
    query: str,
    max_results: int = 5,
) -> list[dict[str, str]]:
    """
    Search the web for *query* and return up to *max_results* results.

    Each result is a dict with keys: ``title``, ``url``, ``snippet``.

    **Agent note**: In the Copilot agent runtime, use the built-in
    ``web_fetch`` tool instead of this function — it is more reliable and
    respects the agent's context window budget.

    This CLI fallback queries the DuckDuckGo Lite HTML endpoint (no API key
    required).
    """
    import re

    encoded = urllib.parse.urlencode({"q": query, "kl": "us-en"})
    search_url = f"https://html.duckduckgo.com/html/?{encoded}"

    try:
        html = _http_get(search_url)
    except Exception as exc:
        return [{"title": "Search unavailable", "url": "", "snippet": str(exc)}]

    link_pattern = re.compile(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S
    )
    snippet_pattern = re.compile(
        r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', re.S
    )
    tag_re = re.compile(r"<[^>]+>")

    links = link_pattern.findall(html)
    snippets = snippet_pattern.findall(html)

    results: list[dict[str, str]] = []
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
    Fetch a web page at *url* and return its text content (HTML tags stripped)
    truncated to *max_chars* characters.

    **Agent note**: In the Copilot agent runtime, use the built-in
    ``web_fetch`` tool instead — it returns cleaner, already-processed content
    and is not subject to network restrictions that may apply to Python code.

    This CLI fallback strips script/style blocks and collapses whitespace.
    """
    import re

    try:
        html = _http_get(url)
    except Exception as exc:
        return f"Could not fetch page: {exc}"

    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]

