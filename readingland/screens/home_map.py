"""Home world map - the hub.

Six 'lands' (one per stage) laid out as a path. Unlocked lands glow and show a
progress bar; locked lands show a padlock. Buttons reach the Rewards Room and the
daily-goal chest. Reading Rabbit greets the child.
"""
from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from .. import config
from ..core.voice_lines import NAV_LINES
from ..ui import theme
from ..ui.icons import Icon, IconButton
from ..ui.widgets import BigButton, ChunkyProgressBar, GlyphTile, Mascot, RoundedCard
from .base import BaseScreen, app

STAGE_ICONS = {1: "👀", 2: "🔤", 3: "🔊", 4: "📕", 5: "📑", 6: "📖"}


class HomeMapScreen(BaseScreen):
    title = "ReadingLand"
    bg_image_key = "map"

    def build(self):
        # Top-bar button switches child profile (a 'swap' icon, not the home one).
        self.back_btn.icon = "switch"

        # Daily goal + rewards buttons live in the top bar area.
        self.rewards_btn = IconButton(icon="gift", size=(theme.touch_size(), theme.touch_size()),
                                      size_hint=(None, None),
                                      pos_hint={"x": 0.02, "y": 0.02},
                                      bg_color=list(config.PALETTE["sun"]),
                                      icon_color=list(config.PALETTE["coral"]),
                                      on_tap=lambda *_: app().go("rewards"))
        self.content.add_widget(self.rewards_btn)

        self.daily_lbl = Label(text="", font_size=theme.FONT_LABEL, bold=True,
                               color=config.PALETTE["cream"], **theme.outline(1.5),
                               pos_hint={"center_x": 0.5, "y": 0.02}, size_hint=(0.5, None),
                               height=dp(40))
        self.content.add_widget(self.daily_lbl)

        char = app().content.character("reading_rabbit") if app() else {"id": "reading_rabbit"}
        self.mascot = Mascot(char=char, size_hint=(None, None), size=(dp(120), dp(150)),
                             pos_hint={"right": 0.99, "y": 0.02})
        self.content.add_widget(self.mascot)

        # Scrollable land path.
        self.scroll = ScrollView(size_hint=(1, 0.8), pos_hint={"x": 0, "top": 0.86})
        self.path = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(16),
                              padding=[dp(20), dp(20)])
        self.path.bind(minimum_height=self.path.setter("height"))
        self.scroll.add_widget(self.path)
        self.content.add_widget(self.scroll)

    def on_back(self):
        app().go("profiles")

    def refresh(self):
        if not app().session.profile:
            app().go("profiles")
            return
        self.title_lbl.text = f"Hi, {app().session.profile.name}!"
        self.mascot.idle()
        self._build_path()
        goal = app().session.daily_goal()
        self.daily_lbl.text = f"Daily goal: {goal['done']}/{goal['goal']}"
        Clock.schedule_once(lambda dt: self.mascot.say(
            NAV_LINES["greet_home"], key="greet_home"), 0.4)

    def _build_path(self):
        self.path.clear_widgets()
        session = app().session
        for stage in config.STAGES:
            sid = stage["id"]
            summ = session.stage_summary(sid)
            unlocked = summ.unlocked

            card = RoundedCard(orientation="horizontal", size_hint=(1, None),
                               height=dp(120), padding=dp(12), spacing=dp(12))
            card.bg_color = list(config.STAGE_COLORS[sid]) if unlocked else list(config.PALETTE["shadow"])

            icon = self._land_icon(STAGE_ICONS.get(sid, "⭐"), unlocked,
                                   self._make_open(sid, unlocked))
            card.add_widget(icon)

            info = BoxLayout(orientation="vertical", spacing=dp(4))
            info.add_widget(Label(text=stage["title"], font_size=theme.FONT_HEADING,
                                  bold=True, color=config.PALETTE["cream"],
                                  **theme.outline(1.5), halign="left", size_hint=(1, 0.4)))
            sub = "Locked - keep learning to open!" if not unlocked else stage["subtitle"]
            info.add_widget(Label(text=sub, font_size=theme.FONT_LABEL,
                                  color=config.PALETTE["cream"], size_hint=(1, 0.3)))
            bar = ChunkyProgressBar(size_hint=(1, None), height=dp(18))
            bar.value = summ.ratio
            bar.bar_color = list(config.PALETTE["sun"])
            info.add_widget(bar)
            info.add_widget(Label(text=f"{summ.mastered}/{summ.total} mastered",
                                  font_size=dp(14), color=config.PALETTE["cream"],
                                  size_hint=(1, 0.2)))
            card.add_widget(info)
            self.path.add_widget(card)

        # Bonus activity: letter tracing (available once Letter Land is unlocked).
        self._add_tracing_card(session)

    def _add_tracing_card(self, session):
        unlocked = session.progress.is_unlocked(session.pid, 2)
        card = RoundedCard(orientation="horizontal", size_hint=(1, None),
                           height=dp(120), padding=dp(12), spacing=dp(12))
        card.bg_color = list(config.PALETTE["tangerine"]) if unlocked else list(config.PALETTE["shadow"])
        icon = self._land_icon("✏️", unlocked, self._make_open_tracing(unlocked),
                               vector="pencil")
        card.add_widget(icon)
        info = BoxLayout(orientation="vertical", spacing=dp(4))
        info.add_widget(Label(text="Trace Letters", font_size=theme.FONT_HEADING, bold=True,
                              color=config.PALETTE["cream"], **theme.outline(1.5),
                              size_hint=(1, 0.5)))
        sub = "Practice writing letters with your finger!" if unlocked \
            else "Opens with Letter Land!"
        info.add_widget(Label(text=sub, font_size=theme.FONT_LABEL,
                              color=config.PALETTE["cream"], size_hint=(1, 0.5)))
        card.add_widget(info)
        self.path.add_widget(card)

    def _land_icon(self, emoji, unlocked, on_tap, vector=None):
        """Crisp land icon: a vector glyph (lock when locked) on a cream tile."""
        if not unlocked:
            btn = IconButton(icon="lock", size_hint=(None, 1), width=dp(96),
                             bg_color=list(config.PALETTE["cream"]),
                             icon_color=list(config.PALETTE["shadow"][:3]) + [0.6],
                             on_tap=on_tap)
            return btn
        if vector:
            btn = IconButton(icon=vector, size_hint=(None, 1), width=dp(96),
                             bg_color=list(config.PALETTE["cream"]),
                             icon_color=list(config.PALETTE["tangerine"]),
                             on_tap=on_tap)
            return btn
        tile = GlyphTile(glyph=emoji, emoji="", size_hint=(None, 1), width=dp(96),
                         on_tap=on_tap)
        tile.bg_color = list(config.PALETTE["cream"])
        return tile

    def _make_open_tracing(self, unlocked):
        def handler(tile):
            if unlocked:
                app().go("tracing")
            else:
                app().audio.play_sfx("locked")
                self.mascot.say(NAV_LINES["locked_tracing"], key="locked_tracing")
        return handler

    def _make_open(self, stage_id, unlocked):
        def handler(tile):
            if unlocked:
                app().open_stage(stage_id)
            else:
                app().audio.play_sfx("locked")
                self.mascot.say(NAV_LINES["locked_stage"], key="locked_stage")
        return handler
