"""Gamification: stickers, badges, character unlocks, treasure chests & daily goals.

Rewards are *only* ever earned, never lost. The system is data-light: reward
definitions live here as a catalogue and are unlocked by simple rules driven by
progress events. Everything is idempotent (UNIQUE constraint in the DB), so
re-awarding is harmless.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .. import config
from .database import Database
from .progress import ProgressTracker

# --------------------------------------------------------------------------- #
# Reward catalogue (data, not behaviour).
# --------------------------------------------------------------------------- #
STICKERS: Dict[str, dict] = {
    "star_smile": {"name": "Smiley Star", "emoji": "🌟"},
    "happy_apple": {"name": "Happy Apple", "emoji": "🍎"},
    "brave_cat": {"name": "Brave Cat", "emoji": "🐱"},
    "good_dog": {"name": "Good Dog", "emoji": "🐶"},
    "rainbow": {"name": "Rainbow", "emoji": "🌈"},
    "rocket": {"name": "Reading Rocket", "emoji": "🚀"},
    "crown": {"name": "Reader's Crown", "emoji": "👑"},
    "balloon": {"name": "Party Balloon", "emoji": "🎈"},
}

BADGES: Dict[str, dict] = {
    "first_steps": {"name": "First Steps", "desc": "Finished your first activity", "emoji": "👣"},
    "letter_explorer": {"name": "Letter Explorer", "desc": "Mastered 5 letters", "emoji": "🔤"},
    "sound_smith": {"name": "Sound Smith", "desc": "Blended your first word", "emoji": "🔊"},
    "word_wizard": {"name": "Word Wizard", "desc": "Read 10 words", "emoji": "🪄"},
    "sentence_star": {"name": "Sentence Star", "desc": "Read your first sentence", "emoji": "⭐"},
    "story_reader": {"name": "Story Reader", "desc": "Finished a storybook", "emoji": "📖"},
    "streak_3": {"name": "On Fire", "desc": "3 days in a row", "emoji": "🔥"},
}

# Characters the child can unlock and "collect".
UNLOCKABLE_CHARACTERS = [
    "milo_monkey", "penny_penguin", "ollie_owl", "benny_bear",
]


@dataclass
class RewardGrant:
    kind: str
    reward_id: str
    name: str
    emoji: str
    is_new: bool


class RewardSystem:
    def __init__(self, db: Database, progress: ProgressTracker):
        self.db = db
        self.progress = progress

    # ------------------------------------------------------------------ #
    # Granting
    # ------------------------------------------------------------------ #
    def _grant(self, profile_id: int, kind: str, reward_id: str,
               name: str, emoji: str) -> RewardGrant:
        existing = self.db.query_one(
            "SELECT 1 FROM rewards WHERE profile_id=? AND kind=? AND reward_id=?",
            (profile_id, kind, reward_id),
        )
        is_new = existing is None
        if is_new:
            with self.db.tx() as c:
                c.execute(
                    "INSERT OR IGNORE INTO rewards(profile_id, kind, reward_id, earned_at) "
                    "VALUES (?,?,?,?)",
                    (profile_id, kind, reward_id, time.time()),
                )
            self.db.log_event(profile_id, "reward", item_id=f"{kind}:{reward_id}")
        return RewardGrant(kind, reward_id, name, emoji, is_new)

    def grant_sticker(self, profile_id: int, sticker_id: str) -> RewardGrant:
        info = STICKERS.get(sticker_id, {"name": sticker_id, "emoji": "✨"})
        return self._grant(profile_id, "sticker", sticker_id, info["name"], info["emoji"])

    def grant_badge(self, profile_id: int, badge_id: str) -> RewardGrant:
        info = BADGES.get(badge_id, {"name": badge_id, "emoji": "🏅"})
        return self._grant(profile_id, "badge", badge_id, info["name"], info["emoji"])

    def unlock_character(self, profile_id: int, char_id: str) -> RewardGrant:
        return self._grant(profile_id, "character", char_id, char_id.replace("_", " ").title(), "🎭")

    # ------------------------------------------------------------------ #
    # Collections (for the sticker book / rewards room)
    # ------------------------------------------------------------------ #
    def owned(self, profile_id: int, kind: str) -> List[str]:
        rows = self.db.query_all(
            "SELECT reward_id FROM rewards WHERE profile_id=? AND kind=? ORDER BY earned_at",
            (profile_id, kind),
        )
        return [r["reward_id"] for r in rows]

    def sticker_book(self, profile_id: int) -> List[dict]:
        """Full sticker catalogue with owned flag for the collection screen."""
        owned = set(self.owned(profile_id, "sticker"))
        return [
            {"id": sid, **info, "owned": sid in owned}
            for sid, info in STICKERS.items()
        ]

    def badge_shelf(self, profile_id: int) -> List[dict]:
        owned = set(self.owned(profile_id, "badge"))
        return [
            {"id": bid, **info, "owned": bid in owned}
            for bid, info in BADGES.items()
        ]

    # ------------------------------------------------------------------ #
    # Daily goal / chest
    # ------------------------------------------------------------------ #
    def _today_key(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def activities_today(self, profile_id: int) -> int:
        start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).timestamp()
        row = self.db.query_one(
            "SELECT COUNT(*) AS n FROM events "
            "WHERE profile_id=? AND kind='answer' AND ts >= ?",
            (profile_id, start),
        )
        return row["n"] if row else 0

    def daily_goal_progress(self, profile_id: int) -> dict:
        done = self.activities_today(profile_id)
        goal = config.DAILY_GOAL_ACTIVITIES
        chest_id = f"chest_{self._today_key()}"
        chest_open = self.db.query_one(
            "SELECT 1 FROM rewards WHERE profile_id=? AND kind='chest' AND reward_id=?",
            (profile_id, chest_id),
        ) is not None
        return {
            "done": min(done, goal),
            "goal": goal,
            "complete": done >= goal,
            "chest_claimed": chest_open,
            "chest_id": chest_id,
        }

    def claim_daily_chest(self, profile_id: int) -> Optional[RewardGrant]:
        prog = self.daily_goal_progress(profile_id)
        if not prog["complete"] or prog["chest_claimed"]:
            return None
        grant = self._grant(profile_id, "chest", prog["chest_id"], "Daily Chest", "🎁")
        # A chest reliably contains a sticker.
        self.progress._add_stars(profile_id, 5)
        return grant

    # ------------------------------------------------------------------ #
    # Rule engine: award milestone rewards from current progress.
    # Call after each answer; returns the list of *new* grants for celebration.
    # ------------------------------------------------------------------ #
    def evaluate_milestones(self, profile_id: int) -> List[RewardGrant]:
        new_grants: List[RewardGrant] = []

        def maybe_badge(badge_id: str):
            g = self.grant_badge(profile_id, badge_id)
            if g.is_new:
                new_grants.append(g)

        summaries = {s.stage: s for s in self.progress.all_summaries(profile_id)}

        # First activity ever.
        any_started = any(s.started for s in summaries.values())
        if any_started:
            maybe_badge("first_steps")

        if summaries.get(2) and summaries[2].mastered >= 5:
            maybe_badge("letter_explorer")
        if summaries.get(3) and summaries[3].mastered >= 1:
            maybe_badge("sound_smith")
        if summaries.get(4) and summaries[4].mastered >= 10:
            maybe_badge("word_wizard")
        if summaries.get(5) and summaries[5].mastered >= 1:
            maybe_badge("sentence_star")
        if summaries.get(6) and summaries[6].mastered >= 1:
            maybe_badge("story_reader")

        # Character unlocks tied to stage unlock.
        unlock_map = {2: "milo_monkey", 3: "benny_bear", 4: "penny_penguin", 6: "ollie_owl"}
        for stage, char in unlock_map.items():
            if summaries.get(stage) and summaries[stage].unlocked:
                g = self.unlock_character(profile_id, char)
                if g.is_new:
                    new_grants.append(g)

        return new_grants
