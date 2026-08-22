"""Parent dashboard + child-lock gate.

``ParentGate`` is a quick multiplication challenge that keeps pre-readers out.
The dashboard shows the local analytics report (progress, accuracy, streak, time,
per-stage breakdown, recent activity) and basic profile/settings management.

Everything is computed on-device from the local SQLite log - nothing is uploaded.
"""
from __future__ import annotations

import random
from typing import Callable

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView

from .. import config
from ..ui import sky, theme
from ..ui.widgets import BigButton, ChunkyProgressBar, RoundedCard
from .base import BaseScreen, app


class ParentGate(ModalView):
    """A simple math gate. 'For grown-ups: what is A x B?'"""

    def __init__(self, on_success: Callable, **kwargs):
        super().__init__(size_hint=(0.8, 0.6), auto_dismiss=True, **kwargs)
        self._on_success = on_success
        self.a, self.b = random.randint(3, 9), random.randint(3, 9)
        self.answer = self.a * self.b

        card = RoundedCard(orientation="vertical", padding=dp(18), spacing=dp(12))
        card.bg_color = list(config.PALETTE["cream"])
        card.add_widget(Label(text="For grown-ups", font_size=theme.FONT_TITLE, bold=True,
                              color=config.PALETTE["ink"], size_hint=(1, 0.2)))
        card.add_widget(Label(text=f"What is  {self.a} x {self.b}?",
                              font_size=theme.FONT_HEADING, color=config.PALETTE["ink"],
                              size_hint=(1, 0.2)))
        opts = self._options()
        grid = GridLayout(cols=2, spacing=dp(12), size_hint=(1, 0.6))
        for val in opts:
            btn = BigButton(text=str(val), size_hint=(1, 1),
                            bg_color=list(config.PALETTE["sky"]),
                            on_tap=self._make_check(val))
            grid.add_widget(btn)
        card.add_widget(grid)
        self.add_widget(card)

    def _options(self):
        opts = {self.answer}
        while len(opts) < 4:
            opts.add(self.answer + random.randint(-12, 12))
        opts = [o for o in opts if o > 0]
        random.shuffle(opts)
        return opts[:4] if self.answer in opts[:4] else [self.answer] + opts[:3]

    def _make_check(self, val):
        def handler(btn):
            if val == self.answer:
                self.dismiss()
                self._on_success()
            else:
                self.a, self.b = random.randint(3, 9), random.randint(3, 9)
                self.answer = self.a * self.b
                self.dismiss()
        return handler


class ParentDashboardScreen(BaseScreen):
    title = "Parent Dashboard"

    def build(self):
        self.bg_top = config.PALETTE["ink"]
        self.bg_bottom = config.PALETTE["sky_deep"]
        self.scroll = ScrollView(size_hint=(1, 0.90), pos_hint={"x": 0, "top": 0.90})
        self.column = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(14),
                                padding=dp(18))
        self.column.bind(minimum_height=self.column.setter("height"))
        self.scroll.add_widget(self.column)
        self.content.add_widget(self.scroll)

    def on_back(self):
        app().go("home")

    def refresh(self):
        if not app().session.profile:
            app().go("profiles")
            return
        report = app().session.analytics.report(app().session.pid)
        self.column.clear_widgets()

        self.column.add_widget(self._heading(f"{report.profile_name} — overview"))
        self.column.add_widget(self._kpi_clouds(report))
        self.column.add_widget(self._heading("Progress by land"))
        self.column.add_widget(self._land_clouds(report))
        self.column.add_widget(self._heading("Recent activity"))
        for w in self._activity_lines(report):
            self.column.add_widget(w)
        self.column.add_widget(self._heading("Settings"))
        self.column.add_widget(self._settings_row())

    # ------------------------------------------------------------------ #
    # Every figure stands on its own cloud. The cream cards this replaced
    # were panels laid over the sky — the method Kariim rejected outright.
    # ------------------------------------------------------------------ #
    def _heading(self, text):
        return Label(text=text, font_size=theme.FONT_HEADING, bold=True,
                     color=config.PALETTE["ink"], size_hint=(1, None), height=dp(56))

    def _kpi_clouds(self, report):
        kpis = [
            (f"{report.overall_percent}%", "Overall progress"),
            (report.current_stage_title, "Current land"),
            (str(report.total_stars), "Stars earned"),
            (f"{round(report.accuracy * 100)}%", "Accuracy"),
            (f"{report.items_mastered}/{report.items_total}", "Items mastered"),
            (f"{report.active_days_streak}", "Day streak"),
            (f"{report.minutes_last_7_days} min", "Time, 7 days"),
        ]
        grid = GridLayout(cols=4, size_hint=(1, None), spacing=dp(4))
        grid.bind(minimum_height=grid.setter("height"))
        for i, (value, name) in enumerate(kpis):
            grid.add_widget(sky.Standing(label=value, caption=name,
                                         which=(i % 2) + 1, size_hint=(1, None),
                                         height=dp(150),
                                         label_size=theme.FONT_BODY))
        return grid

    def _land_clouds(self, report):
        grid = GridLayout(cols=3, size_hint=(1, None), spacing=dp(4))
        grid.bind(minimum_height=grid.setter("height"))
        keys = {st["id"]: st["key"] for st in config.STAGES}
        for i, s in enumerate(report.stage_breakdown):
            art = sky.land_art(keys.get(s["stage"], ""))
            note = f"{s['mastered']}/{s['total']}  ({s['percent']}%)"
            if not s["unlocked"]:
                note = "Locked · " + note
            grid.add_widget(sky.Standing(art=art or None, label=s["title"],
                                         caption=note, which=(i % 2) + 1,
                                         caption_color=list(config.PALETTE["ink"]),
                                         dim=not s["unlocked"], size_hint=(1, None),
                                         height=dp(230),
                                         label_size=theme.FONT_LABEL))
        return grid

    def _activity_lines(self, report):
        """Plain lines on the sky. A parent reads words, not glyphs — the
        ticks and flames here rendered as empty boxes on this laptop."""
        if not report.recent_activity:
            return [Label(text="No activity yet.", font_size=theme.FONT_BODY,
                          color=config.PALETTE["ink"], size_hint=(1, None),
                          height=dp(40))]
        out = []
        for a in report.recent_activity[:8]:
            mark = {True: "right", False: "again", None: "seen"}[a["correct"]]
            text = f"{a['when']}   {mark}   {a['kind']} {a['item'] or ''}".strip()
            out.append(Label(text=text, font_size=theme.FONT_LABEL,
                             color=config.PALETTE["ink"], size_hint=(1, None),
                             height=dp(34)))
        return out

    def _settings_row(self):
        audio_on = app().audio.enabled
        row = BoxLayout(size_hint=(1, None), height=theme.touch_size(), spacing=dp(10))
        row.add_widget(BigButton(text=f"Sound: {'On' if audio_on else 'Off'}",
                                 size_hint=(0.5, 1), bg_color=list(config.PALETTE["mint"]),
                                 on_tap=lambda *_: self._toggle_audio()))
        row.add_widget(BigButton(text="Switch child", size_hint=(0.5, 1),
                                 bg_color=list(config.PALETTE["sky"]),
                                 on_tap=lambda *_: app().go("profiles")))
        return row

    def _toggle_audio(self):
        app().audio.enabled = not app().audio.enabled
        self.refresh()
