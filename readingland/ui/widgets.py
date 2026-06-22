"""Reusable, chunky, child-friendly widgets.

All interactive widgets are oversized (>= MIN_TOUCH_TARGET_DP), bounce on press
and trigger a sound effect, so *every tap creates animation + sound + visual
response* per the design brief.
"""
from __future__ import annotations

from typing import Callable, Optional

from kivy.animation import Animation
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle, Triangle
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from .. import config
from . import theme


def app():
    from kivy.app import App
    return App.get_running_app()


def _is_emoji(text: str) -> bool:
    """Heuristic: does this string contain pictographic / emoji codepoints?"""
    return any(ord(c) >= 0x2190 for c in text)


def _font_for(text: str) -> str:
    """Pick the emoji font for pictographic glyphs, else the default."""
    if _is_emoji(text) and theme.register_fonts():
        return theme.EMOJI_FONT_NAME
    return "Roboto"


# --------------------------------------------------------------------------- #
class RoundedCard(BoxLayout):
    """A BoxLayout with a soft rounded background + drop shadow."""

    bg_color = ListProperty(list(config.PALETTE["cream"]))
    radius = NumericProperty(dp(28))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._shadow_color = Color(*config.PALETTE["shadow"])
            self._shadow = RoundedRectangle(radius=[self.radius])
            self._bg_color = Color(*self.bg_color)
            self._bg = RoundedRectangle(radius=[self.radius])
        self.bind(pos=self._sync, size=self._sync, bg_color=self._sync_color)

    def _sync(self, *_):
        off = dp(6)
        self._shadow.pos = (self.x, self.y - off)
        self._shadow.size = self.size
        self._shadow.radius = [self.radius]
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.radius = [self.radius]

    def _sync_color(self, *_):
        self._bg_color.rgba = self.bg_color


# --------------------------------------------------------------------------- #
class BigButton(ButtonBehavior, Label):
    """A large rounded button. Bounces and plays a 'pop' sfx on press."""

    bg_color = ListProperty(list(config.PALETTE["mint"]))
    radius = NumericProperty(dp(32))
    sfx = StringProperty("pop")

    def __init__(self, on_tap: Optional[Callable] = None, **kwargs):
        kwargs.setdefault("font_size", theme.FONT_HEADING)
        kwargs.setdefault("color", config.PALETTE["ink"])
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)
        self._on_tap = on_tap
        self.size_hint = kwargs.get("size_hint", (None, None))
        if self.size_hint == (None, None):
            self.size = kwargs.get("size", (dp(220), theme.touch_size()))
        with self.canvas.before:
            self._shadow_c = Color(*config.PALETTE["shadow"])
            self._shadow = RoundedRectangle(radius=[self.radius])
            self._bg_c = Color(*self.bg_color)
            self._bg = RoundedRectangle(radius=[self.radius])
        self.bind(pos=self._sync, size=self._sync, bg_color=self._sync_color)

    def _sync(self, *_):
        off = dp(5)
        self._shadow.pos = (self.x, self.y - off)
        self._shadow.size = self.size
        self._shadow.radius = [self.radius]
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.radius = [self.radius]

    def _sync_color(self, *_):
        self._bg_c.rgba = self.bg_color

    def on_press(self):
        a = app()
        if a and getattr(a, "audio", None):
            a.audio.play_sfx(self.sfx)
        Animation(opacity=0.85, d=0.05).start(self)
        Animation.cancel_all(self, "scale")  # (visual hook for kv scaling)

    def on_release(self):
        Animation(opacity=1.0, d=0.08).start(self)
        if self._on_tap:
            self._on_tap(self)


