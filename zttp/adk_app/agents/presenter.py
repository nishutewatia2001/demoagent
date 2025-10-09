"""Presenter agent that writes the final itinerary to disk."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from adk_app.tools.export import md_export


@dataclass
class PresenterAgent:
    """Persist itinerary artifacts as Markdown files."""

    output_dir: str

    def _render_schedule(self, schedule: List[Dict[str, Any]]) -> str:
        lines = ["## Schedule"]
        for day in schedule:
            lines.append(f"### {day['date']} – {day['city']}")
            for segment in day.get("segments", []):
                summary = segment.get("summary")
                detail = f" — {summary}" if summary else ""
                lines.append(f"- **{segment['slot'].title()}**: {segment['activity']}{detail}")
        return "\n".join(lines)

    def _render_checklists(self, checklist: Dict[str, List[str]]) -> str:
        lines = ["## Packing Checklist"]
        for item in checklist.get("packing", []):
            lines.append(f"- [ ] {item}")
        lines.append("\n## Task Checklist")
        for task in checklist.get("tasks", []):
            lines.append(f"- [ ] {task}")
        return "\n".join(lines)

    def present(
        self,
        *,
        filename: str,
        schedule: List[Dict[str, Any]],
        stops: List[Dict[str, Any]],
        checklist: Dict[str, List[str]],
        weather_note: str | None = None,
    ) -> str:
        parts = ["# Zero-Key Trip & Task Planner\n"]
        if weather_note:
            parts.append(f"> Weather note: {weather_note}\n")
        parts.append(self._render_schedule(schedule))
        if stops:
            parts.append("\n## Points of Interest")
            for stop in stops:
                parts.append(f"- **{stop['title']}** — {stop.get('summary', 'No summary available.')}")
                if stop.get("source"):
                    parts.append(f"  - Source: {stop['source']}")
        parts.append("\n" + self._render_checklists(checklist))
        content = "\n".join(parts) + "\n"
        path = f"{self.output_dir}/{filename}"
        md_export(path, content)
        return path

