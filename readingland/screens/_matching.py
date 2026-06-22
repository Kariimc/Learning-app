"""Shared 'find / match' activity used by Stages 1, 2 and 4.

Flow: a mascot poses a prompt ("Find the letter A!"), the child taps among a row
of big tiles. Correct -> celebrate + advance. Wrong -> gentle nudge, narrate
again, let them keep trying (never punished, never blocked).

Subclasses customise only:
  * ``STAGE`` / ``GUIDE`` / ``ACCENT``
  * ``prompt_text(item)``        - what the mascot asks
  * ``tile_glyph(item)``         - big glyph on each tile
  * ``tile_emoji(item)``         - small emoji on each tile
"""
from __future__ import annotations

from typing import List, Optional

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from .. import config
from ..core.content import ContentItem
from ..core.voice_lines import NAV_LINES
from ..ui import particles, theme
from ..ui.icons import IconButton
from ..ui.widgets import ChunkyProgressBar, GlyphTile, Mascot
from .base import BaseScreen, app


class MatchingStageScreen(BaseScreen):
    STAGE = 1
    GUIDE = "reading_rabbit"
    ACCENT = config.PALETTE["mint"]

    def __init__(self, **kwargs):
        self._target: Optional[ContentItem] = None
        self._choices: List[ContentItem] = []
        self._locked = False
        super().__init__(**kwargs)

    # ------------------------------------------------------------------ #
    @property
    def title(self):
        return config.STAGE_BY_ID[self.STAGE]["title"]

    def build(self):
        self.bg_top = config.PALETTE["sky"]
        # Mascot guide.
        char = app().content.character(self.GUIDE) if app() else {"id": self.GUIDE}
        self.mascot = Mascot(char=char, size_hint=(None, None),
                             size=(dp(150), dp(180)), pos_hint={"x": 0.04, "y": 0.36})
        self.content.add_widget(self.mascot)

        # Prompt bubble.
        self.prompt_lbl = Label(
            text="", font_size=theme.FONT_TITLE, bold=True,
            color=config.PALETTE["ink"], size_hint=(0.7, None), height=dp(120),
            pos_hint={"x": 0.28, "top": 0.92}, halign="center", valign="middle",
        )
        self.prompt_lbl.bind(size=lambda *_: setattr(self.prompt_lbl, "text_size", self.prompt_lbl.size))
        self.content.add_widget(self.prompt_lbl)

        # Replay button (hear it again).
        self.replay = IconButton(icon="speaker", on_tap=lambda *_: self._speak_target(),
                                 size_hint=(None, None), size=(dp(80), dp(80)),
                                 pos_hint={"right": 0.97, "top": 0.92},
                                 bg_color=list(config.PALETTE["sun"]),
                                 icon_color=list(config.PALETTE["ink"]))
        self.content.add_widget(self.replay)

        # Choice row.
        self.choice_row = GridLayout(
            rows=1, spacing=dp(16), size_hint=(0.92, 0.4),
            pos_hint={"center_x": 0.5, "y": 0.16}, padding=dp(8),
        )
        self.content.add_widget(self.choice_row)

        # Progress bar.
        self.progress = ChunkyProgressBar(
            size_hint=(0.9, None), height=dp(24),
            pos_hint={"center_x": 0.5, "y": 0.05},
        )
        self.progress.bar_color = list(self.ACCENT)
        self.content.add_widget(self.progress)

    # ------------------------------------------------------------------ #
    def refresh(self):
        if not app() or not app().session.profile:
            return
        self.mascot.idle()
        self._update_progress()
        self._next_round()

    def _update_progress(self):
        summ = app().session.stage_summary(self.STAGE)
        self.progress.value = summ.ratio

    # ------------------------------------------------------------------ #
    def _next_round(self):
        self._locked = False
        session = app().session
        self._target = session.next_item(self.STAGE, exclude=self._target.id if self._target else None)
        if self._target is None:
            return
        self._choices = session.build_choices(self.STAGE, self._target)
        self._render_choices()
        self.prompt_lbl.text = self.prompt_text(self._target)
        Clock.schedule_once(lambda dt: self._speak_target(), 0.3)

    def _render_choices(self):
        self.choice_row.cols = len(self._choices)
        self.choice_row.rows = 1
        self.choice_row.clear_widgets()
        for item in self._choices:
            tile = GlyphTile(
                glyph=self.tile_glyph(item), emoji=self.tile_emoji(item),
                on_tap=self._make_handler(item),
            )
            tile.bg_color = list(config.PALETTE["cream"])
            if item.color:
                tile.glyph_color = list(config.hex_rgba(item.color))
            self.choice_row.add_widget(tile)

    def _make_handler(self, item):
        def handler(tile):
            self._on_choice(item, tile)
        return handler

    def narration_key(self, item: ContentItem) -> str:
        """Override per stage to route to the right voice file."""
        return item.id

    def _speak_target(self):
        if self._target:
            self.mascot.say(self.prompt_text(self._target),
                            key=self.narration_key(self._target))

    # ------------------------------------------------------------------ #
    def _on_choice(self, item: ContentItem, tile: GlyphTile):
        if self._locked:
            return
        correct = item.id == self._target.id
        if correct:
            self._locked = True
            tile.flash(config.PALETTE["mint"])
            outcome = app().session.answer(self.STAGE, self._target, True)
            app().audio.play_sfx("correct")
            self.mascot.react()
            self.mascot.say(outcome.encouragement, key=outcome.encouragement_key)
            self.star_counter.bump(outcome.result.stars_awarded)
            self._update_progress()
            if outcome.celebrate:
                self.celebrate(big=True)
                self._announce_rewards(outcome.new_rewards)
            else:
                particles.star_pop(self.effects, tile.center)
            Clock.schedule_once(lambda dt: self._next_round(), 1.6)
        else:
            tile.flash(config.PALETTE["coral"])
            app().audio.play_sfx("wrong")
            app().session.answer(self.STAGE, self._target, False)
            self.mascot.say(NAV_LINES["retry_listen"], key="retry_listen")
            Clock.schedule_once(lambda dt: self._speak_target(), 0.6)

    def _announce_rewards(self, rewards):
        if not rewards:
            return
        r = rewards[0]
        self.narrate(f"You earned a new {r.kind}! The {r.name}!")

    # ------------------------------------------------------------------ #
    # Overridable presentation
    # ------------------------------------------------------------------ #
    def prompt_text(self, item: ContentItem) -> str:
        return f"Find {item.label}!"

    def tile_glyph(self, item: ContentItem) -> str:
        return item.label

    def tile_emoji(self, item: ContentItem) -> str:
        return item.emoji
