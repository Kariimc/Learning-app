"""Child profile management.

Supports multiple children on one device. Each profile is a fully isolated set
of progress, rewards and analytics. No PII beyond a first name / nickname and an
optional birth year (used only to suggest a starting stage) is ever stored.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import List, Optional

from .database import Database


@dataclass
class Profile:
    id: int
    name: str
    avatar: str
    birth_year: Optional[int]
    created_at: float
    last_active: Optional[float]
    settings: dict

    @classmethod
    def from_row(cls, row) -> "Profile":
        return cls(
            id=row["id"],
            name=row["name"],
            avatar=row["avatar"],
            birth_year=row["birth_year"],
            created_at=row["created_at"],
            last_active=row["last_active"],
            settings=json.loads(row["settings"] or "{}"),
        )


class ProfileManager:
    def __init__(self, db: Database):
        self.db = db

    def create(self, name: str, avatar: str = "reading_rabbit",
               birth_year: Optional[int] = None) -> Profile:
        now = time.time()
        with self.db.tx() as c:
            cur = c.execute(
                "INSERT INTO profiles(name, avatar, birth_year, created_at, last_active) "
                "VALUES (?,?,?,?,?)",
                (name.strip()[:24] or "Friend", avatar, birth_year, now, now),
            )
            pid = cur.lastrowid
            c.execute("INSERT OR IGNORE INTO stars(profile_id, total) VALUES (?, 0)", (pid,))
            # Stage 1 is always unlocked for a new child.
            c.execute(
                "INSERT OR IGNORE INTO stage_state(profile_id, stage, unlocked) VALUES (?, 1, 1)",
                (pid,),
            )
        return self.get(pid)

    def get(self, profile_id: int) -> Optional[Profile]:
        row = self.db.query_one("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        return Profile.from_row(row) if row else None

    def list(self) -> List[Profile]:
        rows = self.db.query_all("SELECT * FROM profiles ORDER BY last_active DESC, id ASC")
        return [Profile.from_row(r) for r in rows]

    def touch(self, profile_id: int) -> None:
        with self.db.tx() as c:
            c.execute("UPDATE profiles SET last_active = ? WHERE id = ?",
                      (time.time(), profile_id))

    def update_settings(self, profile_id: int, **kwargs) -> None:
        prof = self.get(profile_id)
        if not prof:
            return
        prof.settings.update(kwargs)
        with self.db.tx() as c:
            c.execute("UPDATE profiles SET settings = ? WHERE id = ?",
                      (json.dumps(prof.settings), profile_id))

    def rename(self, profile_id: int, name: str) -> None:
        with self.db.tx() as c:
            c.execute("UPDATE profiles SET name = ? WHERE id = ?",
                      (name.strip()[:24] or "Friend", profile_id))

    def delete(self, profile_id: int) -> None:
        with self.db.tx() as c:
            c.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))

    @staticmethod
    def suggested_stage(birth_year: Optional[int], today_year: int = 2026) -> int:
        """Gently suggest a starting stage from age. Children can still roam."""
        if not birth_year:
            return 1
        age = max(0, today_year - birth_year)
        if age <= 3:
            return 1
        if age == 4:
            return 2
        if age == 5:
            return 3
        if age == 6:
            return 4
        return 5
