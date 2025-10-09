"""Simple telemetry span logger for recording tool usage."""

from __future__ import annotations

import contextlib
import sqlite3
import time
import uuid
from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass
class TelemetryLogger:
    db_path: str

    @contextlib.contextmanager
    def span(self, *, run_id: Optional[str], agent: str, tool: str) -> Iterator[None]:
        if run_id is None:
            run_id = str(uuid.uuid4())
        start = time.time()
        error: Optional[str] = None
        try:
            yield
        except Exception as exc:  # pragma: no cover - passthrough to caller
            error = str(exc)
            raise
        finally:
            end = time.time()
            latency_ms = int((end - start) * 1000)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO telemetry(run_id, agent, tool, start_ts, end_ts, latency_ms, error)
                    VALUES(?, ?, ?, ?, ?, ?, ?)
                    """,
                    (run_id, agent, tool, start, end, latency_ms, error),
                )

