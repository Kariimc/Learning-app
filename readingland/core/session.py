"""LearningSession - the single facade the UI talks to.

Holds the active profile and composes the engine pieces so a screen only needs
to call ``session.answer(...)`` and react to one tidy result object. This keeps
Kivy screens thin and the learning logic centralised and testable.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import List, Optional

from .. import config
from .adaptive import AdaptiveEngine
from .analytics import Analytics
from .content import ContentItem, ContentLibrary
from .database import Database
from .progress import AnswerResult, ProgressTracker
from .profiles import Profile, ProfileManager
from .rewards import RewardGrant, RewardSystem


@dataclass
class TurnOutcome:
    """Everything a screen needs to render feedback after one answer."""

    result: AnswerResult
    new_rewards: List[RewardGrant] = field(default_factory=list)
    difficulty: float = 0.0
    celebrate: bool = False           # big celebration vs gentle nudge
    encouragement: str = ""           # narrator line to speak


ENCOURAGE_CORRECT = [
    "Great job!", "Fantastic reading!", "You did it!", "Wonderful!",
    "Super star!", "You found it!", "Brilliant!",
]
ENCOURAGE_RETRY = [
    "Good try! Let's try again.", "Almost! Try once more.",
    "Nice try! Listen again.", "Let's find it together.",
]


class LearningSession:
    def __init__(self, db: Database, content: ContentLibrary,
                 rng: Optional[random.Random] = None):
        self.db = db
        self.content = content
        self.rng = rng or random.Random()
        self.profiles = ProfileManager(db)
        self.progress = ProgressTracker(db, content)
        self.adaptive = AdaptiveEngine(db, content, self.progress, self.rng)
        self.rewards = RewardSystem(db, self.progress)
        self.analytics = Analytics(db, content, self.progress)
        self.profile: Optional[Profile] = None
        self._session_start: Optional[float] = None

    # ------------------------------------------------------------------ #
    # Profile lifecycle
    # ------------------------------------------------------------------ #
    def set_profile(self, profile_id: int) -> Optional[Profile]:
        self.profile = self.profiles.get(profile_id)
        if self.profile:
            self.profiles.touch(profile_id)
            self._session_start = time.time()
        return self.profile

    def end_session(self) -> None:
        if self.profile and self._session_start:
            seconds = time.time() - self._session_start
            self.db.log_event(self.profile.id, "session", payload=str(round(seconds)))
            self._session_start = None

    @property
    def pid(self) -> int:
        if not self.profile:
            raise RuntimeError("No active profile - call set_profile() first")
        return self.profile.id

    # ------------------------------------------------------------------ #
    # Core gameplay
    # ------------------------------------------------------------------ #
    def next_item(self, stage: int, exclude: Optional[str] = None) -> Optional[ContentItem]:
        return self.adaptive.next_item(self.pid, stage, exclude)

    def build_choices(self, stage: int, target: ContentItem) -> List[ContentItem]:
        """Target + adaptive number of distractors, shuffled."""
        n = self.adaptive.num_choices(self.pid, stage)
        distractors = self.adaptive.distractors(
            target, self.content.items(stage), n - 1
        )
        choices = [target, *distractors]
        self.rng.shuffle(choices)
        return choices

    def answer(self, stage: int, item: ContentItem, correct: bool) -> TurnOutcome:
        """Record one answer and return everything needed for feedback."""
        result = self.progress.record_answer(self.pid, stage, item.id, correct)
        st = self.adaptive.register_result(self.pid, stage, correct)
        new_rewards: List[RewardGrant] = []
        if correct:
            new_rewards = self.rewards.evaluate_milestones(self.pid)
            # A mastered item earns a sticker from the catalogue.
            if result.mastered_now:
                sticker_id = self._sticker_for_item(item)
                g = self.rewards.grant_sticker(self.pid, sticker_id)
                if g.is_new:
                    new_rewards.append(g)

        encouragement = (
            self.rng.choice(ENCOURAGE_CORRECT) if correct
            else self.rng.choice(ENCOURAGE_RETRY)
        )
        return TurnOutcome(
            result=result,
            new_rewards=new_rewards,
            difficulty=st.difficulty,
            celebrate=correct and (result.mastered_now or result.stage_unlocked is not None),
            encouragement=encouragement,
        )

    def _sticker_for_item(self, item: ContentItem) -> str:
        # Map some content to themed stickers, else rotate the catalogue.
        from .rewards import STICKERS
        themed = {"apple": "happy_apple", "cat": "brave_cat", "dog": "good_dog"}
        key = item.label.lower()
        if key in themed:
            return themed[key]
        ids = list(STICKERS.keys())
        return ids[hash(item.id) % len(ids)]

    # ------------------------------------------------------------------ #
    # Convenience for screens
    # ------------------------------------------------------------------ #
    def stage_summary(self, stage: int):
        return self.progress.stage_summary(self.pid, stage)

    def stars(self) -> int:
        return self.progress.stars(self.pid)

    def daily_goal(self) -> dict:
        return self.rewards.daily_goal_progress(self.pid)
