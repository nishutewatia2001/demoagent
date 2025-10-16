# Zero-Key Trip & Task Planner (ZTTP)

ZTTP is a multi-agent itinerary planner designed to demonstrate the ADK feature set:

- **Memory integration** with a SQLite profile + itinerary history.
- **Zero-cost tool use** against public APIs (Wikipedia, Open-Meteo, exchangerate.host).
- **MCP connectivity** for filesystem, SQLite, and optional HTTP proxying.
- **Multi-agent orchestration** spanning planning, research, scheduling, checklisting, evaluation, and presentation.
- **Parallel research tasks** (Wikipedia fetch) and concurrent telemetry logging.
- **Rule-based self evaluation** with automatic telemetry capture.

## Repository layout

```
zttp/
├─ adk_app/
│  ├─ agents/             # Multi-agent roles (planner, researcher, scheduler, ...)
│  ├─ tools/              # Public API helpers and local utilities
│  ├─ memory/             # SQLite schema + memory service wrapper
│  ├─ telemetry/          # Span logger writing to sqlite
│  ├─ orchestration/      # Graph wiring agents together
│  ├─ mcp/                # Filesystem + SQLite MCP configs
│  └─ app.py              # Application factory and demo entrypoint
├─ notes/                 # MCP-visible notes mount
├─ plans/                 # Generated itineraries
├─ db/                    # SQLite database location
├─ requirements.txt
├─ .env.example
└─ README.md
```

## Quickstart

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the demo orchestrator:
   ```bash
   python -m adk_app.app
   ```
   The script will fetch a sample itinerary, save it into `plans/`, and print the file path.
3. Launch the optional web UI (standard-library HTTP server):
   ```bash
   python -m adk_app.web.server
   ```
   Visit <http://127.0.0.1:8080> to enter your own city, dates, budget, pace, and optional coordinates for weather-aware itineraries. The browser view shows the resulting schedule, POIs, checklist, rubric score, and the saved Markdown path.
4. Inspect telemetry and memory in `db/zttp.sqlite` using any SQLite browser.

## Training flow (2–3 hours)

Each lab builds upon the previous to showcase ADK concepts:

| Lab | Duration | Focus |
| --- | --- | --- |
| 0 | 15 min | Scaffold project, wire session service, verify hello-world agent |
| 1 | 30 min | Implement zero-cost tools (Wikipedia, weather, currency, markdown export) |
| 2 | 20 min | Add SQLite-backed memory for user preferences and itinerary history |
| 3 | 25 min | Introduce MCP for filesystem + SQLite portability |
| 4 | 30 min | Construct multi-agent pipeline with artifact passing |
| 5 | 20 min | Parallelize POI fetches and supporting calls |
| 6 | 25 min | Add rule-based evaluator with auto re-plan |
| 7 | 15 min | Capture telemetry spans and expose aggregate views |