# --------------------------------------------------------------------------- #
class ShapeWidget(Widget):
    """Draws a primitive shape (circle/square/triangle/star/heart) in a colour.

    Used as placeholder art for Stage 1 'shapes' and as a generic visual token.
    """

    shape = StringProperty("circle")
    fill = ListProperty(list(config.PALETTE["coral"]))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, shape=self._draw, fill=self._draw)
        self._draw()

    def _draw(self, *_):
        self.canvas.clear()
        with self.canvas:
            Color(*self.fill)
            cx, cy = self.center
            w, h = self.width, self.height
            s = min(w, h) * 0.8
            if self.shape == "circle":
                Ellipse(pos=(cx - s / 2, cy - s / 2), size=(s, s))
            elif self.shape == "square":
                RoundedRectangle(pos=(cx - s / 2, cy - s / 2), size=(s, s), radius=[dp(10)])
            elif self.shape == "triangle":
                Triangle(points=[cx - s / 2, cy - s / 2, cx + s / 2, cy - s / 2, cx, cy + s / 2])
            elif self.shape == "star":
                self._star(cx, cy, s / 2)
            elif self.shape == "heart":
                self._heart(cx, cy, s)
            else:
                Ellipse(pos=(cx - s / 2, cy - s / 2), size=(s, s))

    def _star(self, cx, cy, r):
        import math
        pts = []
        for i in range(10):
            ang = math.pi / 2 + i * math.pi / 5
            rad = r if i % 2 == 0 else r * 0.45
            pts += [cx + rad * math.cos(ang), cy + rad * math.sin(ang)]
        # Triangulate fan.
        for i in range(0, 18, 2):
            Triangle(points=[cx, cy, pts[i], pts[i + 1],
                             pts[(i + 2) % 20], pts[(i + 3) % 20]])

    def _heart(self, cx, cy, s):
        r = s * 0.25
        Ellipse(pos=(cx - r * 1.1, cy), size=(r * 1.4, r * 1.4))
        Ellipse(pos=(cx - r * 0.3, cy), size=(r * 1.4, r * 1.4))
        Triangle(points=[cx - r * 1.05, cy + r * 0.5,
                         cx + r * 1.05, cy + r * 0.5,
                         cx, cy - s * 0.45])


# --------------------------------------------------------------------------- #
class Mascot(FloatLayout):
    """Placeholder mascot: a coloured blob body with eyes + the character emoji.

    Replaced by sprite-sheet art in production (see asset spec). Exposes
    ``react()`` (happy bounce), ``idle()`` (gentle breathing) and ``say()``.
    """

    char_id = StringProperty("reading_rabbit")
    body_color = ListProperty(list(config.PALETTE["bubblegum"]))
    emoji = StringProperty("🐰")

    def __init__(self, char: Optional[dict] = None, **kwargs):
        super().__init__(**kwargs)
        if char:
            self.char_id = char.get("id", self.char_id)
            self.emoji = char.get("emoji", self.emoji)
            col = char.get("color")
            if col:
                self.body_color = list(config.hex_rgba(col))
        with self.canvas.before:
            self._c = Color(*self.body_color)
            self._body = Ellipse()
            self._ear_c = Color(*self.body_color)
            self._ear1 = Ellipse()
            self._ear2 = Ellipse()
            Color(1, 1, 1, 1)
            self._eye1 = Ellipse()
            self._eye2 = Ellipse()
            Color(*config.PALETTE["ink"])
            self._pupil1 = Ellipse()
            self._pupil2 = Ellipse()
        self.bind(pos=self._draw, size=self._draw, body_color=self._recolor)
        self._face = Label(text=self.emoji, font_size=dp(40),
                           font_name=theme.EMOJI_FONT_NAME if theme.register_fonts() else "Roboto")
        self.add_widget(self._face)
        self.bind(pos=self._place_face, size=self._place_face)

    def _recolor(self, *_):
        self._c.rgba = self.body_color
        self._ear_c.rgba = self.body_color

    def _place_face(self, *_):
        self._face.center_x = self.center_x
        self._face.center_y = self.y + self.height * 0.18
        self._face.font_size = self.height * 0.16

    def _draw(self, *_):
        w, h = self.width, self.height
        x, y = self.pos
        bw, bh = w * 0.7, h * 0.6
        self._body.pos = (x + (w - bw) / 2, y + h * 0.05)
        self._body.size = (bw, bh)
        er = w * 0.16
        self._ear1.pos = (x + w * 0.3 - er / 2, y + h * 0.6)
        self._ear1.size = (er, h * 0.35)
        self._ear2.pos = (x + w * 0.7 - er / 2, y + h * 0.6)
        self._ear2.size = (er, h * 0.35)
        eye = w * 0.1
        self._eye1.pos = (x + w * 0.4 - eye / 2, y + h * 0.45)
        self._eye1.size = (eye, eye)
        self._eye2.pos = (x + w * 0.6 - eye / 2, y + h * 0.45)
        self._eye2.size = (eye, eye)
        pup = eye * 0.5
        self._pupil1.pos = (x + w * 0.4 - pup / 2, y + h * 0.47)
        self._pupil1.size = (pup, pup)
        self._pupil2.pos = (x + w * 0.6 - pup / 2, y + h * 0.47)
        self._pupil2.size = (pup, pup)

    # -- behaviours ------------------------------------------------------- #
    def idle(self):
        anim = (Animation(opacity=0.92, d=1.1) + Animation(opacity=1.0, d=1.1))
        anim.repeat = True
        anim.start(self)

    def react(self):
        base_y = self.y
        (Animation(y=base_y + dp(24), d=0.16, t="out_back")
         + Animation(y=base_y, d=0.22, t="out_bounce")).start(self)

    def say(self, text: str, key: Optional[str] = None):
        a = app()
        if a and getattr(a, "audio", None):
            a.audio.narrate(text, key=key)
        self.react()


