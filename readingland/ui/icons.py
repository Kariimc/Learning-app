"""Crisp vector UI icons drawn with Kivy graphics.

Chrome icons (back, home, speaker, gift, lock, page arrows...) are drawn as
vector shapes instead of font emoji. Font emoji render as missing-glyph "tofu"
boxes on platforms without a colour-emoji font (notably stock Windows in Kivy),
which looks broken. Vector icons render identically everywhere and scale cleanly
to any touch-target size.

``IconButton`` is the chunky, bouncy, sfx-playing button used for navigation and
actions; ``Icon`` is the bare drawable if you need an icon without a button.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

from kivy.animation import Animation
from kivy.graphics import (Color, Ellipse, Line, PopMatrix, PushMatrix,
                            RoundedRectangle, Scale, Triangle)
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget

from .. import config
from . import theme


def app():
    from kivy.app import App
    return App.get_running_app()


class Icon(Widget):
    """Draws a single named icon centred in its box, scaled to the box."""

    name   = StringProperty("back")
    color  = ListProperty(list(config.PALETTE["ink"]))
    line_w = NumericProperty(dp(6))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, name=self._draw, color=self._draw)
        self._draw()

    def _box(self):
        s = min(self.width, self.height) * 0.62
        cx, cy = self.center
        return cx, cy, s

    def _draw(self, *_):
        self.canvas.clear()
        cx, cy, s = self._box()
        w = max(dp(3), min(self.line_w, s * 0.16))
        with self.canvas:
            Color(*self.color)
            getattr(self, f"_icon_{self.name}", self._icon_back)(cx, cy, s, w)

    # -- individual icons ------------------------------------------------- #
    def _icon_back(self, cx, cy, s, w):
        Line(points=[cx + s * 0.2, cy + s * 0.4, cx - s * 0.2, cy,
                     cx + s * 0.2, cy - s * 0.4], width=w, cap="round", joint="round")

    def _icon_next(self, cx, cy, s, w):
        Line(points=[cx - s * 0.2, cy + s * 0.4, cx + s * 0.2, cy,
                     cx - s * 0.2, cy - s * 0.4], width=w, cap="round", joint="round")

    _icon_prev = _icon_back

    def _icon_home(self, cx, cy, s, w):
        Line(points=[cx - s * 0.45, cy + s * 0.02, cx, cy + s * 0.45,
                     cx + s * 0.45, cy + s * 0.02], width=w, cap="round", joint="round")
        Line(points=[cx - s * 0.32, cy - s * 0.02, cx - s * 0.32, cy - s * 0.42,
                     cx + s * 0.32, cy - s * 0.42, cx + s * 0.32, cy - s * 0.02],
             width=w, cap="round", joint="round")
        Line(points=[cx - s * 0.1, cy - s * 0.42, cx - s * 0.1, cy - s * 0.12,
                     cx + s * 0.1, cy - s * 0.12, cx + s * 0.1, cy - s * 0.42],
             width=w * 0.8, cap="round", joint="round")

    def _icon_speaker(self, cx, cy, s, w):
        Line(points=[cx - s * 0.42, cy - s * 0.14, cx - s * 0.22, cy - s * 0.14,
                     cx - s * 0.02, cy - s * 0.34, cx - s * 0.02, cy + s * 0.34,
                     cx - s * 0.22, cy + s * 0.14, cx - s * 0.42, cy + s * 0.14],
             width=w, cap="round", joint="round", close=True)
        for i in range(2):
            Line(circle=(cx + s * 0.12, cy, s * (0.2 + i * 0.16), -55, 55),
                 width=w * 0.8, cap="round")

    def _icon_play(self, cx, cy, s, w):
        Triangle(points=[cx - s * 0.28, cy + s * 0.36,
                         cx - s * 0.28, cy - s * 0.36,
                         cx + s * 0.4,  cy])

    def _icon_gift(self, cx, cy, s, w):
        Line(rounded_rectangle=(cx - s * 0.36, cy - s * 0.4, s * 0.72, s * 0.6, dp(4)),
             width=w, cap="round", joint="round")
        Line(points=[cx - s * 0.42, cy + s * 0.2, cx + s * 0.42, cy + s * 0.2],
             width=w, cap="round")
        Line(points=[cx, cy + s * 0.42, cx, cy - s * 0.4], width=w, cap="round")
        Line(circle=(cx - s * 0.12, cy + s * 0.34, s * 0.12), width=w * 0.8)
        Line(circle=(cx + s * 0.12, cy + s * 0.34, s * 0.12), width=w * 0.8)

    def _icon_lock(self, cx, cy, s, w):
        Line(rounded_rectangle=(cx - s * 0.3, cy - s * 0.4, s * 0.6, s * 0.5, dp(6)),
             width=w, cap="round", joint="round")
        Line(circle=(cx, cy + s * 0.12, s * 0.22, 0, 180), width=w, cap="round")
        Ellipse(pos=(cx - s * 0.06, cy - s * 0.2), size=(s * 0.12, s * 0.12))

    def _icon_pencil(self, cx, cy, s, w):
        Line(points=[cx - s * 0.35, cy - s * 0.35, cx + s * 0.3, cy + s * 0.3],
             width=w * 1.6, cap="round")
        Line(points=[cx + s * 0.3, cy + s * 0.3, cx + s * 0.42, cy + s * 0.42],
             width=w, cap="round")
        Line(points=[cx - s * 0.35, cy - s * 0.35, cx - s * 0.45, cy - s * 0.45],
             width=w * 2.0, cap="round")

    def _icon_switch(self, cx, cy, s, w):
        Line(circle=(cx, cy, s * 0.34, 20, 200), width=w, cap="round")
        Line(circle=(cx, cy, s * 0.34, 200, 380), width=w, cap="round")
        Line(points=[cx + s * 0.34, cy + s * 0.02, cx + s * 0.34, cy - s * 0.2,
                     cx + s * 0.12, cy - s * 0.12], width=w * 0.9, cap="round", joint="round")
        Line(points=[cx - s * 0.34, cy - s * 0.02, cx - s * 0.34, cy + s * 0.2,
                     cx - s * 0.12, cy + s * 0.12], width=w * 0.9, cap="round", joint="round")

    def _icon_check(self, cx, cy, s, w):
        Line(points=[cx - s * 0.3, cy, cx - s * 0.05, cy - s * 0.28,
                     cx + s * 0.36, cy + s * 0.3], width=w * 1.2, cap="round", joint="round")

    def _icon_star(self, cx, cy, s, w):
        pts = []
        for i in range(10):
            ang = math.pi / 2 + i * math.pi / 5
            rad = s * 0.45 if i % 2 == 0 else s * 0.2
            pts += [cx + rad * math.cos(ang), cy + rad * math.sin(ang)]
        Line(points=pts + pts[:2], width=w, cap="round", joint="round")

    def _icon_adult(self, cx, cy, s, w):
        Line(circle=(cx, cy + s * 0.22, s * 0.18), width=w, cap="round")
        Line(points=[cx - s * 0.3, cy - s * 0.4, cx - s * 0.24, cy - s * 0.06,
                     cx + s * 0.24, cy - s * 0.06, cx + s * 0.3, cy - s * 0.4],
             width=w, cap="round", joint="round")


class IconButton(ButtonBehavior, Widget):
    """Chunky rounded button showing a vector icon. Bounces + plays sfx on tap."""

    icon      = StringProperty("back")
    bg_color  = ListProperty(list(config.PALETTE["cream"]))
    icon_color = ListProperty(list(config.PALETTE["ink"]))
    radius    = NumericProperty(dp(26))
    sfx       = StringProperty("tap")
    _bounce   = NumericProperty(1.0)

    def __init__(self, on_tap: Optional[Callable] = None, **kwargs):
        super().__init__(**kwargs)
        self._on_tap = on_tap
        if self.size_hint == (1, 1):
            self.size_hint = (None, None)
            self.size = (theme.touch_size(), theme.touch_size())
        # canvas.before: PushMatrix + Scale wraps the bg drawing AND the child
        # Icon widget (canvas.after PopMatrix fires after children in Kivy).
        with self.canvas.before:
            PushMatrix()
            self._gscale = Scale(x=1, y=1, z=1)
            self._shadow_c = Color(*config.PALETTE["shadow"])
            self._shadow = RoundedRectangle(radius=[self.radius])
            self._bg_c = Color(*self.bg_color)
            self._bg = RoundedRectangle(radius=[self.radius])
        with self.canvas.after:
            PopMatrix()
        # Child Icon draws its own canvas co-located with this button.
        self._icon = Icon(name=self.icon, color=self.icon_color)
        self.add_widget(self._icon)
        self.bind(pos=self._sync, size=self._sync, bg_color=self._recolor,
                  icon=lambda *_: setattr(self._icon, "name", self.icon),
                  icon_color=lambda *_: setattr(self._icon, "color", self.icon_color),
                  _bounce=self._update_scale, center=self._update_scale)

    def _sync(self, *_):
        off = dp(4)
        self._shadow.pos = (self.x, self.y - off)
        self._shadow.size = self.size
        self._shadow.radius = [self.radius]
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.radius = [self.radius]
        # Icon exactly fills the button so Icon._box() centres the drawing.
        self._icon.pos = self.pos
        self._icon.size = self.size
        self._update_scale()

    def _recolor(self, *_):
        self._bg_c.rgba = self.bg_color

    def _update_scale(self, *_):
        self._gscale.x = self._bounce
        self._gscale.y = self._bounce
        self._gscale.origin = (self.center_x, self.center_y, 0)

    def on_press(self):
        a = app()
        if a and getattr(a, "audio", None):
            a.audio.play_sfx(self.sfx)
        Animation.cancel_all(self, "_bounce")
        Animation(_bounce=0.86, d=0.07, t="out_quad").start(self)

    def on_release(self):
        Animation.cancel_all(self, "_bounce")
        (Animation(_bounce=1.12, d=0.1, t="out_quad") +
         Animation(_bounce=1.0, d=0.14, t="out_bounce")).start(self)
        if self._on_tap:
            self._on_tap(self)
