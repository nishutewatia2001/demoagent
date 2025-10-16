"""Simple HTTP UI for interacting with the Zero-Key Trip & Task Planner."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import parse_qs

from adk_app.app import Application, create_app


def _base_path() -> Path:
    return Path(__file__).resolve().parents[2]


class PlannerRequestHandler(BaseHTTPRequestHandler):
    """Serve the static UI and handle planning requests."""

    app: Application = create_app(_base_path())
    index_path = Path(__file__).parent / "templates" / "index.html"

    def log_message(self, format: str, *args) -> None:  # pragma: no cover - keep server quiet
        return

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler API)
        if self.path in {"/", "/index.html"}:
            self._serve_index()
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler API)
        if self.path != "/plan":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        content_type = self.headers.get("Content-Type", "application/json")

        if "application/json" in content_type:
            try:
                payload = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON payload")
                return
        else:
            payload = {k: v[0] for k, v in parse_qs(body).items()}

        try:
            request = self._parse_payload(payload)
        except ValueError as exc:
            self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        try:
            result = self.app.run(request)
        except Exception as exc:
            self._write_json({"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        response = {
            "plan": result["plan"],
            "artifact_path": result.get("artifact_path"),
            "evaluation": asdict(result["evaluation"]),
            "passed": result.get("passed"),
        }
        self._write_json(response)

    def _serve_index(self) -> None:
        if not self.index_path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "UI template missing")
            return
        with self.index_path.open("rb") as handle:
            content = handle.read()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _parse_payload(self, payload: Dict[str, object]) -> Dict[str, object]:
        required = ["user_id", "city", "start_date", "duration_days", "pace", "budget"]
        missing = [key for key in required if key not in payload or payload[key] in {None, ""}]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        start_date = date.fromisoformat(str(payload["start_date"]))
        duration = int(payload["duration_days"])
        weather_coordinates: Optional[Dict[str, float]] = None
        lat = payload.get("lat")
        lon = payload.get("lon")
        if lat not in {None, ""} and lon not in {None, ""}:
            try:
                weather_coordinates = {"lat": float(lat), "lon": float(lon)}
            except (TypeError, ValueError) as exc:
                raise ValueError("Latitude and longitude must be numbers") from exc

        return {
            "user_id": str(payload["user_id"]),
            "city": str(payload["city"]),
            "start_date": start_date,
            "duration_days": duration,
            "pace": str(payload["pace"]),
            "budget": str(payload["budget"]),
            "weather_coordinates": weather_coordinates,
        }

    def _write_json(self, payload: Dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(host: str = "127.0.0.1", port: int = 8080) -> None:
    """Start the planner HTTP server."""

    server = ThreadingHTTPServer((host, port), PlannerRequestHandler)
    print(f"ZTTP web UI available at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - manual shutdown
        pass
    finally:
        server.server_close()


def main() -> None:
    host = os.environ.get("ZTTP_HOST", "127.0.0.1")
    port = int(os.environ.get("ZTTP_PORT", "8080"))
    serve(host=host, port=port)


if __name__ == "__main__":
    main()

