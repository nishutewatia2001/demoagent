"""Checklist agent builds packing and task lists."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ChecklistAgent:
    """Create lightweight packing and preparation tasks."""

    def build(self, *, schedule: List[Dict[str, Any]], weather: Dict[str, Any] | None = None) -> Dict[str, Any]:
        packing = ["Comfortable walking shoes", "Reusable water bottle", "Phone charger"]
        tasks = ["Download offline maps", "Confirm local transit options"]
        if weather:
            precipitation = weather.get("precipitation_probability_max", [0])
            if any(p > 40 for p in precipitation):
                packing.append("Light rain jacket")
        if schedule:
            packing.append("Tickets or confirmations for booked activities")
        return {"packing": sorted(set(packing)), "tasks": tasks}

