"""Theme helpers: fonts, sizing in dp, and emoji support detection."""
from __future__ import annotations

import glob
import os

from kivy.core.text import LabelBase
from kivy.metrics import dp

from .. import config

PALETTE = config.PALETTE

# Bigger, bolder type scale — rounded display font feels friendly at these sizes.
FONT_DISPLAY = 108
FONT_TITLE   = 48
FONT_HEADING  = 36
FONT_BODY     = 28
FONT_LABEL    = 22

FONT_MAIN = "Fredoka"   # fun round kids font; falls back to Roboto if absent

_EMOJI_FONT_REGISTERED = False
_MAIN_FONT_REGISTERED  = False
EMOJI_FONT_NAME = "Emoji"


def register_main_font() -> bool:
    """Register a rounded, toddler-friendly display font and set it as default.

    Looks for Fredoka-Bold.ttf in assets/fonts (downloaded by fetch_assets.py).
    If missing, Kivy's built-in Roboto stays in place — the app still runs fine.
    """
    global _MAIN_FONT_REGISTERED
    if _MAIN_FONT_REGISTERED:
        return True
    candidates = [
        os.path.join(config.ASSETS_DIR, "fonts", "Fredoka-Bold.ttf"),
        os.path.join(config.ASSETS_DIR, "fonts", "Nunito-ExtraBold.ttf"),
        os.path.join(config.ASSETS_DIR, "fonts", "Nunito-Bold.ttf"),
    ]
    candidates += glob.glob(os.path.join(config.ASSETS_DIR, "fonts", "Fredoka*.ttf"))
    candidates += glob.glob(os.path.join(config.ASSETS_DIR, "fonts", "Nunito*.ttf"))
    for path in candidates:
        if os.path.exists(path):
            try:
                LabelBase.register(name=FONT_MAIN, fn_regular=path)
                # Also register as default so un-named Labels pick it up.
                LabelBase.register(name="Roboto", fn_regular=path)
                _MAIN_FONT_REGISTERED = True
                return True
            except Exception:
                continue
    return False


def register_fonts() -> bool:
    """Try to register a colour-emoji font. Returns True if one was found."""
    global _EMOJI_FONT_REGISTERED
    if _EMOJI_FONT_REGISTERED:
        return True
    win = os.environ.get("WINDIR", r"C:\Windows")
    candidates = [
        os.path.join(config.ASSETS_DIR, "fonts", "NotoColorEmoji.ttf"),
        os.path.join(config.ASSETS_DIR, "fonts", "emoji.ttf"),
        os.path.join(win, "Fonts", "seguiemj.ttf"),
        "/System/Library/Fonts/Apple Color Emoji.ttc",
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
    return dp(config.MIN_TOUCH_TARGET_DP)
