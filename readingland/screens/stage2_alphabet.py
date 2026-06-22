"""Stage 2 - Letter Land (alphabet mastery).

The child hears a letter name + sound + example word and finds the matching
letter. Tiles show the big uppercase letter with the example-word emoji beneath.
"""
from .. import config
from ..core.content import ContentItem
from ._matching import MatchingStageScreen


class Stage2Screen(MatchingStageScreen):
    STAGE = 2
    GUIDE = "reading_rabbit"
    ACCENT = config.PALETTE["tangerine"]
    bg_image_key = "alphabet"

    def prompt_text(self, item: ContentItem) -> str:
        sound = item.data.get("sound", "")
        word = item.data.get("word", "")
        # "Find the letter A. A is for Apple. Ah!"
        return f"Find {item.label}!  {item.label} is for {word}."

    def tile_glyph(self, item: ContentItem) -> str:
        return item.label  # uppercase letter

    def tile_emoji(self, item: ContentItem) -> str:
        return item.emoji
