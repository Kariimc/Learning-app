"""Splash / welcome screen. Big logo, dancing mascot, 'tap anywhere to start'."""
from __future__ import annotations

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.label import Label

from .. import config
from ..ui import particles, theme
from ..ui.widgets import Mascot
from .base import BaseScreen, app


class SplashScreen(BaseScreen):
    show_topbar = False

    def build(self):
        self.bg_top = config.PALETTE["bubblegum"]
        self.bg_bottom = config.PALETTE["grape"]

        self.logo = Label(text="ReadingLand", font_size=dp(64), bold=True,
                          color=config.PALETTE["ink"],
                          pos_hint={"center_x": 0.5, "center_y": 0.84})
        self.content.add_widget(self.logo)

        self.tagline = Label(text="From pictures to stories!", font_size=theme.FONT_HEADING,
                             color=config.PALETTE["ink"],
                             pos_hint={"center_x": 0.5, "center_y": 0.76})
        self.content.add_widget(self.tagline)

        # Reading Rabbit stands on wool, like everything else in this sky.
        char = app().content.character("reading_rabbit") if app() else {"id": "reading_rabbit"}
        self.mascot = Mascot(char=char, cloud=True, size_hint=(None, None),
                             size=(dp(300), dp(400)),
                             pos_hint={"center_x": 0.5, "center_y": 0.44})
        self.content.add_widget(self.mascot)

        # Ink, not sun-yellow. The invitation sat in the brightest part of the
        # golden sky and read as a smudge; yellow on gold is not a colour pair.
        self.tap_lbl = Label(text="Tap anywhere to start!", font_size=theme.FONT_TITLE,
                             bold=True, color=config.PALETTE["ink"],
                             pos_hint={"center_x": 0.5, "center_y": 0.12})
        self.content.add_widget(self.tap_lbl)

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.mascot.idle()
        Clock.schedule_once(lambda dt: self.mascot.say(
            "Hi friend! I'm Reading Rabbit. Let's learn together!", key="greet"), 0.4)
        # never below half: the sky under this line is at its brightest and a
        # 30% ink line disappeared into it entirely
        pulse = (Animation(opacity=0.55, d=0.7) + Animation(opacity=1.0, d=0.7))
        pulse.repeat = True
        pulse.start(self.tap_lbl)
        Clock.schedule_once(lambda dt: particles.rising_bubbles(self.effects, 10), 0.2)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app().go("profiles")
            return True
        return super().on_touch_down(touch)
