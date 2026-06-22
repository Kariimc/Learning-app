"""Recorded narrator ("fairy godmother", Mabel) voice-line manifest.

Universal lines (praise, retry, greetings) plus per-content voice keys for
the 26 letters and the Stage 4 words. All keys map to
``assets/audio/voice/mabel/<key>.mp3``; the app falls back to TTS when absent.
"""
from __future__ import annotations

import re
from typing import Dict


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return s[:40] or "line"


# Praise (correct) and gentle retry pools.
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
    "greet_home":    "Hello my dear! Which land shall we explore today?",
    "greet_story":   "Hello little one! Pick a story and we will read it together.",
    "locked_stage":  "Let's finish this land first, then we'll open the next one!",
    "locked_tracing": "Let's learn some letters first, then we can trace them together!",
    "finish_book":   "The end! What a wonderful reader you are!",
    "retry_listen":  "Good try! Let's listen again.",
    "retry_sound":   "Good try! Let's sound it out again.",
    "retry_read":    "Good try! Let's read it again.",
}

# Per-letter narrations (key: letter_a … letter_z).
# Text is spoken when no recording is present; recording uses the same text.
LETTER_LINES: Dict[str, str] = {
    "letter_a": "A. Ah. Apple.",
    "letter_b": "B. Buh. Ball.",
    "letter_c": "C. Kuh. Cat.",
    "letter_d": "D. Duh. Dog.",
    "letter_e": "E. Eh. Egg.",
    "letter_f": "F. Fff. Fish.",
    "letter_g": "G. Guh. Goat.",
    "letter_h": "H. Huh. Hat.",
    "letter_i": "I. Ih. Igloo.",
    "letter_j": "J. Juh. Jam.",
    "letter_k": "K. Kuh. Kite.",
    "letter_l": "L. Lll. Lion.",
    "letter_m": "M. Mmm. Moon.",
    "letter_n": "N. Nnn. Nest.",
    "letter_o": "O. Oh. Orange.",
    "letter_p": "P. Puh. Pig.",
    "letter_q": "Q. Kwuh. Queen.",
    "letter_r": "R. Rrr. Rabbit.",
    "letter_s": "S. Sss. Sun.",
    "letter_t": "T. Tuh. Tree.",
    "letter_u": "U. Uh. Umbrella.",
    "letter_v": "V. Vvv. Van.",
    "letter_w": "W. Wuh. Whale.",
    "letter_x": "X. Ks. Fox.",
    "letter_y": "Y. Yuh. Yo-yo.",
    "letter_z": "Z. Zzz. Zebra.",
}

# Per-word narrations (key == item id from words.json — already lowercase).
WORD_LINES: Dict[str, str] = {
    "cat": "cat", "dog": "dog", "sun": "sun", "ball": "ball",
    "fish": "fish", "tree": "tree", "star": "star", "bird": "bird",
    "run": "run", "jump": "jump", "fly": "fly", "look": "look",
    "play": "play", "the": "the", "is": "is", "a": "a",
    "can": "can", "see": "see", "go": "go", "happy": "happy",
}


def key_for(text: str) -> str:
    """Stable voice key for a praise/retry phrase."""
    return "ln_" + slugify(text)


def all_lines() -> Dict[str, str]:
    """Every recorded line: key -> text (used by generation tooling + tests)."""
    lines: Dict[str, str] = dict(NAV_LINES)
    for text in ENCOURAGE_CORRECT + ENCOURAGE_RETRY:
        lines[key_for(text)] = text
    lines.update(LETTER_LINES)
    lines.update(WORD_LINES)
    return lines
