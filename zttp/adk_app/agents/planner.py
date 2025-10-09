"""Planner agent responsible for drafting a coarse itinerary skeleton."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List


@dataclass
class PlannerAgent:
    """Generate a high-level plan layout for a given trip request."""

    def plan(self, *, city: str, travel_date: date, duration_days: int, pace: str) -> Dict[str, Any]:
        """Return a simple day-by-day skeleton.

        Parameters
        ----------
        city:
            Name of the destination city.
        travel_date:
            Date of the first day of the trip.
        duration_days:
            Number of days to plan for.
        pace:
            Desired pace (e.g., "leisurely", "balanced", "packed").
        """
        slots: List[Dict[str, Any]] = []
        for offset in range(duration_days):
            day_label = travel_date.fromordinal(travel_date.toordinal() + offset).isoformat()
            slots.append(
                {
                    "date": day_label,
                    "city": city,
                    "pace": pace,
                    "segments": [
                        {"slot": "morning", "notes": []},
                        {"slot": "afternoon", "notes": []},
                        {"slot": "evening", "notes": []},
                    ],
                }
            )
        return {"city": city, "days": slots}

