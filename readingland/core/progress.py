"""Progress & mastery tracking.

Records every answer, advances per-item mastery, awards stars, unlocks the next
stage when enough of the current stage is mastered, and surfaces summaries for
the world map and the parent dashboard.

Design note: a child is *never punished*. A wrong answer simply doesn't advance
mastery and nudges the adaptive engine toward more support - it never subtracts
stars or locks anything.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from .. import config
from .content import ContentLibrary
from .database import Database


@dataclass
class AnswerResult:
    correct: bool
    first_try: bool
    mastery: int
    mastered_now: bool
    stars_awarded: int
    stage_unlocked: Optional[int]  # stage id newly unlocked, if any


@dataclass
class StageSummary:
    stage: int
    unlocked: bool
    total: int
    mastered: int
    started: int

    @property
    def ratio(self) -> float:
        return (self.mastered / self.total) if self.total else 0.0

    @property
    def percent(self) -> int:
        return round(self.ratio * 100)


class ProgressTracker:
    def __init__(self, db: Database, content: ContentLibrary):
        self.db = db
        self.content = content

    # ------------------------------------------------------------------ #
    # Recording answers
    # ------------------------------------------------------------------ #
    def record_answer(
        self, profile_id: int, stage: int, item_id: str, correct: bool
    ) -> AnswerResult:
        row = self.db.query_one(
            "SELECT mastery, attempts, correct FROM progress "
            "WHERE profile_id=? AND stage=? AND item_id=?",
            (profile_id, stage, item_id),
        )
        first_try = row is None or row["attempts"] == 0
        prev_mastery = row["mastery"] if row else 0

        new_mastery = prev_mastery
        if correct and prev_mastery < config.MASTERY_THRESHOLD:
            new_mastery = prev_mastery + 1
        mastered_now = (
            new_mastery >= config.MASTERY_THRESHOLD
            and prev_mastery < config.MASTERY_THRESHOLD
        )

        with self.db.tx() as c:
            if row is None:
                c.execute(
                    "INSERT INTO progress(profile_id, stage, item_id, mastery, attempts, "
                    "correct, last_seen) VALUES (?,?,?,?,?,?,?)",
                    (profile_id, stage, item_id, new_mastery, 1,
                     1 if correct else 0, time.time()),
                )
            else:
                c.execute(
                    "UPDATE progress SET mastery=?, attempts=attempts+1, "
                    "correct=correct+?, last_seen=? "
                    "WHERE profile_id=? AND stage=? AND item_id=?",
                    (new_mastery, 1 if correct else 0, time.time(),
                     profile_id, stage, item_id),
                )

        # Stars (only ever added).
        stars = 0
        if correct:
            stars = config.STARS_PER_PERFECT if first_try else config.STARS_PER_CORRECT
            self._add_stars(profile_id, stars)

        self.db.log_event(profile_id, "answer", stage, item_id, correct)

        unlocked = self._maybe_unlock_next(profile_id, stage) if mastered_now else None
        return AnswerResult(
            correct=correct,
            first_try=first_try,
            mastery=new_mastery,
            mastered_now=mastered_now,
            stars_awarded=stars,
            stage_unlocked=unlocked,
        )

    # ------------------------------------------------------------------ #
    # Stars
    # ------------------------------------------------------------------ #
    def _add_stars(self, profile_id: int, amount: int) -> None:
        with self.db.tx() as c:
            c.execute("INSERT OR IGNORE INTO stars(profile_id, total) VALUES (?,0)",
                      (profile_id,))
            c.execute("UPDATE stars SET total = total + ? WHERE profile_id=?",
                      (amount, profile_id))

    def stars(self, profile_id: int) -> int:
        row = self.db.query_one("SELECT total FROM stars WHERE profile_id=?", (profile_id,))
        return row["total"] if row else 0

    # ------------------------------------------------------------------ #
    # Stage unlocking
    # ------------------------------------------------------------------ #
    def is_unlocked(self, profile_id: int, stage: int) -> bool:
        if stage <= 1:
            return True
        row = self.db.query_one(
            "SELECT unlocked FROM stage_state WHERE profile_id=? AND stage=?",
            (profile_id, stage),
        )
        return bool(row and row["unlocked"])

    def _unlock(self, profile_id: int, stage: int) -> None:
        with self.db.tx() as c:
            c.execute(
                "INSERT INTO stage_state(profile_id, stage, unlocked) VALUES (?,?,1) "
                "ON CONFLICT(profile_id, stage) DO UPDATE SET unlocked=1",
                (profile_id, stage),
            )
        self.db.log_event(profile_id, "stage_unlock", stage)

    def _maybe_unlock_next(self, profile_id: int, stage: int) -> Optional[int]:
        nxt = stage + 1
        if nxt not in config.STAGE_BY_ID or self.is_unlocked(profile_id, nxt):
            return None
        summary = self.stage_summary(profile_id, stage)
        if summary.total and summary.ratio >= config.STAGE_UNLOCK_RATIO:
            self._unlock(profile_id, nxt)
            return nxt
        return None

    # ------------------------------------------------------------------ #
    # Summaries
    # ------------------------------------------------------------------ #
    def stage_summary(self, profile_id: int, stage: int) -> StageSummary:
        total = self.content.total_items(stage)
        row = self.db.query_one(
            "SELECT "
            "  SUM(CASE WHEN mastery >= ? THEN 1 ELSE 0 END) AS mastered, "
            "  COUNT(*) AS started "
            "FROM progress WHERE profile_id=? AND stage=?",
            (config.MASTERY_THRESHOLD, profile_id, stage),
        )
        mastered = (row["mastered"] or 0) if row else 0
        started = (row["started"] or 0) if row else 0
        return StageSummary(
            stage=stage,
            unlocked=self.is_unlocked(profile_id, stage),
            total=total,
            mastered=mastered,
            started=started,
        )

    def all_summaries(self, profile_id: int) -> List[StageSummary]:
        return [self.stage_summary(profile_id, s["id"]) for s in config.STAGES]

    def item_mastery(self, profile_id: int, stage: int) -> Dict[str, int]:
        rows = self.db.query_all(
            "SELECT item_id, mastery FROM progress WHERE profile_id=? AND stage=?",
            (profile_id, stage),
        )
        return {r["item_id"]: r["mastery"] for r in rows}

    def overall_percent(self, profile_id: int) -> int:
        summaries = self.all_summaries(profile_id)
        total = sum(s.total for s in summaries)
        mastered = sum(s.mastered for s in summaries)
        return round((mastered / total) * 100) if total else 0
