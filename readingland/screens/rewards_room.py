"""Rewards Room - sticker book, badge shelf, daily treasure chest.

Hosted by Milo Monkey. Owned rewards are bright; not-yet-earned ones are faded
silhouettes to invite collection. Nothing here is ever lost.
"""
from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from .. import config
from ..ui import particles, theme
from ..ui.widgets import BigButton, GlyphTile, Mascot, RoundedCard
from .base import BaseScreen, app


class RewardsRoomScreen(BaseScreen):
    title = "My Treasures"

    def build(self):
        self.bg_top = config.PALETTE["sun"]
        self.bg_bottom = config.PALETTE["tangerine"]

        char = app().content.character("milo_monkey") if app() else {"id": "milo_monkey"}
        self.mascot = Mascot(char=char, size_hint=(None, None), size=(dp(120), dp(150)),
                             pos_hint={"right": 0.99, "y": 0.0})
        self.content.add_widget(self.mascot)

        self.chest_btn = BigButton(text="Open Daily Chest", size=(dp(280), dp(64)),
                                   size_hint=(None, None),
                                   pos_hint={"center_x": 0.5, "top": 0.86},
                                   bg_color=list(config.PALETTE["coral"]),
                                   on_tap=lambda *_: self._claim_chest())
        self.content.add_widget(self.chest_btn)

        self.scroll = ScrollView(size_hint=(1, 0.72), pos_hint={"x": 0, "top": 0.78})
        self.column = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(12),
                                padding=dp(16))
        self.column.bind(minimum_height=self.column.setter("height"))
        self.scroll.add_widget(self.column)
        self.content.add_widget(self.scroll)

    def refresh(self):
        if not app().session.profile:
            app().go("profiles")
            return
        self.mascot.idle()
        self._render()
        Clock.schedule_once(lambda dt: self.mascot.say(
            "Party time! Look at all your treasures!"), 0.3)

    def _render(self):
        self.column.clear_widgets()
        session = app().session

        # Stickers.
        self.column.add_widget(self._section_label("My Stickers"))
        sticker_grid = GridLayout(cols=4, spacing=dp(10), size_hint_y=None)
        sticker_grid.bind(minimum_height=sticker_grid.setter("height"))
        for s in session.rewards.sticker_book(session.pid):
            tile = GlyphTile(glyph=s["emoji"] if s["owned"] else "❔",
                             emoji=s["name"] if s["owned"] else "?",
                             size_hint=(1, None), height=dp(120))
            tile.bg_color = list(config.PALETTE["cream"]) if s["owned"] \
                else list(config.PALETTE["shadow"])
            sticker_grid.add_widget(tile)
        self.column.add_widget(sticker_grid)

        # Badges.
        self.column.add_widget(self._section_label("My Badges"))
        badge_grid = GridLayout(cols=4, spacing=dp(10), size_hint_y=None)
        badge_grid.bind(minimum_height=badge_grid.setter("height"))
        for b in session.rewards.badge_shelf(session.pid):
            tile = GlyphTile(glyph=b["emoji"] if b["owned"] else "🔒",
                             emoji=b["name"] if b["owned"] else "Locked",
                             size_hint=(1, None), height=dp(120))
            tile.bg_color = list(config.PALETTE["sun"]) if b["owned"] \
                else list(config.PALETTE["shadow"])
            badge_grid.add_widget(tile)
        self.column.add_widget(badge_grid)

    def _section_label(self, text):
        return Label(text=text, font_size=theme.FONT_TITLE, bold=True,
                     color=config.PALETTE["ink"], size_hint_y=None, height=dp(50))

    def _claim_chest(self):
        session = app().session
        grant = session.rewards.claim_daily_chest(session.pid)
        if grant:
            app().audio.play_sfx("chest")
            self.mascot.say("You opened the treasure chest! Wow!")
            particles.celebrate(self.effects, big=True)
            self.star_counter.count = session.stars()
            self._render()
        else:
            self.mascot.say("Finish your daily goal to open the chest!")
