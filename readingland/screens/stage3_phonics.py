"""Stage 3 - Sound Forest (phonics: blending).

Benny Bear shows a CVC word split into phoneme tiles (c | a | t). The child taps
each tile left-to-right to hear its sound, the tiles slide together to "build"
the word, then the child picks the matching picture to prove the blend.
"""
from __future__ import annotations

from typing import List, Optional

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from .. import config
from ..core.content import ContentItem
from ..core.voice_lines import NAV_LINES
from ..ui import particles, theme
from ..ui.widgets import ChunkyProgressBar, GlyphTile, Mascot
from .base import BaseScreen, app


class Stage3Screen(BaseScreen):
    STAGE = 3
    GUIDE = "benny_bear"
    ACCENT = config.PALETTE["grape"]
    title = "Sound Forest"
    bg_image_key = "phonics"

    def __init__(self, **kwargs):
        self._target: Optional[ContentItem] = None
        self._tapped = 0
        self._locked = False
        super().__init__(**kwargs)

    def build(self):
        char = app().content.character(self.GUIDE) if app() else {"id": self.GUIDE}
        self.mascot = Mascot(char=char, size_hint=(None, None),
                             size=(dp(140), dp(170)), pos_hint={"x": 0.04, "y": 0.45})
        self.content.add_widget(self.mascot)

        self.prompt_lbl = Label(text="Let's sound it out!", font_size=theme.FONT_HEADING,
                                bold=True, color=config.PALETTE["cream"],
                                size_hint=(0.7, None), height=dp(60),
                                pos_hint={"center_x": 0.5, "top": 0.95})
        self.content.add_widget(self.prompt_lbl)

        # Phoneme tiles row (the word being built).
        self.phoneme_row = GridLayout(rows=1, spacing=dp(14), size_hint=(0.8, 0.26),
                                      pos_hint={"center_x": 0.5, "top": 0.78},
                                      padding=dp(8))
        self.content.add_widget(self.phoneme_row)

        # Picture choices.
        self.choice_row = GridLayout(rows=1, spacing=dp(16), size_hint=(0.9, 0.3),
                                     pos_hint={"center_x": 0.5, "y": 0.14}, padding=dp(8))
        self.content.add_widget(self.choice_row)

        self.progress = ChunkyProgressBar(size_hint=(0.9, None), height=dp(24),
                                          pos_hint={"center_x": 0.5, "y": 0.05})
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
        self.progress.value = app().session.stage_summary(self.STAGE).ratio

    def _next_round(self):
        self._locked = False
        self._tapped = 0
        session = app().session
        self._target = session.next_item(self.STAGE,
                                          exclude=self._target.id if self._target else None)
        if not self._target:
            return
        self._build_phonemes()
        self._build_choices()
        self.prompt_lbl.text = "Tap each sound, then find the picture!"
        Clock.schedule_once(lambda dt: self.mascot.say(
            f"Let's build {self._target.label}. Tap the sounds!"), 0.3)

    def _build_phonemes(self):
        self.phoneme_row.clear_widgets()
        phonemes = self._target.data.get("phonemes", list(self._target.label))
        sounds = self._target.data.get("sounds", phonemes)
        self.phoneme_row.cols = len(phonemes)
        self._phoneme_tiles = []
        for i, ph in enumerate(phonemes):
            tile = GlyphTile(glyph=ph, emoji="",
                             on_tap=self._make_phoneme_handler(i, sounds[i] if i < len(sounds) else ph))
            tile.bg_color = list(config.PALETTE["cream"])
            tile.glyph_color = list(self.ACCENT)
            self.phoneme_row.add_widget(tile)
            self._phoneme_tiles.append(tile)

    def _make_phoneme_handler(self, index, sound):
        def handler(tile):
            app().audio.play_sfx("tap")
            self.mascot.say(sound)
            tile.flash(config.PALETTE["sun"])
            if index == self._tapped:
                self._tapped += 1
            if self._tapped >= len(self._phoneme_tiles):
                self._blend()
        return handler

    def _blend(self):
        # Slide tiles together and announce the whole word.
        self.prompt_lbl.text = f"{self._target.label}!"
        self.mascot.say(self._target.narration or self._target.label, key=self._target.id)
        for tile in self._phoneme_tiles:
            Animation(opacity=0.5, d=0.3).start(tile)

    def _build_choices(self):
        session = app().session
        choices = session.build_choices(self.STAGE, self._target)
        self.choice_row.cols = len(choices)
        self.choice_row.clear_widgets()
        for item in choices:
            tile = GlyphTile(glyph=item.emoji or "?", emoji="",
                             on_tap=self._make_choice_handler(item))
            tile.bg_color = list(config.PALETTE["cream"])
            self.choice_row.add_widget(tile)

    def _make_choice_handler(self, item):
        def handler(tile):
            self._on_choice(item, tile)
        return handler

    def _on_choice(self, item: ContentItem, tile: GlyphTile):
        if self._locked:
            return
        correct = item.id == self._target.id
        if correct:
            self._locked = True
            tile.flash(config.PALETTE["mint"])
            app().audio.play_sfx("correct")
            outcome = app().session.answer(self.STAGE, self._target, True)
            self.mascot.react()
            self.mascot.say(f"You blended {self._target.label}!")
            self.star_counter.bump(outcome.result.stars_awarded)
            self._update_progress()
            self.celebrate(big=outcome.celebrate)
            Clock.schedule_once(lambda dt: self._next_round(), 1.7)
        else:
            tile.flash(config.PALETTE["coral"])
            app().audio.play_sfx("wrong")
            app().session.answer(self.STAGE, self._target, False)
            self.mascot.say(NAV_LINES["retry_sound"], key="retry_sound")
