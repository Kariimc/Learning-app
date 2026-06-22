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
from ..ui import particles, theme
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
            self._c_top = Color(*self.bg_top)
            self._rect_top = Rectangle()
            self._c_bottom = Color(*self.bg_bottom)
            self._rect_bottom = Rectangle()
            if self._bg_source:
                # Painted land art covers the gradient; clouds drift on top of it.
                Color(1, 1, 1, 1)
                self._bg_rect = Rectangle(source=self._bg_source)
            Color(1, 1, 1, 0.85 if not self._bg_source else 0.5)
            for _ in range(4):
                self._clouds.append(Ellipse())
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

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
        self.title_lbl = Label(text=self.title, font_size=theme.FONT_TITLE, bold=True,
                               color=config.PALETTE["cream"])
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
        for i, cloud in enumerate(self._clouds):
            cw = self.width * random.uniform(0.16, 0.26) if cloud.size[0] == 100 else cloud.size[0]
            cloud.size = (max(dp(120), self.width * 0.2), max(dp(50), self.height * 0.08))
            cloud.pos = (self.x + (i * self.width / 4), self.y + self.height * (0.6 + 0.08 * (i % 3)))

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
        # Endless gentle sky: nudge each cloud rightward, wrap around.
        speeds = [dp(8), dp(14), dp(6), dp(11)]
        for i, cloud in enumerate(self._clouds):
            x, y = cloud.pos
            x += speeds[i % len(speeds)] * dt
            if x > self.right:
                x = self.x - cloud.size[0]
            cloud.pos = (x, y)

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
