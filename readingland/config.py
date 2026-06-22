"""Global configuration: theme palette, stage definitions and tunables.

This module is pure data and constants. It is imported by both the core engine
and the UI layer, so it must never import Kivy.
"""
from __future__ import annotations

import os

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(PACKAGE_DIR, "content")
PROJECT_ROOT = os.path.dirname(PACKAGE_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

# Database lives in the OS-appropriate user data dir at runtime; this is the
# fallback used by headless tests.
DEFAULT_DB_NAME = "readingland.db"

# --------------------------------------------------------------------------- #
# Brand palette - bright, warm, high-contrast and accessibility-checked.
# Colours are RGBA tuples in 0..1 so they drop straight into Kivy graphics.
# --------------------------------------------------------------------------- #
def hex_rgba(value: str, alpha: float = 1.0):
    """Convert ``#RRGGBB`` to an RGBA float tuple."""
    value = value.lstrip("#")
    r, g, b = (int(value[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (r, g, b, alpha)


PALETTE = {
    "sky":        hex_rgba("#5DC1F0"),   # primary background
    "sky_deep":   hex_rgba("#2E9BD6"),
    "sun":        hex_rgba("#FFD23F"),   # rewards / stars
    "coral":      hex_rgba("#FF6B6B"),   # warm accent / wrong-but-gentle
    "mint":       hex_rgba("#3DDC97"),   # correct / go
    "grape":      hex_rgba("#9B5DE5"),   # phonics
    "bubblegum":  hex_rgba("#FF8FB1"),
    "tangerine":  hex_rgba("#FF9F1C"),
    "cream":      hex_rgba("#FFF6E9"),   # card surfaces / text on dark
    "ink":        hex_rgba("#2B2D42"),   # text on light
    "leaf":       hex_rgba("#7AC74F"),
    "white":      hex_rgba("#FFFFFF"),
    "shadow":     hex_rgba("#000000", 0.18),
}

# Per-stage accent colour, keeps each "land" visually distinct.
STAGE_COLORS = {
    1: PALETTE["mint"],
    2: PALETTE["tangerine"],
    3: PALETTE["grape"],
    4: PALETTE["coral"],
    5: PALETTE["sky_deep"],
    6: PALETTE["bubblegum"],
}

# --------------------------------------------------------------------------- #
# Stages - the spine of the curriculum. Order matters; index == unlock order.
# --------------------------------------------------------------------------- #
STAGES = [
    {
        "id": 1,
        "key": "visual",
        "title": "Look & Learn",
        "subtitle": "Shapes, colors, animals & objects",
        "age": "2-3",
        "screen": "stage1",
        "content": "stage1_visual.json",
        "icon": "shapes",
        "guide": "reading_rabbit",
    },
    {
        "id": 2,
        "key": "alphabet",
        "title": "Letter Land",
        "subtitle": "Letter names & sounds",
        "age": "3-4",
        "screen": "stage2",
        "content": "alphabet.json",
        "icon": "abc",
        "guide": "reading_rabbit",
    },
    {
        "id": 3,
        "key": "phonics",
        "title": "Sound Forest",
        "subtitle": "Blending sounds into words",
        "age": "4-5",
        "screen": "stage3",
        "content": "phonics.json",
        "icon": "blend",
        "guide": "benny_bear",
    },
    {
        "id": 4,
        "key": "words",
        "title": "Word Town",
        "subtitle": "Reading first words",
        "age": "4-6",
        "screen": "stage4",
        "content": "words.json",
        "icon": "word",
        "guide": "penny_penguin",
    },
    {
        "id": 5,
        "key": "sentences",
        "title": "Sentence River",
        "subtitle": "Reading sentences",
        "age": "5-7",
        "screen": "stage5",
        "content": "sentences.json",
        "icon": "sentence",
        "guide": "penny_penguin",
    },
    {
        "id": 6,
        "key": "stories",
        "title": "Story Sky",
        "subtitle": "Read-along storybooks",
        "age": "5-8",
        "screen": "stage6",
        "content": "stories.json",
        "icon": "book",
        "guide": "ollie_owl",
    },
]

STAGE_BY_ID = {s["id"]: s for s in STAGES}

# --------------------------------------------------------------------------- #
# Learning / gamification tunables
# --------------------------------------------------------------------------- #
# Number of correct answers (mastery score) needed to "master" an item.
MASTERY_THRESHOLD = 3
# A stage unlocks when this fraction of the previous stage's items is mastered.
STAGE_UNLOCK_RATIO = 0.7
# Stars awarded per perfect (first-try) answer.
STARS_PER_PERFECT = 3
STARS_PER_CORRECT = 1
# Daily goal: activities to complete for the daily-reward chest.
DAILY_GOAL_ACTIVITIES = 5

# Adaptive engine bounds. Difficulty is a float 0..1.
ADAPTIVE_MIN = 0.0
ADAPTIVE_MAX = 1.0
ADAPTIVE_STEP_UP = 0.12     # raise difficulty after a streak of correct
ADAPTIVE_STEP_DOWN = 0.18   # lower difficulty (more support) after misses
ADAPTIVE_STREAK_UP = 3      # correct-in-a-row needed to step up

# Accessibility / UX
MIN_TOUCH_TARGET_DP = 88    # generous tap targets for tiny hands
NARRATION_REPEAT_DELAY = 0.4

# Audio
TTS_RATE = 150              # words per minute for fallback TTS
PREFER_RECORDED_AUDIO = True
