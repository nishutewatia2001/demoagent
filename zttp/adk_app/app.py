"""Application wiring for the Zero-Key Trip & Task Planner."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict

from adk_app.agents.checklist import ChecklistAgent
from adk_app.agents.planner import PlannerAgent
from adk_app.agents.presenter import PresenterAgent
from adk_app.agents.researcher import ResearcherAgent
from adk_app.agents.scheduler import SchedulerAgent
from adk_app.memory.sqlite_memory import SQLiteMemoryService
from adk_app.orchestration.graph import OrchestrationGraph
from adk_app.telemetry.logger import TelemetryLogger


@dataclass
class Application:
    graph: OrchestrationGraph

    def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return self.graph.run(**request)


def create_app(base_path: Path) -> Application:
    base_path = base_path.resolve()
    db_path = base_path / "db" / "zttp.sqlite"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    memory_service = SQLiteMemoryService(db_path=db_path)
    telemetry = TelemetryLogger(db_path=str(db_path))

    graph = OrchestrationGraph(
        planner=PlannerAgent(),
        researcher=ResearcherAgent(),
        scheduler=SchedulerAgent(),
        checklist=ChecklistAgent(),
        presenter=PresenterAgent(output_dir=str(base_path / "plans")),
        memory=memory_service,
        telemetry=telemetry,
    )
    return Application(graph=graph)


def demo() -> None:
    app = create_app(Path(__file__).resolve().parents[1])
    request = {
        "user_id": "demo-user",
        "city": "Bengaluru",
        "start_date": date.today(),
        "duration_days": 1,
        "pace": "balanced",
        "weather_coordinates": {"lat": 12.9716, "lon": 77.5946},
        "budget": "low",
    }
    result = app.run(request)
    print(f"Draft itinerary saved to: {result['artifact_path']}")


if __name__ == "__main__":
    demo()

