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


# Content emoji -> plush cutout slug. Mirrors the map the owner defined in
# prototypes/readingland-flow.html so the app and prototype stay in sync.
_EMOJI_ICON = {
    "\U0001F534": "circle", "\U0001F7E6": "square", "\U0001F53A": "triangle",
    "⭐": "star", "❤️": "heart",
    "\U0001F436": "dog", "\U0001F431": "cat", "\U0001F41F": "fish",
    "\U0001F426": "bird", "⚽": "ball", "\U0001F34E": "apple",
    "\U0001F697": "car", "\U0001F95A": "egg", "\U0001F410": "goat",
    "\U0001F3A9": "hat",
}


def content_icon(item_id: Optional[str] = None, emoji: Optional[str] = None) -> Optional[str]:
    """Plush cutout art for a content item, or ``None`` to fall back to emoji.

    Resolves by the item id (``cards/icon_<id>.png``) first, then by the item's
    emoji via the shared emoji->slug map. These are the real generated cutouts
    already committed under ``assets/images/cards/`` - no new art needed.
    """
    base = os.path.join(config.ASSETS_DIR, "images", "cards")
    cands = []
    if item_id:
        cands += [os.path.join(base, f"icon_{item_id}" + ext) for ext in _IMAGE_EXTS]
    if emoji:
        slug = _EMOJI_ICON.get(emoji)
        if slug:
            cands += [os.path.join(base, f"icon_{slug}" + ext) for ext in _IMAGE_EXTS]
    return _first_existing(*cands)
