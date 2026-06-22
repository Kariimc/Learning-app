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
from ..ui import theme
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
        self.scroll = ScrollView(size_hint=(1, 0.86), pos_hint={"x": 0, "top": 0.86})
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

        self.column.add_widget(self._kpi_card(report))
        self.column.add_widget(self._stage_card(report))
        self.column.add_widget(self._activity_card(report))
        self.column.add_widget(self._manage_card())

    # ------------------------------------------------------------------ #
    def _card(self, title):
        card = RoundedCard(orientation="vertical", size_hint=(1, None), padding=dp(14),
                           spacing=dp(8))
        card.bg_color = list(config.PALETTE["cream"])
        card.add_widget(Label(text=title, font_size=theme.FONT_HEADING, bold=True,
                              color=config.PALETTE["ink"], size_hint=(1, None), height=dp(40)))
        return card

    def _kpi_card(self, report):
        card = self._card(f"{report.profile_name} — overview")
        kpis = [
            ("Overall progress", f"{report.overall_percent}%"),
            ("Current land", report.current_stage_title),
            ("Stars earned", f"⭐ {report.total_stars}"),
            ("Accuracy", f"{round(report.accuracy * 100)}%"),
            ("Items mastered", f"{report.items_mastered}/{report.items_total}"),
            ("Day streak", f"🔥 {report.active_days_streak}"),
            ("Time (7 days)", f"{report.minutes_last_7_days} min"),
        ]
        grid = GridLayout(cols=2, size_hint=(1, None), spacing=dp(6))
        grid.bind(minimum_height=grid.setter("height"))
        for k, v in kpis:
            row = BoxLayout(size_hint=(1, None), height=dp(40))
            row.add_widget(Label(text=k, font_size=theme.FONT_BODY, halign="left",
                                 color=config.PALETTE["ink"]))
            row.add_widget(Label(text=str(v), font_size=theme.FONT_BODY, bold=True,
                                 color=config.PALETTE["sky_deep"]))
            grid.add_widget(row)
        card.add_widget(grid)
        card.height = dp(60) + dp(40) * (len(kpis) // 2 + 1)
        return card

    def _stage_card(self, report):
        card = self._card("Progress by land")
        for s in report.stage_breakdown:
            row = BoxLayout(orientation="vertical", size_hint=(1, None), height=dp(54),
                            spacing=dp(2))
            top = BoxLayout(size_hint=(1, None), height=dp(26))
            lock = "" if s["unlocked"] else "  🔒"
            top.add_widget(Label(text=f"{s['title']}{lock}", font_size=theme.FONT_LABEL,
                                 bold=True, color=config.PALETTE["ink"], halign="left"))
            top.add_widget(Label(text=f"{s['mastered']}/{s['total']} ({s['percent']}%)",
                                 font_size=theme.FONT_LABEL, color=config.PALETTE["ink"]))
            row.add_widget(top)
            bar = ChunkyProgressBar(size_hint=(1, None), height=dp(16))
            bar.value = s["percent"] / 100.0
            bar.bar_color = list(config.STAGE_COLORS[s["stage"]])
            row.add_widget(bar)
            card.add_widget(row)
        card.height = dp(70) + dp(58) * len(report.stage_breakdown)
        return card

    def _activity_card(self, report):
        card = self._card("Recent activity")
        if not report.recent_activity:
            card.add_widget(Label(text="No activity yet.", font_size=theme.FONT_BODY,
                                  color=config.PALETTE["ink"], size_hint=(1, None), height=dp(30)))
            card.height = dp(110)
            return card
        for a in report.recent_activity[:8]:
            mark = "✓" if a["correct"] else ("·" if a["correct"] is None else "↻")
            text = f"{a['when']}  {mark}  {a['kind']} {a['item'] or ''}".strip()
            card.add_widget(Label(text=text, font_size=theme.FONT_LABEL, halign="left",
                                  color=config.PALETTE["ink"], size_hint=(1, None), height=dp(28)))
        card.height = dp(70) + dp(28) * min(8, len(report.recent_activity))
        return card

    def _manage_card(self):
        card = self._card("Settings")
        session = app().session
        audio_on = app().audio.enabled
        row = BoxLayout(size_hint=(1, None), height=theme.touch_size(), spacing=dp(10))
        row.add_widget(BigButton(text=f"Sound: {'On' if audio_on else 'Off'}",
                                 size_hint=(0.5, 1), bg_color=list(config.PALETTE["mint"]),
                                 on_tap=lambda *_: self._toggle_audio()))
        row.add_widget(BigButton(text="Switch child", size_hint=(0.5, 1),
                                 bg_color=list(config.PALETTE["sky"]),
                                 on_tap=lambda *_: app().go("profiles")))
        card.add_widget(row)
        card.height = dp(70) + theme.touch_size()
        return card

    def _toggle_audio(self):
        app().audio.enabled = not app().audio.enabled
        self.refresh()
