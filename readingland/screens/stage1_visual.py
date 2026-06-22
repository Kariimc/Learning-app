"""Stage 1 - Look & Learn (visual recognition, ages 2-3).

Fully narrated picture matching: shapes, colors, animals, objects. The tile is
the picture (emoji) itself; the child matches by sight + sound, no reading.
"""
from .. import config
from ..core.content import ContentItem
from ._matching import MatchingStageScreen


class Stage1Screen(MatchingStageScreen):
    STAGE = 1
    GUIDE = "reading_rabbit"
    ACCENT = config.PALETTE["mint"]

    def prompt_text(self, item: ContentItem) -> str:
        cat = item.data.get("category", "thing")
        verbs = {
            "shape": f"Find the {item.label}!",
            "color": f"Find {item.label}!",
            "animal": f"Where is the {item.label}?",
            "object": f"Tap the {item.label}!",
        }
        return verbs.get(cat, f"Find the {item.label}!")

    def tile_glyph(self, item: ContentItem) -> str:
        # Pre-readers see the picture, not text.
        return item.emoji or "●"

    def tile_emoji(self, item: ContentItem) -> str:
        return ""
