"""Profile select - 'Who's reading today?'.

Big avatar tiles, one per child. A '+' tile creates a new profile (avatar picker,
no keyboard needed). A small corner button opens the parent area behind a gate.
"""
from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView

from .. import config
from ..ui import theme
from ..ui.widgets import BigButton, GlyphTile, RoundedCard
from .base import BaseScreen, app

AVATARS = ["reading_rabbit", "benny_bear", "penny_penguin", "ollie_owl", "milo_monkey"]


class ProfileSelectScreen(BaseScreen):
    show_topbar = False

    def build(self):
        self.bg_top = config.PALETTE["sky"]
        self.heading = Label(text="Who's reading today?", font_size=dp(44), bold=True,
                             color=config.PALETTE["cream"],
                             pos_hint={"center_x": 0.5, "top": 0.96}, size_hint=(1, None),
                             height=dp(80))
        self.content.add_widget(self.heading)

        self.grid = GridLayout(cols=3, spacing=dp(20), size_hint=(0.9, 0.66),
                               pos_hint={"center_x": 0.5, "center_y": 0.48}, padding=dp(10))
        self.content.add_widget(self.grid)

        # Parent corner.
        self.parent_btn = BigButton(text="Parents", size=(dp(170), dp(64)),
                                    size_hint=(None, None), font_size=theme.FONT_BODY,
                                    pos_hint={"right": 0.98, "y": 0.03},
                                    bg_color=list(config.PALETTE["cream"]),
                                    color=config.PALETTE["grape"],
                                    on_tap=lambda *_: self._open_parent_gate())
        self.content.add_widget(self.parent_btn)

    def refresh(self):
        self.grid.clear_widgets()
        for prof in app().session.profiles.list():
            char = app().content.character(prof.avatar)
            tile = GlyphTile(glyph=char.get("emoji", "🙂"), emoji=prof.name,
                             on_tap=self._make_select(prof.id))
            tile.bg_color = list(config.hex_rgba(char.get("color", "#FFF6E9")))
            self.grid.add_widget(tile)
        add = GlyphTile(glyph="➕", emoji="New", on_tap=lambda *_: self._add_profile())
        add.bg_color = list(config.PALETTE["sun"])
        self.grid.add_widget(add)

    def _make_select(self, pid):
        def handler(tile):
            app().select_profile(pid)
        return handler

    # ------------------------------------------------------------------ #
    def _add_profile(self):
        modal = ModalView(size_hint=(0.8, 0.7), auto_dismiss=True)
        card = RoundedCard(orientation="vertical", padding=dp(16), spacing=dp(12))
        card.add_widget(Label(text="Pick your buddy!", font_size=theme.FONT_TITLE,
                              bold=True, color=config.PALETTE["ink"], size_hint=(1, 0.2)))
        row = GridLayout(cols=3, spacing=dp(14), size_hint=(1, 0.8))
        for avatar in AVATARS:
            char = app().content.character(avatar)
            tile = GlyphTile(glyph=char.get("emoji", "🙂"), emoji=char.get("name", avatar),
                             on_tap=self._make_create(avatar, modal))
            tile.bg_color = list(config.hex_rgba(char.get("color", "#FFF6E9")))
            row.add_widget(tile)
        card.add_widget(row)
        modal.add_widget(card)
        modal.open()

    def _make_create(self, avatar, modal):
        def handler(tile):
            n = len(app().session.profiles.list()) + 1
            prof = app().session.profiles.create(name=f"Reader {n}", avatar=avatar)
            modal.dismiss()
            app().select_profile(prof.id)
        return handler

    # ------------------------------------------------------------------ #
    def _open_parent_gate(self):
        """Simple multiply-gate keeps young children out of the parent area."""
        from .parent_dashboard import ParentGate
        ParentGate(on_success=lambda: app().go("parent")).open()
