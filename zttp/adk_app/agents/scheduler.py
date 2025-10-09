"""Scheduler agent that orders activities and attaches metadata to slots."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from adk_app.tools.geo import cluster_points


@dataclass
class SchedulerAgent:
    """Arrange researched POIs into the planner skeleton."""

    def schedule(self, *, skeleton: Dict[str, Any], pois: List[Dict[str, Any]]) -> Dict[str, Any]:
        days = skeleton.get("days", [])
        if not days:
            return {"schedule": [], "stops": []}
        clusters = cluster_points(pois, buckets=len(days) or 1)
        schedule: List[Dict[str, Any]] = []
        stops: List[Dict[str, Any]] = []
        poi_iter = iter(pois)
        for day, cluster in zip(days, clusters):
            segments = day["segments"]
            day_plan = {"date": day["date"], "city": day["city"], "segments": []}
            for segment in segments:
                poi = next(poi_iter, None)
                if poi is None and cluster:
                    poi = cluster.pop(0)
                if poi is None:
                    entry = {"slot": segment["slot"], "activity": "Open exploration"}
                else:
                    stops.append(poi)
                    entry = {
                        "slot": segment["slot"],
                        "activity": poi["title"],
                        "summary": poi.get("summary"),
                    }
                day_plan["segments"].append(entry)
            schedule.append(day_plan)
        return {"schedule": schedule, "stops": stops}

