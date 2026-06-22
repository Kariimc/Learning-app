"""Particle / celebration effects: confetti, stars, bubbles, balloons.

These are deliberately lightweight - a handful of animated ``Widget`` tokens that
add themselves to a parent layout, animate, then remove themselves. The brief
calls for confetti, bubbles, stars and balloons on wins; this module is the
single place that produces them so every screen celebrates consistently.
"""
from __future__ import annotations

import random

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from .. import config
from . import theme

_CONFETTI_COLORS = [
    config.PALETTE["coral"], config.PALETTE["sun"], config.PALETTE["mint"],
    config.PALETTE["grape"], config.PALETTE["sky"], config.PALETTE["bubblegum"],
]


class _Particle(Widget):
    def __init__(self, color, kind="rect", size=dp(16), **kwargs):
        super().__init__(size_hint=(None, None), size=(size, size), **kwargs)
        with self.canvas:
            Color(*color)
            if kind == "rect":
                self._g = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(3)])
            else:
                self._g = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self._g.pos = self.pos
        self._g.size = self.size


def burst_confetti(parent, count: int = 36, origin=None):
    """Spray confetti from ``origin`` (defaults to top-centre of parent)."""
    if parent is None:
        return
    ox = origin[0] if origin else parent.center_x
    oy = origin[1] if origin else parent.top - dp(40)
    for _ in range(count):
        p = _Particle(random.choice(_CONFETTI_COLORS),
                      kind=random.choice(["rect", "ellipse"]),
                      size=dp(random.randint(10, 20)))
        p.center = (ox, oy)
        parent.add_widget(p)
        dx = random.uniform(-parent.width * 0.45, parent.width * 0.45)
        dy = random.uniform(-parent.height * 0.55, -dp(60))
        anim = Animation(center_x=ox + dx, center_y=oy + dy,
                         opacity=0.0, d=random.uniform(0.8, 1.5), t="out_quad")
        anim.bind(on_complete=lambda a, w=p: parent.remove_widget(w))
        anim.start(p)


def rising_bubbles(parent, count: int = 14):
    if parent is None:
        return
    for _ in range(count):
        size = dp(random.randint(18, 44))
        p = _Particle((1, 1, 1, 0.35), kind="ellipse", size=size)
        p.center = (random.uniform(parent.x, parent.right), parent.y - size)
        parent.add_widget(p)
        anim = Animation(center_y=parent.top + size, opacity=0.0,
                         d=random.uniform(2.2, 4.0), t="in_out_sine")
        anim.bind(on_complete=lambda a, w=p: parent.remove_widget(w))
        anim.start(p)


def float_balloons(parent, count: int = 6):
    if parent is None:
        return
    for _ in range(count):
        emoji = Label(text="🎈", font_size=dp(random.randint(40, 70)),
                      size_hint=(None, None), size=(dp(70), dp(70)),
                      font_name=theme.EMOJI_FONT_NAME if theme.register_fonts() else "Roboto")
        emoji.center = (random.uniform(parent.x, parent.right), parent.y)
        parent.add_widget(emoji)
        anim = Animation(center_y=parent.top + dp(80),
                         d=random.uniform(2.5, 4.5), t="out_sine")
        anim.bind(on_complete=lambda a, w=emoji: parent.remove_widget(w))
        anim.start(emoji)


def star_pop(parent, center, count: int = 10):
    if parent is None:
        return
    for _ in range(count):
        star = Label(text="⭐", font_size=dp(random.randint(20, 38)),
                     size_hint=(None, None), size=(dp(40), dp(40)),
                     font_name=theme.EMOJI_FONT_NAME if theme.register_fonts() else "Roboto")
        star.center = center
        parent.add_widget(star)
        ang = random.uniform(0, 6.28)
        dist = random.uniform(dp(60), dp(160))
        import math
        anim = Animation(center_x=center[0] + dist * math.cos(ang),
                         center_y=center[1] + dist * math.sin(ang),
                         opacity=0.0, font_size=dp(12),
                         d=random.uniform(0.7, 1.2), t="out_quad")
        anim.bind(on_complete=lambda a, w=star: parent.remove_widget(w))
        anim.start(star)


def celebrate(parent, big: bool = True):
    """One-call celebration combo used after correct answers / milestones."""
    burst_confetti(parent, count=44 if big else 20)
    if big:
        float_balloons(parent, count=5)
        Clock.schedule_once(lambda dt: rising_bubbles(parent, 10), 0.1)
