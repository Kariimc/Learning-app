"""Stage 4 - Word Town (first word reading).

The mascot shows a picture and asks the child to find the matching *word*. Tiles
show the word text (with a faint emoji) so the child links spelling to meaning.
"""
from .. import config
from ..core.content import ContentItem
from ._matching import MatchingStageScreen


class Stage4Screen(MatchingStageScreen):
    STAGE = 4
    GUIDE = "penny_penguin"
    ACCENT = config.PALETTE["coral"]

    def prompt_text(self, item: ContentItem) -> str:
        if item.data.get("kind") == "sight":
            return f"Find the word \"{item.label}\"."
        return f"{item.emoji}  Which word says \"{item.label}\"?"

    def tile_glyph(self, item: ContentItem) -> str:
        return item.label  # the word itself

    def tile_emoji(self, item: ContentItem) -> str:
        # Sight words have no picture; nouns/verbs show a small hint emoji.
        return "" if item.data.get("kind") == "sight" else item.emoji
