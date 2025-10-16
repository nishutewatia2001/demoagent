CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    budget_tier TEXT,
    pace_preference TEXT,
    must_avoid TEXT
);

CREATE TABLE IF NOT EXISTS itineraries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    city TEXT,
    start_date TEXT,
    duration_days INTEGER,
    artifact_path TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    agent TEXT,
    tool TEXT,
    start_ts REAL,
    end_ts REAL,
    latency_ms INTEGER,
    error TEXT
);

CREATE TABLE IF NOT EXISTS rubric_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    score INTEGER,
    max INTEGER,
    passed INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
