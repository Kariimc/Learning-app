"""Theme helpers: fonts, sizing in dp, and emoji support detection.

Real shipping art replaces the programmatic placeholders, but the *theme* (the
palette in ``config.PALETTE``, the type scale here) stays constant so swapping
art never changes layout.
"""
from __future__ import annotations

import glob
import os

from kivy.core.text import LabelBase
from kivy.metrics import dp

from .. import config

# Re-export palette for convenience.
PALETTE = config.PALETTE

# Rounded, friendly type scale (in sp via dp helper at call sites).
FONT_DISPLAY = 96     # giant letters / words
FONT_TITLE = 40
FONT_HEADING = 30
FONT_BODY = 22
FONT_LABEL = 18

_EMOJI_FONT_REGISTERED = False
EMOJI_FONT_NAME = "Emoji"


def register_fonts() -> bool:
    """Try to register a colour-emoji font. Returns True if one was found.

    Children's content leans on emoji as quick placeholder art. If the platform
    ships an emoji font we register it; otherwise the UI falls back to coloured
    shapes + big text, which still teaches the concept.
    """
    global _EMOJI_FONT_REGISTERED
    if _EMOJI_FONT_REGISTERED:
        return True
    win = os.environ.get("WINDIR", r"C:\Windows")
    candidates = [
        # Bundled with the app (most reliable across platforms) - drop a
        # colour-emoji .ttf here to guarantee consistent rendering everywhere.
        os.path.join(config.ASSETS_DIR, "fonts", "NotoColorEmoji.ttf"),
        os.path.join(config.ASSETS_DIR, "fonts", "emoji.ttf"),
        # Windows (Segoe UI Emoji) - fixes the "tofu box" glyphs on stock PCs.
        os.path.join(win, "Fonts", "seguiemj.ttf"),
        # macOS.
        "/System/Library/Fonts/Apple Color Emoji.ttc",
        # Linux.
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/truetype/noto/NotoEmoji-Regular.ttf",
        "/usr/share/fonts/google-noto-emoji/NotoColorEmoji.ttf",
    ]
    candidates += glob.glob(os.path.join(config.ASSETS_DIR, "fonts", "*Emoji*.ttf"))
    candidates += glob.glob("/usr/share/fonts/**/NotoColorEmoji.ttf", recursive=True)
    candidates += glob.glob("/usr/share/fonts/**/*Emoji*.ttf", recursive=True)
    for path in candidates:
        if os.path.exists(path):
            try:
                LabelBase.register(name=EMOJI_FONT_NAME, fn_regular=path)
                _EMOJI_FONT_REGISTERED = True
                return True
            except Exception:
                continue
    return False


def touch_size() -> float:
    """Minimum comfortable touch target for small hands."""
    return dp(config.MIN_TOUCH_TARGET_DP)
