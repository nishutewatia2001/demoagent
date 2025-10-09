"""Deterministic evaluator applying a simple itinerary rubric."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class EvaluationResult:
    score: int
    max: int
    rules: Dict[str, bool]

    @property
    def passed(self) -> bool:
        return self.score >= max(1, int(self.max * 0.7))


def evaluate(plan: Dict[str, Any]) -> EvaluationResult:
    schedule: List[Dict[str, Any]] = plan.get("schedule", [])
    stops: List[Dict[str, Any]] = plan.get("stops", [])
    rules = {
        "has_two_meals": any(
            "breakfast" in segment.get("activity", "").lower()
            or "lunch" in segment.get("activity", "").lower()
            for day in schedule
            for segment in day.get("segments", [])
        ),
        "covers_3_pois": len(stops) >= 3,
        "weather_aware": bool(plan.get("weather_note")),
        "budget_tagged": plan.get("budget") in {"low", "mid", "high"},
        "no_duplicates": len({stop.get("title") for stop in stops}) == len(stops),
        "has_sources": all(stop.get("source") for stop in stops),
    }
    score = sum(int(value) for value in rules.values())
    return EvaluationResult(score=score, max=len(rules), rules=rules)

