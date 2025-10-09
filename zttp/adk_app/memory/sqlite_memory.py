"""SQLite-backed memory service for user profiles and itineraries."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SQLiteMemoryService:
    db_path: Path

    def __post_init__(self) -> None:
        self.ensure_schema()

    @property
    def _connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def ensure_schema(self) -> None:
        schema_path = Path(__file__).with_name("schema.sql")
        sql = schema_path.read_text(encoding="utf-8")
        with self._connection as conn:
            conn.executescript(sql)

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, str]]:
        with self._connection as conn:
            row = conn.execute(
                "SELECT user_id, budget_tier, pace_preference, must_avoid FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "user_id": row[0],
            "budget_tier": row[1],
            "pace_preference": row[2],
            "must_avoid": row[3],
        }

    def upsert_user_profile(
        self, user_id: str, *, budget_tier: str, pace_preference: str, must_avoid: str
    ) -> None:
        with self._connection as conn:
            conn.execute(
                """
                INSERT INTO users(user_id, budget_tier, pace_preference, must_avoid)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    budget_tier=excluded.budget_tier,
                    pace_preference=excluded.pace_preference,
                    must_avoid=excluded.must_avoid
                """,
                (user_id, budget_tier, pace_preference, must_avoid),
            )

    def record_itinerary(
        self,
        *,
        user_id: str,
        city: str,
        start_date: str,
        duration_days: int,
        artifact_path: str,
    ) -> None:
        with self._connection as conn:
            conn.execute(
                """
                INSERT INTO itineraries(user_id, city, start_date, duration_days, artifact_path)
                VALUES(?, ?, ?, ?, ?)
                """,
                (user_id, city, start_date, duration_days, artifact_path),
            )

    def fetch_last_itineraries(self, user_id: str, limit: int = 5) -> List[Dict[str, str]]:
        with self._connection as conn:
            rows = conn.execute(
                """
                SELECT city, start_date, duration_days, artifact_path
                FROM itineraries
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [
            {
                "city": row[0],
                "start_date": row[1],
                "duration_days": row[2],
                "artifact_path": row[3],
            }
            for row in rows
        ]

