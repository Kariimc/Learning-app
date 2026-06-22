"""SQLite persistence layer.

A thin, dependency-free wrapper around :mod:`sqlite3`. All progress, profiles,
rewards and analytics events are stored locally so the app is fully **offline**.
The schema is created idempotently on first run and migrated forward by version.

See ``docs/09_database_structure.md`` for the entity-relationship overview.
"""
from __future__ import annotations

import os
import sqlite3
import time
from contextlib import contextmanager
from typing import Iterable, Optional

SCHEMA_VERSION = 1


class Database:
    """Owns a single SQLite connection and the schema."""

    def __init__(self, path: str):
        self.path = path
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        # check_same_thread=False: Kivy clock callbacks may touch the DB from
        # the main thread while audio runs on a worker; we serialise writes.
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._create_schema()

    # ------------------------------------------------------------------ #
    # Connection helpers
    # ------------------------------------------------------------------ #
    @property
    def conn(self) -> sqlite3.Connection:
        return self._conn

    @contextmanager
    def tx(self):
        """Transaction context manager."""
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------------ #
    # Schema
    # ------------------------------------------------------------------ #
    def _create_schema(self) -> None:
        with self.tx() as c:
            c.executescript(
                """
                CREATE TABLE IF NOT EXISTS meta (
                    key   TEXT PRIMARY KEY,
                    value TEXT
                );

                CREATE TABLE IF NOT EXISTS profiles (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT NOT NULL,
                    avatar      TEXT DEFAULT 'reading_rabbit',
                    birth_year  INTEGER,
                    created_at  REAL NOT NULL,
                    last_active REAL,
                    settings    TEXT DEFAULT '{}'
                );

                -- One mastery row per (profile, content item).
                CREATE TABLE IF NOT EXISTS progress (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id    INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                    stage         INTEGER NOT NULL,
                    item_id       TEXT NOT NULL,
                    mastery       INTEGER DEFAULT 0,   -- 0..MASTERY_THRESHOLD
                    attempts      INTEGER DEFAULT 0,
                    correct       INTEGER DEFAULT 0,
                    last_seen     REAL,
                    UNIQUE(profile_id, stage, item_id)
                );

                -- Per (profile, stage) adaptive difficulty + unlock state.
                CREATE TABLE IF NOT EXISTS stage_state (
                    profile_id  INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                    stage       INTEGER NOT NULL,
                    unlocked    INTEGER DEFAULT 0,
                    difficulty  REAL DEFAULT 0.0,
                    streak      INTEGER DEFAULT 0,
                    PRIMARY KEY (profile_id, stage)
                );

                -- Rewards earned: stickers, badges, unlocked characters.
                CREATE TABLE IF NOT EXISTS rewards (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id  INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                    kind        TEXT NOT NULL,   -- sticker|badge|character|chest
                    reward_id   TEXT NOT NULL,
                    earned_at   REAL NOT NULL,
                    UNIQUE(profile_id, kind, reward_id)
                );

                CREATE TABLE IF NOT EXISTS stars (
                    profile_id  INTEGER PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
                    total       INTEGER DEFAULT 0
                );

                -- Analytics event log powering the parent dashboard.
                CREATE TABLE IF NOT EXISTS events (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id  INTEGER REFERENCES profiles(id) ON DELETE CASCADE,
                    ts          REAL NOT NULL,
                    kind        TEXT NOT NULL,   -- answer|session|reward|stage_unlock
                    stage       INTEGER,
                    item_id     TEXT,
                    correct     INTEGER,
                    payload     TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_events_profile_ts
                    ON events(profile_id, ts);
                CREATE INDEX IF NOT EXISTS idx_progress_profile
                    ON progress(profile_id, stage);
                """
            )
            c.execute(
                "INSERT OR IGNORE INTO meta(key, value) VALUES ('schema_version', ?)",
                (str(SCHEMA_VERSION),),
            )

    # ------------------------------------------------------------------ #
    # Generic helpers
    # ------------------------------------------------------------------ #
    def execute(self, sql: str, params: Iterable = ()):  # pragma: no cover - trivial
        return self._conn.execute(sql, tuple(params))

    def query_one(self, sql: str, params: Iterable = ()) -> Optional[sqlite3.Row]:
        cur = self._conn.execute(sql, tuple(params))
        return cur.fetchone()

    def query_all(self, sql: str, params: Iterable = ()):
        cur = self._conn.execute(sql, tuple(params))
        return cur.fetchall()

    def log_event(
        self,
        profile_id: Optional[int],
        kind: str,
        stage: Optional[int] = None,
        item_id: Optional[str] = None,
        correct: Optional[bool] = None,
        payload: Optional[str] = None,
    ) -> None:
        with self.tx() as c:
            c.execute(
                "INSERT INTO events(profile_id, ts, kind, stage, item_id, correct, payload) "
                "VALUES (?,?,?,?,?,?,?)",
                (
                    profile_id,
                    time.time(),
                    kind,
                    stage,
                    item_id,
                    None if correct is None else int(correct),
                    payload,
                ),
            )
