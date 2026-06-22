"""Letter Tracing activity (visual guides + finger tracing).

Reading Rabbit shows a big letter with a dotted stroke guide, a green start dot
and a numbered/animated demo. The child drags a finger along each stroke in
order; the traced path lights up as they go. Completing all strokes counts as
practicing that letter (records a correct answer for Stage 2), so tracing plugs
straight into mastery, stars and rewards.

Forgiving by design: generous tolerance, no failure state, gentle re-prompts.
"""
from __future__ import annotations

from typing import Callable, List, Optional

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from .. import config
from ..core import tracing
from ..core.content import ContentItem
from ..ui import particles, theme
from ..ui.widgets import ChunkyProgressBar, GlyphTile, Mascot
from .base import BaseScreen, app


class TracingCanvas(Widget):
    """Renders a letter's stroke guides and tracks finger tracing."""

    def __init__(self, on_complete: Optional[Callable] = None, **kwargs):
        super().__init__(**kwargs)
        self.on_complete = on_complete
        self._strokes: List[List[tuple]] = []   # normalized strokes
        self._ci = 0                             # current stroke index
        self._pi = 0                             # progress index within stroke
        self._tracing = False
        self._demo_ev = None
        self.glyph = ""
        self.glyph_color = config.PALETTE["tangerine"]
        self.bind(pos=self._redraw, size=self._redraw)

    # ------------------------------------------------------------------ #
    def load(self, letter: str, color):
        self._strokes = tracing.get_strokes(letter) or []
        self._ci = 0
        self._pi = 0
        self._tracing = False
        self.glyph = letter
        self.glyph_color = color
        self._redraw()
        self._play_demo()

    def _box(self):
        """Square trace box centred in the widget."""
        side = min(self.width, self.height)
        x = self.x + (self.width - side) / 2
        y = self.y + (self.height - side) / 2
        return x, y, side

    def _to_px(self, p):
        x, y, side = self._box()
        return (x + p[0] * side, y + p[1] * side)

    # ------------------------------------------------------------------ #
    def _redraw(self, *_):
        self.canvas.clear()
        if not self._strokes:
            return
        with self.canvas:
            # Faint full-letter guide (all strokes, dotted look via thin line).
            Color(*config.PALETTE["ink"][:3], 0.18)
            for stroke in self._strokes:
                pts = []
                for p in stroke:
                    pts.extend(self._to_px(p))
                Line(points=pts, width=dp(9), cap="round", joint="round")

            # Already-completed strokes in bright colour.
            Color(*self.glyph_color)
            for done in self._strokes[: self._ci]:
                pts = []
                for p in done:
                    pts.extend(self._to_px(p))
                Line(points=pts, width=dp(10), cap="round", joint="round")

            # Current stroke: traced-so-far portion bright.
            if self._ci < len(self._strokes):
                cur = self._strokes[self._ci]
                pts = []
                for p in cur[: self._pi + 1]:
                    pts.extend(self._to_px(p))
                if len(pts) >= 4:
                    Color(*self.glyph_color)
                    Line(points=pts, width=dp(10), cap="round", joint="round")
                # Green start dot at the next point to touch.
                nxt = cur[min(self._pi, len(cur) - 1)]
                cx, cy = self._to_px(nxt)
                Color(*config.PALETTE["mint"])
                r = dp(18)
                Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))

    # ------------------------------------------------------------------ #
    def _play_demo(self):
        """Animate a dot along the current stroke to model the motion."""
        if self._demo_ev:
            self._demo_ev.cancel()
        if self._ci >= len(self._strokes):
            return
        cur = self._strokes[self._ci]
        self._demo_i = 0

        # Demo dot graphic.
        self._demo_dot = Ellipse()
        with self.canvas:
            self._demo_color = Color(*config.PALETTE["coral"])
            self._demo_dot = Ellipse()

        def step(dt):
            if self._tracing:           # child took over - stop demo
                return False
            if self._demo_i >= len(cur):
                self._redraw()
                return False
            cx, cy = self._to_px(cur[self._demo_i])
            r = dp(14)
            self._demo_dot.pos = (cx - r, cy - r)
            self._demo_dot.size = (r * 2, r * 2)
            self._demo_i += 1
            return True

        self._demo_ev = Clock.schedule_interval(step, 0.04)

    # ------------------------------------------------------------------ #
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos) or self._ci >= len(self._strokes):
            return super().on_touch_down(touch)
        cur = self._strokes[self._ci]
        start_px = self._to_px(cur[self._pi])
        if self._dist(touch.pos, start_px) <= self._tol():
            self._tracing = True
            if self._demo_ev:
                self._demo_ev.cancel()
            app().audio.play_sfx("tap")
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self._tracing or self._ci >= len(self._strokes):
            return super().on_touch_move(touch)
        cur = self._strokes[self._ci]
        tol = self._tol()
        advanced = False
        # Advance through any upcoming points the finger is now near (forgiving).
        while self._pi < len(cur) - 1 and self._dist(touch.pos, self._to_px(cur[self._pi + 1])) <= tol:
            self._pi += 1
            advanced = True
        if advanced:
            self._redraw()
            if self._pi >= len(cur) - 1:
                self._finish_stroke()
        return True

    def on_touch_up(self, touch):
        if self._tracing and self._ci < len(self._strokes):
            # Didn't finish the stroke - reset progress on this stroke, retry.
            self._tracing = False
            if self._pi < len(self._strokes[self._ci]) - 1:
                self._pi = 0
                self._redraw()
                self._play_demo()
        return super().on_touch_up(touch)

    # ------------------------------------------------------------------ #
    def _finish_stroke(self):
        self._tracing = False
        app().audio.play_sfx("correct")
        self._ci += 1
        self._pi = 0
        self._redraw()
        if self._ci >= len(self._strokes):
            if self.on_complete:
                self.on_complete()
        else:
            self._play_demo()

    def _tol(self):
        _, _, side = self._box()
        return max(dp(40), side * 0.16)

    @staticmethod
    def _dist(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


class TracingScreen(BaseScreen):
    STAGE = 2
    GUIDE = "reading_rabbit"
    title = "Trace Letters"

    def __init__(self, **kwargs):
        self._target: Optional[ContentItem] = None
        super().__init__(**kwargs)

    def build(self):
        self.bg_top = config.PALETTE["tangerine"]
        char = app().content.character(self.GUIDE) if app() else {"id": self.GUIDE}
        self.mascot = Mascot(char=char, size_hint=(None, None), size=(dp(120), dp(150)),
                             pos_hint={"x": 0.02, "y": 0.04})
        self.content.add_widget(self.mascot)

        self.prompt_lbl = Label(text="", font_size=theme.FONT_TITLE, bold=True,
                                color=config.PALETTE["cream"], size_hint=(0.8, None),
                                height=dp(60), pos_hint={"center_x": 0.5, "top": 0.93})
        self.content.add_widget(self.prompt_lbl)

        # Reference tile (small) showing the letter + example word picture.
        self.ref = GlyphTile(glyph="", emoji="", size_hint=(None, None),
                             size=(dp(120), dp(150)), pos_hint={"right": 0.97, "top": 0.9})
        self.ref.bg_color = list(config.PALETTE["cream"])
        self.content.add_widget(self.ref)

        self.canvas_widget = TracingCanvas(on_complete=self._on_done,
                                           size_hint=(0.7, 0.62),
                                           pos_hint={"center_x": 0.5, "y": 0.16})
        self.content.add_widget(self.canvas_widget)

        self.replay = GlyphTile(glyph="🔊", on_tap=lambda *_: self._speak(),
                                size_hint=(None, None), size=(dp(80), dp(80)),
                                pos_hint={"x": 0.02, "top": 0.9})
        self.replay.bg_color = list(config.PALETTE["sun"])
        self.content.add_widget(self.replay)

        self.progress = ChunkyProgressBar(size_hint=(0.9, None), height=dp(22),
                                          pos_hint={"center_x": 0.5, "y": 0.05})
        self.progress.bar_color = list(config.PALETTE["tangerine"])
        self.content.add_widget(self.progress)

    def on_back(self):
        app().go("home")

    def refresh(self):
        if not app() or not app().session.profile:
            return
        self.mascot.idle()
        self.progress.value = app().session.stage_summary(self.STAGE).ratio
        self._next_letter()

    def _next_letter(self):
        session = app().session
        # Only pick letters we have stroke data for.
        item = session.next_item(self.STAGE, exclude=self._target.id if self._target else None)
        guard = 0
        while item and not tracing.get_strokes(item.label) and guard < 30:
            item = session.next_item(self.STAGE, exclude=item.id)
            guard += 1
        if not item:
            return
        self._target = item
        color = list(config.hex_rgba(item.color)) if item.color else list(config.PALETTE["tangerine"])
        self.ref.glyph = item.label
        self.ref.emoji = item.emoji
        self.ref.glyph_color = color
        self.canvas_widget.load(item.label, color)
        self.prompt_lbl.text = f"Trace the letter {item.label}!"
        Clock.schedule_once(lambda dt: self._speak(), 0.4)

    def _speak(self):
        if self._target:
            word = self._target.data.get("word", "")
            self.mascot.say(f"Trace the letter {self._target.label}. {self._target.label} is for {word}.",
                            key=self._target.id)

    def _on_done(self):
        outcome = app().session.answer(self.STAGE, self._target, True)
        self.mascot.react()
        self.mascot.say(f"You traced {self._target.label}! {outcome.encouragement}")
        self.star_counter.bump(outcome.result.stars_awarded)
        self.progress.value = app().session.stage_summary(self.STAGE).ratio
        self.celebrate(big=outcome.celebrate)
        if not outcome.celebrate:
            particles.star_pop(self.effects, self.canvas_widget.center)
        Clock.schedule_once(lambda dt: self._next_letter(), 1.9)
