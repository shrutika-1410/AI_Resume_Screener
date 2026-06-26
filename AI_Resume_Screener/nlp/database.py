"""SQLite-based candidate storage for persistent data across restarts."""

import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "candidates.db")


def _get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database (row factory enabled)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """Create the candidates table if it doesn't exist."""
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                email       TEXT    NOT NULL,
                skills      TEXT    DEFAULT '',
                score       INTEGER DEFAULT 0,
                job_recommendations TEXT DEFAULT '[]',
                created_at  TEXT    DEFAULT (datetime('now'))
            )
        """)


def insert_candidate(
    name: str,
    email: str,
    skills: str,
    score: int,
    job_recommendations: list[dict],
) -> int:
    """Insert a new candidate and return the new row id."""
    with _get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO candidates (name, email, skills, score, job_recommendations)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, skills, score, json.dumps(job_recommendations)),
        )
        return cur.lastrowid


def get_all_candidates() -> list[dict]:
    """Return all candidates ordered by newest first."""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM candidates ORDER BY id DESC"
        ).fetchall()

    result = []
    for row in rows:
        recs = json.loads(row["job_recommendations"]) if row["job_recommendations"] else []
        result.append({
            "name": row["name"],
            "email": row["email"],
            "skills": row["skills"],
            "score": row["score"],
            "job_recommendations": recs,
        })
    return result
