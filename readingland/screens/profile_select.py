"""Profile select - 'Who's reading today?'.

Each child stands on their own cloud, the same way the six lands do on the map.
Tapping a cloud picks that child; the last cloud makes a new one. A small corner
button opens the parent area behind a gate.

The flat colour tiles this replaced were the method Kariim rejected: a picture
laid on a rectangle of paint, with the name clipped in half underneath it.
"""
from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView

from .. import config
from ..ui import sky, theme
from ..ui.widgets import BigButton, GlyphTile, RoundedCard
from .base import BaseScreen, app

AVATARS = ["reading_rabbit", "benny_bear", "penny_penguin", "ollie_owl", "milo_monkey"]


def cloud_spots(n: int):
    """Where n clouds float: a zigzag down the sky, the same walk the six
    lands take on the map. Never a grid — the sky is a place, not a table."""
    if n <= 1:
        return [(0.50, 0.55)]
    top, bottom = 0.74, 0.24
    step = (top - bottom) / (n - 1)
    return [(0.27 if i % 2 == 0 else 0.73, top - i * step) for i in range(n)]


class ProfileSelectScreen(BaseScreen):
    show_topbar = False

    def build(self):
        self.bg_top = config.PALETTE["sky"]
        # ink, not cream: cream text vanishes into a pale golden sky
        self.heading = Label(text="Who's reading today?", font_size=dp(44), bold=True,
                             color=config.PALETTE["ink"],
                             pos_hint={"center_x": 0.5, "top": 0.96}, size_hint=(1, None),
                             height=dp(80))
        self.content.add_widget(self.heading)

        self.clouds = []
        self._cloud_float_ev = None

        # Parent corner.
        self.parent_btn = BigButton(text="Parents", size=(dp(170), dp(64)),
                                    size_hint=(None, None), font_size=theme.FONT_BODY,
                                    pos_hint={"right": 0.98, "y": 0.03},
                                    bg_color=list(config.PALETTE["cream"]),
                                    color=config.PALETTE["grape"],
                                    on_tap=lambda *_: self._open_parent_gate())
        self.content.add_widget(self.parent_btn)

    def refresh(self):
        for c in self.clouds:
            self.content.remove_widget(c)
        self.clouds = []
        from ..ui.assets import character_image
        profiles = app().session.profiles.list()
        W = self.width or dp(400)
        spots = cloud_spots(len(profiles) + 1)
        for n, prof in enumerate(profiles):
            cx, cy = spots[n]
            cloud = sky.Perched(art=character_image(prof.avatar) or None,
                                cxf=cx, cyf=cy, wpx=W * 0.17, label=prof.name,
                                phase=n * 1.37, which=(n % 2) + 1,
                                on_tap=self._make_select(prof.id))
            self.content.add_widget(cloud)
            self.clouds.append(cloud)
        cx, cy = spots[len(profiles)]
        add = sky.Perched(art=None, cxf=cx, cyf=cy, wpx=W * 0.16, label="New",
                          phase=len(profiles) * 1.37, which=(len(profiles) % 2) + 1,
                          on_tap=lambda *_: self._add_profile())
        self.content.add_widget(add)
        self.clouds.append(add)
        self._t = 0.0
        if self._cloud_float_ev is None:
            self._cloud_float_ev = Clock.schedule_interval(self._float, 1 / 60.0)

    def _float(self, dt):
        self._t = getattr(self, "_t", 0.0) + dt
        for c in self.clouds:
            c.step(self._t, self.width, self.height)

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
        from ..ui.assets import character_image
        for avatar in AVATARS:
            char = app().content.character(avatar)
            portrait = character_image(avatar) or ""
            name = char.get("name", avatar)
            tile = GlyphTile(glyph=name, emoji="" if portrait else name,
                             image=portrait, on_tap=self._make_create(avatar, modal))
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
