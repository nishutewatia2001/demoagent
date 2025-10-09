"""Simple orchestration graph that wires agents and tools together."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional

from adk_app.agents import evaluator
from adk_app.agents.checklist import ChecklistAgent
from adk_app.agents.planner import PlannerAgent
from adk_app.agents.presenter import PresenterAgent
from adk_app.agents.researcher import ResearcherAgent
from adk_app.agents.scheduler import SchedulerAgent
from adk_app.memory.sqlite_memory import SQLiteMemoryService
from adk_app.telemetry.logger import TelemetryLogger
from adk_app.tools.weather import weather_forecast


@dataclass
class OrchestrationGraph:
    planner: PlannerAgent
    researcher: ResearcherAgent
    scheduler: SchedulerAgent
    checklist: ChecklistAgent
    presenter: PresenterAgent
    memory: SQLiteMemoryService
    telemetry: TelemetryLogger

    def run(
        self,
        *,
        user_id: str,
        city: str,
        start_date: date,
        duration_days: int,
        pace: str,
        weather_coordinates: Optional[Dict[str, float]] = None,
        budget: str = "mid",
    ) -> Dict[str, Any]:
        run_id = f"run-{start_date.isoformat()}-{city.replace(' ', '_')}"
        profile = self.memory.get_user_profile(user_id) or {}
        merged_pace = profile.get("pace_preference", pace)
        skeleton = self.planner.plan(city=city, travel_date=start_date, duration_days=duration_days, pace=merged_pace)

        with self.telemetry.span(run_id=run_id, agent="researcher", tool="wiki"):
            pois_payload = asyncio.run(self.researcher.research(city=city, focus=profile.get("must_avoid")))
        pois = pois_payload.get("pois", [])

        schedule_payload = self.scheduler.schedule(skeleton=skeleton, pois=pois)
        schedule = schedule_payload["schedule"]
        stops = schedule_payload["stops"]

        weather_note: Optional[str] = None
        weather_data: Dict[str, Any] | None = None
        if weather_coordinates:
            lat = weather_coordinates.get("lat")
            lon = weather_coordinates.get("lon")
            if lat is not None and lon is not None:
                with self.telemetry.span(run_id=run_id, agent="weather", tool="open-meteo"):
                    weather_data = weather_forecast(lat, lon, start_date.isoformat())
                precip_values = weather_data.get("precipitation_probability_max", [0]) if weather_data else [0]
                temp_high = weather_data.get("temperature_2m_max", [None])[0] if weather_data else None
                temp_low = weather_data.get("temperature_2m_min", [None])[0] if weather_data else None
                weather_note = (
                    f"Chance of precipitation: {max(precip_values)}% | Temps: {temp_low}°C – {temp_high}°C"
                )

        checklist_payload = self.checklist.build(schedule=schedule, weather=weather_data)

        plan = {
            "schedule": schedule,
            "stops": stops,
            "weather_note": weather_note,
            "budget": budget,
            "checklist": checklist_payload,
        }

        evaluation = evaluator.evaluate(plan)
        with self.telemetry.span(run_id=run_id, agent="evaluator", tool="rule-rubric"):
            passed = evaluation.passed

        filename = f"{start_date.isoformat()}_{city.replace(' ', '_').lower()}.md"
        with self.telemetry.span(run_id=run_id, agent="presenter", tool="md_export"):
            artifact_path = self.presenter.present(
                filename=filename,
                schedule=schedule,
                stops=stops,
                checklist=checklist_payload,
                weather_note=weather_note,
            )

        self.memory.record_itinerary(
            user_id=user_id,
            city=city,
            start_date=start_date.isoformat(),
            duration_days=duration_days,
            artifact_path=artifact_path,
        )

        return {
            "run_id": run_id,
            "plan": plan,
            "evaluation": evaluation,
            "artifact_path": artifact_path,
            "profile": profile,
            "passed": passed,
        }

