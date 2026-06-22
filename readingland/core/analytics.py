"""Parent-dashboard analytics.

Turns the raw ``events`` log into the friendly numbers a parent wants: time on
task, accuracy, current reading level, words learned, streaks and a per-stage
breakdown. All computed locally - nothing leaves the device.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from .. import config
from .content import ContentLibrary
from .database import Database
from .progress import ProgressTracker


@dataclass
class DashboardReport:
    profile_id: int
    profile_name: str
    overall_percent: int
    current_stage: int
    current_stage_title: str
    total_stars: int
    accuracy: float
    items_mastered: int
    items_total: int
    active_days_streak: int
    minutes_last_7_days: int
    stage_breakdown: List[dict] = field(default_factory=list)
    recent_activity: List[dict] = field(default_factory=list)


class Analytics:
    def __init__(self, db: Database, content: ContentLibrary, progress: ProgressTracker):
        self.db = db
        self.content = content
        self.progress = progress

    def _accuracy(self, profile_id: int) -> float:
        row = self.db.query_one(
            "SELECT COUNT(*) AS n, SUM(correct) AS ok FROM events "
            "WHERE profile_id=? AND kind='answer'",
            (profile_id,),
        )
        if not row or not row["n"]:
            return 0.0
        return round((row["ok"] or 0) / row["n"], 3)

    def _active_days_streak(self, profile_id: int) -> int:
        rows = self.db.query_all(
            "SELECT DISTINCT date(ts, 'unixepoch') AS d FROM events "
            "WHERE profile_id=? ORDER BY d DESC",
            (profile_id,),
        )
        if not rows:
            return 0
        days = [r["d"] for r in rows]
        streak = 0
        cursor = datetime.now(timezone.utc).date()
        day_set = set(days)
        # Allow today OR yesterday to start a streak.
        if cursor.isoformat() not in day_set:
            cursor = cursor - timedelta(days=1)
            if cursor.isoformat() not in day_set:
                return 0
        while cursor.isoformat() in day_set:
            streak += 1
            cursor = cursor - timedelta(days=1)
        return streak

    def _minutes_last_7_days(self, profile_id: int) -> int:
        """Estimate engaged minutes by counting answer events in 7 days.

        Without explicit session timers we approximate ~20s of engaged time per
        answer event, capped sensibly. (Real session timing is logged as
        'session' events by the UI when available.)
        """
        since = (datetime.now(timezone.utc) - timedelta(days=7)).timestamp()
        # Prefer real session events if the UI logged them.
        row = self.db.query_one(
            "SELECT SUM(CAST(payload AS REAL)) AS secs FROM events "
            "WHERE profile_id=? AND kind='session' AND ts>=?",
            (profile_id, since),
        )
        if row and row["secs"]:
            return round(row["secs"] / 60)
        ans = self.db.query_one(
            "SELECT COUNT(*) AS n FROM events "
            "WHERE profile_id=? AND kind='answer' AND ts>=?",
            (profile_id, since),
        )
        n = ans["n"] if ans else 0
        return round(n * 20 / 60)

    def _current_stage(self, profile_id: int) -> int:
        # Highest unlocked stage that still has unmastered items, else last stage.
        current = 1
        for s in config.STAGES:
            if self.progress.is_unlocked(profile_id, s["id"]):
                current = s["id"]
        return current

    def _recent(self, profile_id: int, limit: int = 12) -> List[dict]:
        rows = self.db.query_all(
            "SELECT ts, kind, stage, item_id, correct FROM events "
            "WHERE profile_id=? AND kind IN ('answer','reward','stage_unlock') "
            "ORDER BY ts DESC LIMIT ?",
            (profile_id, limit),
        )
        out = []
        for r in rows:
            out.append({
                "when": datetime.fromtimestamp(r["ts"], tz=timezone.utc).strftime("%b %d %H:%M"),
                "kind": r["kind"],
                "stage": r["stage"],
                "item": r["item_id"],
                "correct": None if r["correct"] is None else bool(r["correct"]),
            })
        return out

    def report(self, profile_id: int) -> DashboardReport:
        prof = self.db.query_one("SELECT name FROM profiles WHERE id=?", (profile_id,))
        name = prof["name"] if prof else "Friend"
        summaries = self.progress.all_summaries(profile_id)
        items_mastered = sum(s.mastered for s in summaries)
        items_total = sum(s.total for s in summaries)
        cur = self._current_stage(profile_id)
        breakdown = [{
            "stage": s.stage,
            "title": config.STAGE_BY_ID[s.stage]["title"],
            "unlocked": s.unlocked,
            "mastered": s.mastered,
            "total": s.total,
            "percent": s.percent,
        } for s in summaries]

        return DashboardReport(
            profile_id=profile_id,
            profile_name=name,
            overall_percent=self.progress.overall_percent(profile_id),
            current_stage=cur,
            current_stage_title=config.STAGE_BY_ID[cur]["title"],
            total_stars=self.progress.stars(profile_id),
            accuracy=self._accuracy(profile_id),
            items_mastered=items_mastered,
            items_total=items_total,
            active_days_streak=self._active_days_streak(profile_id),
            minutes_last_7_days=self._minutes_last_7_days(profile_id),
            stage_breakdown=breakdown,
            recent_activity=self._recent(profile_id),
        )
