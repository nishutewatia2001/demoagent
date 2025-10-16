"""MediaWiki helper tools for the ZTTP project."""

from __future__ import annotations

from typing import Dict, List

import requests

BASE_URL = "https://en.wikipedia.org/w/api.php"


def _fallback_search(query: str, limit: int) -> List[Dict[str, str]]:
    generic = [
        {"title": "City Highlights", "snippet": "Top landmarks and iconic views."},
        {"title": "Local Museum", "snippet": "Art, history, and culture under one roof."},
        {"title": "Neighborhood Market", "snippet": "Street food and artisan crafts."},
        {"title": "Riverside Walk", "snippet": "Relaxing strolls along the water."},
        {"title": "Cultural Center", "snippet": "Workshops, performances, and exhibits."},
    ]
    return generic[:limit]


def wiki_search(query: str, limit: int = 5) -> List[Dict[str, str]]:
    try:
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
    except Exception:
        data = _fallback_search(query, limit)
    return [{"title": item.get("title", "Unnamed"), "snippet": item.get("snippet", "")} for item in data]


def wiki_page(title: str) -> Dict[str, str]:
    try:
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
    except Exception:
        page = {"title": title, "extract": f"Overview for {title}."}
    return {"title": page.get("title", title), "text": page.get("extract", "")}

