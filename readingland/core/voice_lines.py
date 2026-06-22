"""Recorded narrator ("fairy godmother", Mabel) voice-line manifest.

These are the *universal* spoken lines heard across every stage - praise,
gentle retries, greetings and celebrations. Each has a stable key; the recorded
``assets/audio/voice/mabel/<key>.ogg`` is played when present, otherwise the
TTS fallback speaks the same text. ``scripts/fetch_assets.py`` downloads the
recordings, and this same manifest drives their generation.

Per-content narration (individual letters/words/story lines) currently uses the
warm TTS fallback; those packs can be added later by extending this manifest.
"""
from __future__ import annotations

import re
from typing import Dict


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return s[:40] or "line"


# Praise (correct) and gentle retry pools. Source of truth for session.py too.
ENCOURAGE_CORRECT = [
    "Great job!", "Fantastic reading!", "You did it!", "Wonderful!",
    "Super star!", "You found it!", "Brilliant!",
]
ENCOURAGE_RETRY = [
    "Good try! Let's try again.", "Almost! Try once more.",
    "Nice try! Listen again.", "Let's find it together.",
]

# Fixed greeting / navigation / celebration lines, keyed explicitly.
NAV_LINES: Dict[str, str] = {
    "greet_home": "Hello my dear! Which land shall we explore today?",
    "greet_story": "Hello little one! Pick a story and we will read it together.",
    "locked_stage": "Let's finish this land first, then we'll open the next one!",
    "locked_tracing": "Let's learn some letters first, then we can trace them together!",
    "finish_book": "The end! What a wonderful reader you are!",
    "retry_listen": "Good try! Let's listen again.",
    "retry_sound": "Good try! Let's sound it out again.",
    "retry_read": "Good try! Let's read it again.",
}


def key_for(text: str) -> str:
    """Stable voice key for a praise/retry phrase."""
    return "ln_" + slugify(text)


def all_lines() -> Dict[str, str]:
    """Every recorded line: key -> text (used by the generation tooling)."""
    lines: Dict[str, str] = dict(NAV_LINES)
    for text in ENCOURAGE_CORRECT + ENCOURAGE_RETRY:
        lines[key_for(text)] = text
    return lines
