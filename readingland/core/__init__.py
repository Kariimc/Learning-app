"""Pure-Python engine for ReadingLand.

Nothing in this sub-package may import Kivy. That guarantee lets the whole
learning brain - persistence, curriculum, progress, adaptive difficulty and
rewards - run and be unit-tested in a headless CI environment.
"""
from .content import ContentLibrary
from .database import Database
from .profiles import ProfileManager
from .progress import ProgressTracker
from .adaptive import AdaptiveEngine
from .rewards import RewardSystem

__all__ = [
    "ContentLibrary",
    "Database",
    "ProfileManager",
    "ProgressTracker",
    "AdaptiveEngine",
    "RewardSystem",
]
