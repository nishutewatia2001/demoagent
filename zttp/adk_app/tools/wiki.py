"""MediaWiki helper tools for the ZTTP project."""

from __future__ import annotations

from typing import Dict, List

import requests

BASE_URL = "https://en.wikipedia.org/w/api.php"


def wiki_search(query: str, limit: int = 5) -> List[Dict[str, str]]:
    response = requests.get(
        BASE_URL,
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": limit,
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json().get("query", {}).get("search", [])
    return [{"title": item["title"], "snippet": item.get("snippet", "")} for item in data]


def wiki_page(title: str) -> Dict[str, str]:
    response = requests.get(
        BASE_URL,
        params={
            "action": "query",
            "prop": "extracts",
            "explaintext": True,
            "titles": title,
            "format": "json",
        },
        timeout=15,
    )
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    return {"title": page.get("title", title), "text": page.get("extract", "")}

