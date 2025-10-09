"""Researcher agent responsible for gathering POIs from public sources."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from adk_app.tools.wiki import wiki_page, wiki_search


async def _fetch_page(title: str) -> Dict[str, Any]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, wiki_page, title)


async def _fetch_pages(titles: Iterable[str]) -> List[Dict[str, Any]]:
    return await asyncio.gather(*(_fetch_page(t) for t in titles))


@dataclass
class ResearcherAgent:
    """Collect information about points of interest."""

    max_results: int = 6

    async def research(self, *, city: str, focus: str | None = None) -> Dict[str, Any]:
        query = f"{city} points of interest"
        if focus:
            query = f"{query} {focus}"
        search_results = wiki_search(query, limit=self.max_results)
        titles = [result["title"] for result in search_results]
        pages = await _fetch_pages(titles)
        pois: List[Dict[str, Any]] = []
        for page, result in zip(pages, search_results):
            pois.append(
                {
                    "title": page.get("title") or result["title"],
                    "summary": (page.get("text") or "").split("\n", 1)[0].strip(),
                    "source": f"https://en.wikipedia.org/wiki/{result['title'].replace(' ', '_')}",
                }
            )
        return {"city": city, "pois": pois}

