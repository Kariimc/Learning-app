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

# Assets the shipping app cannot boot without - the real generated art + Mabel
# voice pack. If any is missing or is an LFS pointer stub, verify_assets()
# raises so the app never starts in the placeholder look.
_REQUIRED_ASSETS = (
    ("images", "backgrounds", "bg_map.png"),
    ("images", "backgrounds", "bg_visual.png"),
    ("images", "backgrounds", "bg_alphabet.png"),
    ("images", "backgrounds", "bg_phonics.png"),
    ("images", "backgrounds", "bg_words.png"),
    ("images", "backgrounds", "bg_sentences.png"),
    ("images", "backgrounds", "bg_stories.png"),
    ("images", "characters", "reading_rabbit", "portrait.png"),
    ("images", "characters", "benny_bear", "portrait.png"),
    ("images", "characters", "penny_penguin", "portrait.png"),
    ("images", "characters", "ollie_owl", "portrait.png"),
    ("images", "characters", "milo_monkey", "portrait.png"),
    ("fonts", "Fredoka-Bold.ttf"),
    ("audio", "voice", "mabel", "greet_home.mp3"),
)

_ASSET_EXTS = (".png", ".webp", ".jpg", ".jpeg", ".mp3", ".wav", ".ogg", ".ttf")


def verify_assets(assets_dir: str = None) -> None:
    """Fail fast if the real generated assets aren't fully on disk.

    Checks 1) every required asset exists, and 2) no asset file anywhere in the
    tree is a Git-LFS pointer stub. Called at app start so a broken checkout
    (LFS objects not pulled) can never boot into placeholders/TTS.
    """
    base = assets_dir or config.ASSETS_DIR
    missing = [os.path.join(*parts) for parts in _REQUIRED_ASSETS
               if not os.path.isfile(os.path.join(base, *parts))]
    stubs = []
    for root, _dirs, files in os.walk(base):
        for name in files:
            if name.lower().endswith(_ASSET_EXTS):
                p = os.path.join(root, name)
                if config.is_lfs_pointer(p):
                    stubs.append(os.path.relpath(p, base))
    if missing or stubs:
        raise RuntimeError(
            "ReadingLand refuses to start without its real generated assets "
            "(no placeholder fallback). Run `git lfs install && git lfs pull` "
            "or `python scripts/fetch_assets.py`.\n"
            + ("Missing: %s\n" % ", ".join(sorted(missing)) if missing else "")
            + ("LFS pointer stubs: %s" % ", ".join(sorted(stubs)) if stubs else "")
        )


def _first_existing(*paths: str) -> Optional[str]:
    for p in paths:
        # asset_file_exists rejects (and, in shipping config, raises on)
        # Git-LFS pointer stubs so a broken checkout can't silently fall
        # back to placeholder art.
        if p and config.asset_file_exists(p):
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
        # Content ids carry a category prefix (shape_circle, animal_dog...);
        # the cutouts are stored by bare name (icon_circle, icon_dog...).
        if "_" in item_id:
            suffix = item_id.split("_", 1)[1]
            cands += [os.path.join(base, f"icon_{suffix}" + ext) for ext in _IMAGE_EXTS]
    if emoji:
        slug = _EMOJI_ICON.get(emoji)
        if slug:
            cands += [os.path.join(base, f"icon_{slug}" + ext) for ext in _IMAGE_EXTS]
    return _first_existing(*cands)
