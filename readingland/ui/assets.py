"""Asset path resolution.

Centralises where on-disk art lives so widgets can opt into real art when it's
present and fall back to programmatic placeholders when it isn't. Lookups follow
the conventions documented in ``docs/06_asset_list.md`` and ``assets/README.md``.
"""
from __future__ import annotations

import os
from typing import Optional

from .. import config

_IMAGE_EXTS = (".png", ".webp", ".jpg", ".jpeg")


def _first_existing(*paths: str) -> Optional[str]:
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def character_image(char_id: str) -> Optional[str]:
    """Portrait/idle art for a mascot: assets/images/characters/<id>/portrait.*"""
    base = os.path.join(config.ASSETS_DIR, "images", "characters", char_id)
    candidates = [os.path.join(base, "portrait" + ext) for ext in _IMAGE_EXTS]
    candidates += [os.path.join(base, "idle" + ext) for ext in _IMAGE_EXTS]
    return _first_existing(*candidates)


def background_image(stage_key: str) -> Optional[str]:
    base = os.path.join(config.ASSETS_DIR, "images", "backgrounds")
    candidates = [os.path.join(base, f"bg_{stage_key}" + ext) for ext in _IMAGE_EXTS]
    return _first_existing(*candidates)


def card_image(item_id: str) -> Optional[str]:
    base = os.path.join(config.ASSETS_DIR, "images", "cards")
    return _first_existing(*[os.path.join(base, item_id + ext) for ext in _IMAGE_EXTS])


def ui_image(name: str) -> Optional[str]:
    base = os.path.join(config.ASSETS_DIR, "images", "ui")
    return _first_existing(*[os.path.join(base, name + ext) for ext in _IMAGE_EXTS])


_FELT_CACHE: dict = {}


def felt_texture(kind: str = "button") -> str:
    """Path to the tintable plush-felt texture for a rounded surface, or "".

    ``kind="button"`` -> wide pillow texture; anything else -> square panel.
    Buttons draw this on their ``RoundedRectangle`` so Kivy multiplies the felt
    shading by the widget's ``bg_color``, turning any colour into stuffed felt.
    Returns "" (falsy) when the art hasn't been generated, so callers keep their
    flat-colour fallback. Cached: the lookup runs once per kind.
    """
    if kind not in _FELT_CACHE:
        name = "felt_button" if kind == "button" else "felt_panel"
        _FELT_CACHE[kind] = ui_image(name) or ""
    return _FELT_CACHE[kind]