# --------------------------------------------------------------------------- #
class GlyphTile(ButtonBehavior, RoundedCard):
    """A tappable tile showing a big glyph (letter/word) and optional emoji.

    The workhorse answer-choice / content widget across every stage.
    """

    glyph = StringProperty("A")
    emoji = StringProperty("")
    glyph_color = ListProperty(list(config.PALETTE["ink"]))

    def __init__(self, on_tap: Optional[Callable] = None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(8)
        self._on_tap = on_tap
        self._emoji_lbl = Label(
            text=self.emoji, font_size=dp(40), size_hint_y=0.45,
            color=config.PALETTE["ink"], font_name=_font_for(self.emoji),
            halign="center", valign="middle", shorten=True, shorten_from="right",
        )
        self._glyph_lbl = Label(
            text=self.glyph, font_size=theme.FONT_DISPLAY, bold=True,
            color=self.glyph_color, size_hint_y=0.55, font_name=_font_for(self.glyph),
            halign="center", valign="middle",
        )
        self._emoji_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
        self._glyph_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.add_widget(self._emoji_lbl)
        self.add_widget(self._glyph_lbl)
        self.bind(glyph=self._on_glyph, emoji=self._on_emoji,
                  glyph_color=lambda *_: setattr(self._glyph_lbl, "color", self.glyph_color),
                  size=self._scale)

    def _on_glyph(self, *_):
        self._glyph_lbl.text = self.glyph
        self._glyph_lbl.font_name = _font_for(self.glyph)

    def _on_emoji(self, *_):
        self._emoji_lbl.text = self.emoji
        self._emoji_lbl.font_name = _font_for(self.emoji)

    def _scale(self, *_):
        # Big glyph scales with tile height, but shrinks for long words so a
        # word like "happy" or a name like "Reader 1" never overflows the card.
        size = self.height * 0.42
        n = max(1, len(self.glyph.strip()))
        if n > 1:
            size = min(size, self.width * 1.5 / n)
        self._glyph_lbl.font_size = max(dp(18), size)
        cap = self.height * 0.26
        cn = max(1, len(self.emoji.strip()))
        if cn > 2:  # a word/name caption, not a single emoji
            cap = min(cap, self.width * 1.6 / cn)
        self._emoji_lbl.font_size = max(dp(14), cap)

    def on_press(self):
        a = app()
        if a and getattr(a, "audio", None):
            a.audio.play_sfx("tap")
        Animation(opacity=0.8, d=0.05).start(self)

    def on_release(self):
        Animation(opacity=1.0, d=0.1).start(self)
        if self._on_tap:
            self._on_tap(self)

    def flash(self, color):
        """Briefly tint the card (green=correct, coral=gentle retry)."""
        original = list(self.bg_color)
        self.bg_color = list(color)
        Animation(bg_color=original, d=0.6).start(self)


# --------------------------------------------------------------------------- #
class ChunkyProgressBar(Widget):
    value = NumericProperty(0.0)  # 0..1
    bar_color = ListProperty(list(config.PALETTE["mint"]))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1, 0.5)
            self._track = RoundedRectangle(radius=[dp(14)])
            Color(*self.bar_color)
            self._fill = RoundedRectangle(radius=[dp(14)])
        self.bind(pos=self._sync, size=self._sync, value=self._sync, bar_color=self._recolor)

    def _recolor(self, *_):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 0.5)
            self._track = RoundedRectangle(radius=[dp(14)])
            Color(*self.bar_color)
            self._fill = RoundedRectangle(radius=[dp(14)])
        self._sync()

    def _sync(self, *_):
        self._track.pos = self.pos
        self._track.size = self.size
        self._fill.pos = self.pos
        self._fill.size = (self.width * max(0.0, min(1.0, self.value)), self.height)


# --------------------------------------------------------------------------- #
class StarCounter(BoxLayout):
    count = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", spacing=dp(6), **kwargs)
        self._star = Label(text="⭐", font_size=dp(28),
                           font_name=theme.EMOJI_FONT_NAME if theme.register_fonts() else "Roboto")
        self._num = Label(text="0", font_size=theme.FONT_HEADING, bold=True,
                          color=config.PALETTE["ink"])
        self.add_widget(self._star)
        self.add_widget(self._num)
        self.bind(count=lambda *_: setattr(self._num, "text", str(self.count)))

    def bump(self, amount: int):
        self.count += amount
        Animation(font_size=dp(40), d=0.12).start(self._star)
        Animation(font_size=dp(28), d=0.2).start(self._star)
