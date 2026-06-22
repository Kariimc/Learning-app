"""Stage 5 - Sentence River (sentence reading).

Penny Penguin shows a full sentence as word tiles. Tapping "Read" highlights each
word in turn while it is spoken (word-by-word karaoke). The child then taps the
picture that matches the sentence to advance.
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
from ..ui import theme
from ..ui.widgets import BigButton, ChunkyProgressBar, GlyphTile, Mascot
from .base import BaseScreen, app


class Stage5Screen(BaseScreen):
    STAGE = 5
    GUIDE = "penny_penguin"
    ACCENT = config.PALETTE["sky_deep"]
    title = "Sentence River"

    def __init__(self, **kwargs):
        self._target: Optional[ContentItem] = None
        self._word_lbls: List[Label] = []
        self._locked = False
        super().__init__(**kwargs)

    def build(self):
        char = app().content.character(self.GUIDE) if app() else {"id": self.GUIDE}
        self.mascot = Mascot(char=char, size_hint=(None, None),
                             size=(dp(130), dp(160)), pos_hint={"x": 0.03, "y": 0.5})
        self.content.add_widget(self.mascot)

        # Sentence word row.
        self.sentence_box = BoxLayout(orientation="horizontal", spacing=dp(10),
                                      size_hint=(0.9, 0.22),
                                      pos_hint={"center_x": 0.5, "top": 0.82},
                                      padding=dp(8))
        self.content.add_widget(self.sentence_box)

        # Read-along button.
        self.read_btn = BigButton(text="▶  Read it!", size=(dp(220), dp(72)),
                                  size_hint=(None, None),
                                  pos_hint={"center_x": 0.5, "y": 0.46},
                                  bg_color=list(config.PALETTE["sun"]),
                                  on_tap=lambda *_: self._read_along())
        self.content.add_widget(self.read_btn)

        self.prompt_lbl = Label(text="", font_size=theme.FONT_BODY, bold=True,
                                color=config.PALETTE["cream"], size_hint=(0.8, None),
                                height=dp(40), pos_hint={"center_x": 0.5, "y": 0.4})
        self.content.add_widget(self.prompt_lbl)

        self.choice_row = GridLayout(rows=1, spacing=dp(16), size_hint=(0.9, 0.28),
                                     pos_hint={"center_x": 0.5, "y": 0.12}, padding=dp(8))
        self.content.add_widget(self.choice_row)

        self.progress = ChunkyProgressBar(size_hint=(0.9, None), height=dp(22),
                                          pos_hint={"center_x": 0.5, "y": 0.04})
        self.progress.bar_color = list(self.ACCENT)
        self.content.add_widget(self.progress)

    # ------------------------------------------------------------------ #
    def refresh(self):
        if not app() or not app().session.profile:
            return
        self.mascot.idle()
        self.progress.value = app().session.stage_summary(self.STAGE).ratio
        self._next_round()

    def _next_round(self):
        self._locked = False
        session = app().session
        self._target = session.next_item(self.STAGE,
                                          exclude=self._target.id if self._target else None)
        if not self._target:
            return
        self._render_sentence()
        self._render_choices()
        self.prompt_lbl.text = "Read, then find the picture!"
        Clock.schedule_once(lambda dt: self._read_along(), 0.4)

    def _render_sentence(self):
        self.sentence_box.clear_widgets()
        self._word_lbls = []
        words = self._target.data.get("words", self._target.label.split())
        for w in words:
            lbl = Label(text=w, font_size=theme.FONT_TITLE, bold=True,
                        color=config.PALETTE["ink"])
            # Card-ish background per word for tap clarity.
            self.sentence_box.add_widget(lbl)
            self._word_lbls.append(lbl)

    def _read_along(self):
        """Karaoke highlight: speak each word and tint it as it's spoken."""
        words = self._target.data.get("words", self._target.label.split())
        delay = 0.0
        for i, (lbl, w) in enumerate(zip(self._word_lbls, words)):
            def step(dt, lbl=lbl, w=w):
                lbl.color = config.PALETTE["coral"]
                Animation(font_size=theme.FONT_TITLE * 1.25, d=0.12).start(lbl)
                Animation(font_size=theme.FONT_TITLE, d=0.25).start(lbl)
                if w not in (".", "!", ","):
                    app().audio.narrate(w)
                Clock.schedule_once(
                    lambda dt2, lbl=lbl: setattr(lbl, "color", config.PALETTE["ink"]), 0.5)
            Clock.schedule_once(step, delay)
            delay += 0.55

    def _render_choices(self):
        choices = app().session.build_choices(self.STAGE, self._target)
        self.choice_row.cols = len(choices)
        self.choice_row.clear_widgets()
        for item in choices:
            tile = GlyphTile(glyph=item.emoji or "?", emoji="",
                             on_tap=self._make_handler(item))
            tile.bg_color = list(config.PALETTE["cream"])
            self.choice_row.add_widget(tile)

    def _make_handler(self, item):
        def handler(tile):
            self._on_choice(item, tile)
        return handler

    def _on_choice(self, item: ContentItem, tile: GlyphTile):
        if self._locked:
            return
        if item.id == self._target.id:
            self._locked = True
            tile.flash(config.PALETTE["mint"])
            app().audio.play_sfx("correct")
            outcome = app().session.answer(self.STAGE, self._target, True)
            self.mascot.react()
            self.mascot.say(f"Yes! {self._target.label}")
            self.star_counter.bump(outcome.result.stars_awarded)
            self.progress.value = app().session.stage_summary(self.STAGE).ratio
            self.celebrate(big=outcome.celebrate)
            Clock.schedule_once(lambda dt: self._next_round(), 1.8)
        else:
            tile.flash(config.PALETTE["coral"])
            app().audio.play_sfx("wrong")
            app().session.answer(self.STAGE, self._target, False)
            self.mascot.say("Good try! Read it again.")
            Clock.schedule_once(lambda dt: self._read_along(), 0.5)
