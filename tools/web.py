"""Web tools: search and fetch using httpx + Scrapling parser (no API keys needed)."""

import re
from typing import Any
from urllib.parse import quote_plus, urlparse, parse_qs, unquote

import httpx
from scrapling.parser import Selector

from .base import Tool


def _extract_ddg_url(raw_href: str) -> str:
    """Extract real URL from DuckDuckGo's redirect link."""
    parsed = urlparse(raw_href)
    uddg = parse_qs(parsed.query).get("uddg", [""])[0]
    return unquote(uddg) if uddg else raw_href


class WebSearchTool(Tool):
    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web using DuckDuckGo (free, no API key)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
            },
            "required": ["query"],
        }

    async def execute(self, **kwargs: Any) -> str:
        query = kwargs["query"]
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            async with httpx.AsyncClient(verify=False) as client:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15, follow_redirects=True)
            page = Selector(resp.text)

            results = []
            for item in page.css(".result"):
                titles = item.css(".result__a")
                snippets = item.css(".result__snippet")
                if not titles:
                    continue
                title = titles[0].text.strip()
                link = _extract_ddg_url(titles[0].attrib.get("href", ""))
                snippet = snippets[0].text.strip() if snippets else ""
                results.append(f"**{title}**\n{snippet}\nURL: {link}")
                if len(results) >= 5:
                    break

            return "\n\n".join(results) if results else "No results found."
        except Exception as e:
            return f"Error: {e}"


class WebFetchTool(Tool):
    @property
    def name(self) -> str:
        return "web_fetch"

    @property
    def description(self) -> str:
        return "Fetch a URL and extract readable text content."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        try:
            async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            # Strip script/style tags with regex before parsing
            html = re.sub(r"<(script|style|nav|footer|header)[^>]*>.*?</\1>", "", resp.text, flags=re.DOTALL | re.IGNORECASE)
            page = Selector(html)

            # Try get_all_text first (most reliable), then body.text
            text = page.get_all_text() or ""
            if not text:
                body = page.css("body")
                text = (body[0].text if body else page.text) or ""

            text = re.sub(r"\s+", " ", text).strip()
            if len(text) > 8000:
                text = text[:8000] + "\n... (truncated)"
            return text or "No content extracted."
        except Exception as e:
            return f"Error fetching URL: {e}"
