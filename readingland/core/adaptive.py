"""Adaptive learning engine.

Keeps a per-(profile, stage) *difficulty* value in ``0..1`` and a running streak.
The engine does three jobs:

1. Adjust difficulty up after a streak of correct answers, down after a miss -
   so the app meets each child where they are without ever feeling punishing.
2. Pick the *next item* to present, weighting toward items the child has seen
   least / mastered least (spaced practice) while respecting difficulty.
3. Decide how many answer choices / how much support to show (scaffolding).

It is deterministic given a seed, which makes it unit-testable.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

from .. import config
from .content import ContentItem, ContentLibrary
from .database import Database
from .progress import ProgressTracker


@dataclass
class StageState:
    difficulty: float
    streak: int


class AdaptiveEngine:
    def __init__(
        self,
        db: Database,
        content: ContentLibrary,
        progress: ProgressTracker,
        rng: Optional[random.Random] = None,
    ):
        self.db = db
        self.content = content
        self.progress = progress
        self.rng = rng or random.Random()

    # ------------------------------------------------------------------ #
    # Difficulty state
    # ------------------------------------------------------------------ #
    def state(self, profile_id: int, stage: int) -> StageState:
        row = self.db.query_one(
            "SELECT difficulty, streak FROM stage_state WHERE profile_id=? AND stage=?",
            (profile_id, stage),
        )
        if row is None:
            return StageState(difficulty=config.ADAPTIVE_MIN, streak=0)
        return StageState(difficulty=row["difficulty"] or 0.0, streak=row["streak"] or 0)

    def _save_state(self, profile_id: int, stage: int, st: StageState) -> None:
        with self.db.tx() as c:
            c.execute(
                "INSERT INTO stage_state(profile_id, stage, difficulty, streak, unlocked) "
                "VALUES (?,?,?,?,COALESCE((SELECT unlocked FROM stage_state "
                "   WHERE profile_id=? AND stage=?), ?)) "
                "ON CONFLICT(profile_id, stage) DO UPDATE SET difficulty=?, streak=?",
                (
                    profile_id, stage, st.difficulty, st.streak,
                    profile_id, stage, 1 if stage == 1 else 0,
                    st.difficulty, st.streak,
                ),
            )

    def register_result(self, profile_id: int, stage: int, correct: bool) -> StageState:
        """Update difficulty/streak after an answer and return the new state."""
        st = self.state(profile_id, stage)
        if correct:
            st.streak += 1
            if st.streak >= config.ADAPTIVE_STREAK_UP:
                st.difficulty = min(
                    config.ADAPTIVE_MAX, st.difficulty + config.ADAPTIVE_STEP_UP
                )
                st.streak = 0
        else:
            st.streak = 0
            st.difficulty = max(
                config.ADAPTIVE_MIN, st.difficulty - config.ADAPTIVE_STEP_DOWN
            )
        self._save_state(profile_id, stage, st)
        return st

    # ------------------------------------------------------------------ #
    # Item selection (spaced practice)
    # ------------------------------------------------------------------ #
    def next_item(
        self, profile_id: int, stage: int, exclude: Optional[str] = None
    ) -> Optional[ContentItem]:
        items = self.content.items(stage)
        if not items:
            return None
        mastery = self.progress.item_mastery(profile_id, stage)

        candidates = [it for it in items if it.id != exclude] or items

        def weight(it: ContentItem) -> float:
            m = mastery.get(it.id, 0)
            # Unseen items are most attractive; mastered items least.
            base = (config.MASTERY_THRESHOLD - m) + 1.0
            # A little jitter so order isn't identical each pass.
            return base

        weights = [weight(it) for it in candidates]
        return self.rng.choices(candidates, weights=weights, k=1)[0]

    def session_plan(
        self, profile_id: int, stage: int, length: int = config.DAILY_GOAL_ACTIVITIES
    ) -> List[ContentItem]:
        """Build a short, varied practice set, front-loading weak items."""
        plan: List[ContentItem] = []
        last: Optional[str] = None
        for _ in range(length):
            it = self.next_item(profile_id, stage, exclude=last)
            if it is None:
                break
            plan.append(it)
            last = it.id
        return plan

    # ------------------------------------------------------------------ #
    # Scaffolding
    # ------------------------------------------------------------------ #
    def num_choices(self, profile_id: int, stage: int) -> int:
        """How many answer options to show. Easier = fewer choices."""
        d = self.state(profile_id, stage).difficulty
        if d < 0.34:
            return 2
        if d < 0.67:
            return 3
        return 4

    def show_hint(self, profile_id: int, stage: int) -> bool:
        """Whether to show extra visual/audio scaffolding for this item."""
        return self.state(profile_id, stage).difficulty < 0.5

    def distractors(
        self, target: ContentItem, pool: List[ContentItem], count: int
    ) -> List[ContentItem]:
        """Pick ``count`` wrong-answer options that are not the target."""
        others = [it for it in pool if it.id != target.id]
        self.rng.shuffle(others)
        return others[:count]
