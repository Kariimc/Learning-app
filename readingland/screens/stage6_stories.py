"""Stage 6 - Story Sky (read-along storybooks).

Ollie Owl reads short, interactive books. Each page shows a scene, a line of text
that highlights word-by-word as it's read, and one tappable interactive object.
A library view lists the books; finishing a book marks it mastered.
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
from ..ui.widgets import BigButton, GlyphTile, Mascot, RoundedCard
from .base import BaseScreen, app


class Stage6Screen(BaseScreen):
    STAGE = 6
    GUIDE = "ollie_owl"
    title = "Story Sky"

    def __init__(self, **kwargs):
        self._book: Optional[ContentItem] = None
        self._page = 0
        self._word_lbls: List[Label] = []
        super().__init__(**kwargs)

    def build(self):
        self.bg_top = config.PALETTE["grape"]
        self.bg_bottom = config.PALETTE["sky_deep"]
        char = app().content.character(self.GUIDE) if app() else {"id": self.GUIDE}
        self.mascot = Mascot(char=char, size_hint=(None, None),
                             size=(dp(110), dp(140)), pos_hint={"right": 0.99, "y": 0.0})
        self.content.add_widget(self.mascot)

        # --- Library view --- #
        self.library = GridLayout(cols=3, spacing=dp(16), size_hint=(0.92, 0.7),
                                  pos_hint={"center_x": 0.5, "center_y": 0.5}, padding=dp(8))
        self.content.add_widget(self.library)

        # --- Reader view (hidden until a book is opened) --- #
        self.reader = BoxLayout(orientation="vertical", size_hint=(0.94, 0.82),
                                pos_hint={"center_x": 0.5, "center_y": 0.5},
                                padding=dp(12), spacing=dp(10))
        self.scene_card = RoundedCard(size_hint=(1, 0.55))
        self.scene_card.bg_color = list(config.PALETTE["cream"])
        self.scene_emoji = Label(text="", font_size=dp(120),
                                 font_name=theme.EMOJI_FONT_NAME if theme.register_fonts() else "Roboto")
        self.scene_card.add_widget(self.scene_emoji)
        self.reader.add_widget(self.scene_card)

        self.text_box = BoxLayout(orientation="horizontal", spacing=dp(8),
                                  size_hint=(1, 0.18), padding=dp(8))
        self.reader.add_widget(self.text_box)

        nav = BoxLayout(orientation="horizontal", size_hint=(1, 0.18), spacing=dp(12))
        self.prev_btn = BigButton(text="◀", size_hint=(0.25, 1),
                                  bg_color=list(config.PALETTE["cream"]),
                                  on_tap=lambda *_: self._turn(-1))
        self.read_btn = BigButton(text="🔊 Read", size_hint=(0.5, 1),
                                  bg_color=list(config.PALETTE["sun"]),
                                  on_tap=lambda *_: self._read_page())
        self.next_btn = BigButton(text="▶", size_hint=(0.25, 1),
                                  bg_color=list(config.PALETTE["mint"]),
                                  on_tap=lambda *_: self._turn(1))
        nav.add_widget(self.prev_btn)
        nav.add_widget(self.read_btn)
        nav.add_widget(self.next_btn)
        self.reader.add_widget(nav)
        self.reader.opacity = 0
        self.reader.disabled = True

    # ------------------------------------------------------------------ #
    def refresh(self):
        if not app() or not app().session.profile:
            return
        self.mascot.idle()
        self._show_library()

    def _show_library(self):
        if self.reader.parent:
            self.content.remove_widget(self.reader)
        if not self.library.parent:
            self.content.add_widget(self.library)
        self.library.clear_widgets()
        for book in app().content.items(self.STAGE):
            tile = GlyphTile(glyph=book.emoji, emoji=book.label,
                             on_tap=self._make_open(book))
            tile.bg_color = list(config.hex_rgba(book.color) if book.color else config.PALETTE["cream"])
            self.library.add_widget(tile)
        Clock.schedule_once(lambda dt: self.mascot.say("Whoo's ready for a story? Pick a book!"), 0.3)

    def _make_open(self, book):
        def handler(tile):
            self._open_book(book)
        return handler

    # ------------------------------------------------------------------ #
    def _open_book(self, book: ContentItem):
        self._book = book
        self._page = 0
        if self.library.parent:
            self.content.remove_widget(self.library)
        if not self.reader.parent:
            self.content.add_widget(self.reader)
        self.reader.opacity = 1
        self.reader.disabled = False
        self.mascot.say(book.narration or f"Let's read {book.label}")
        self._render_page()

    def _pages(self):
        return self._book.data.get("pages", []) if self._book else []

    def _render_page(self):
        pages = self._pages()
        if not pages:
            return
        self._page = max(0, min(self._page, len(pages) - 1))
        page = pages[self._page]
        self.scene_emoji.text = page.get("interactive", {}).get("emoji", self._book.emoji)
        self.text_box.clear_widgets()
        self._word_lbls = []
        for w in page.get("words", page.get("text", "").split()):
            lbl = Label(text=w, font_size=theme.FONT_HEADING, bold=True,
                        color=config.PALETTE["ink"])
            self.text_box.add_widget(lbl)
            self._word_lbls.append(lbl)
        Clock.schedule_once(lambda dt: self._read_page(), 0.35)

    def _read_page(self):
        pages = self._pages()
        if not pages:
            return
        page = pages[self._page]
        words = page.get("words", page.get("text", "").split())
        delay = 0.0
        for lbl, w in zip(self._word_lbls, words):
            def step(dt, lbl=lbl, w=w):
                lbl.color = config.PALETTE["grape"]
                Animation(font_size=theme.FONT_HEADING * 1.3, d=0.1).start(lbl)
                Animation(font_size=theme.FONT_HEADING, d=0.25).start(lbl)
                if w not in (".", "!", ",", "?"):
                    app().audio.narrate(w)
                Clock.schedule_once(
                    lambda dt2, lbl=lbl: setattr(lbl, "color", config.PALETTE["ink"]), 0.45)
            Clock.schedule_once(step, delay)
            delay += 0.5

    def _turn(self, direction: int):
        pages = self._pages()
        new_page = self._page + direction
        if new_page < 0:
            self._show_library()
            return
        if new_page >= len(pages):
            self._finish_book()
            return
        self._page = new_page
        app().audio.play_sfx("page")
        self._render_page()

    def _finish_book(self):
        self.mascot.say("The end! What a wonderful reader you are!")
        outcome = app().session.answer(self.STAGE, self._book, True)
        self.star_counter.bump(outcome.result.stars_awarded)
        self.celebrate(big=True)
        Clock.schedule_once(lambda dt: self._show_library(), 2.2)
