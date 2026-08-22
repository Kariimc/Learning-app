"""BaseScreen: living background + top bar shared by every screen.

The brief demands "no static screens", so the base paints an animated sky
(gradient + drifting clouds + lazy bubbles) behind all content. Subclasses add
their own widgets to ``self.content`` (a FloatLayout) on top.
"""
from __future__ import annotations

import random
from typing import Callable, Optional

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from .. import config
from ..ui import particles, sky, theme
from ..ui.icons import IconButton
from ..ui.widgets import BigButton, StarCounter


def app():
    from kivy.app import App
    return App.get_running_app()


class _Cloud(Ellipse):
    pass


class BaseScreen(Screen):
    bg_top = config.PALETTE["sky"]
    bg_bottom = config.PALETTE["sky_deep"]
    bg_image_key = None          # set by subclasses to load a painted background
    show_topbar = True
    title = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from ..ui.assets import background_image
        self._bg_source = background_image(self.bg_image_key) if self.bg_image_key else None
        self._clouds = []
        with self.canvas.before:
            # Kept only as the floor under the sky and behind painted land art.
            self._c_top = Color(*self.bg_top)
            self._rect_top = Rectangle()
            self._c_bottom = Color(*self.bg_bottom)
            self._rect_bottom = Rectangle()
            if self._bg_source:
                Color(1, 1, 1, 1)
                self._bg_rect = Rectangle(source=self._bg_source)
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

        # The sky world. Screens with no painted land art get the shader sky and
        # real wool drifting past; the four drawn ellipses this replaced were the
        # method Kariim rejected. See ui/sky.py.
        self.sky = None
        if not self._bg_source and sky.wool_path(1):
            self.sky = sky.ShaderSky(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
            self.root_layout.add_widget(self.sky)
            for i, (spd, yf, wpx) in enumerate(
                    [(dp(5), 0.92, dp(150)), (dp(4), 0.72, dp(135)),
                     (dp(9), 0.60, dp(165)), (dp(7), 0.34, dp(150)),
                     (dp(3), 0.47, dp(120)), (dp(6), 0.17, dp(145))]):
                c = sky.WoolCloud(speed=spd, yfrac=yf, width_px=wpx,
                                  which=(i % 2) + 1)
                self.root_layout.add_widget(c)
                self._clouds.append(c)

        # Top bar (back + title + stars).
        self.topbar = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=theme.touch_size(),
            pos_hint={"top": 1}, padding=[dp(12), dp(6)], spacing=dp(8),
        )
        self.back_btn = IconButton(
            icon="home", size=(theme.touch_size(), theme.touch_size()),
            size_hint=(None, None), bg_color=list(config.PALETTE["cream"]),
            icon_color=list(config.PALETTE["grape"]),
            on_tap=lambda *_: self.on_back(),
        )
        # ink on the sky screens, cream over painted land art, because the sky
        # is pale at golden hour and cream text vanished into it
        self.title_lbl = Label(text=self.title, font_size=theme.FONT_TITLE, bold=True,
                               color=config.PALETTE["cream"] if self._bg_source
                               else config.PALETTE["ink"])
        self.star_counter = StarCounter(size_hint=(None, 1), width=dp(120))
        if self.show_topbar:
            self.topbar.add_widget(self.back_btn)
            self.topbar.add_widget(self.title_lbl)
            self.topbar.add_widget(self.star_counter)
            self.root_layout.add_widget(self.topbar)

        # Content area below the top bar.
        self.content = FloatLayout(
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
        )
        self.root_layout.add_widget(self.content)
        # Effects layer always on top.
        self.effects = FloatLayout()
        self.root_layout.add_widget(self.effects)

        self.build()

    # ------------------------------------------------------------------ #
    # Lifecycle hooks for subclasses
    # ------------------------------------------------------------------ #
    def build(self):
        """Override: construct screen content into ``self.content``."""

    def refresh(self):
        """Override: re-read state when the screen is shown."""

    # ------------------------------------------------------------------ #
    def _sync_bg(self, *_):
        h = self.height
        self._rect_top.pos = (self.x, self.y + h / 2)
        self._rect_top.size = (self.width, h / 2)
        self._rect_bottom.pos = self.pos
        self._rect_bottom.size = (self.width, h / 2)
        if self._bg_source:
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size
        # The wool sizes and places itself in step(); nothing to lay out here.

    def on_pre_enter(self, *args):
        self.refresh()
        if self.show_topbar and getattr(app(), "session", None) and app().session.profile:
            self.star_counter.count = app().session.stars()
        self._cloud_ev = Clock.schedule_interval(self._drift_clouds, 1 / 30.0)

    def on_pre_leave(self, *args):
        ev = getattr(self, "_cloud_ev", None)
        if ev:
            ev.cancel()

    def _drift_clouds(self, dt):
        # Endless gentle sky. Each cloud carries its own speed, so the layers
        # separate by parallax rather than by being drawn dimmer.
        for cloud in self._clouds:
            cloud.step(dt, self.width, self.height)

    # ------------------------------------------------------------------ #
    # Navigation helpers
    # ------------------------------------------------------------------ #
    def on_back(self):
        a = app()
        if a:
            a.go("home")

    def celebrate(self, big=True):
        particles.celebrate(self.effects, big=big)

    def narrate(self, text, key=None):
        a = app()
        if a and getattr(a, "audio", None):
            a.audio.narrate(text, key=key)
