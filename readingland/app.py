"""ReadingLandApp - the Kivy application shell.

Owns the long-lived services (Database, ContentLibrary, LearningSession,
AudioManager), the ScreenManager, and the global navigation helpers
(``go``, ``open_stage``). Screens stay thin by calling back into here.
"""
from __future__ import annotations

import os

from kivy.app import App
from kivy.uix.screenmanager import FadeTransition, ScreenManager

from . import config
from .core.audio import AudioManager
from .core.content import ContentLibrary
from .core.database import Database
from .core.session import LearningSession
from .ui import theme


class ReadingLandApp(App):
    title = "ReadingLand"

    def build(self):
        # Imported here (not at module top) so importing the app module never
        # forces a GL window - keeps headless import/CI clean.
        from kivy.core.window import Window

        theme.register_fonts()
        Window.clearcolor = config.PALETTE["sky"]

        # --- services -------------------------------------------------- #
        db_path = os.path.join(self.user_data_dir, config.DEFAULT_DB_NAME)
        self.db = Database(db_path)
        self.content = ContentLibrary()
        self.session = LearningSession(self.db, self.content)
        self.audio = AudioManager(enabled=True)

        # --- screens --------------------------------------------------- #
        self.sm = ScreenManager(transition=FadeTransition(duration=0.25))
        self._register_screens()

        # Start at profile select if any profiles exist, else splash->create.
        self.sm.current = "splash"
        return self.sm

    def on_start(self):
        self.audio.play_music("theme", loop=True, volume=0.25)

    def on_stop(self):
        if self.session.profile:
            self.session.end_session()
        self.db.close()

    # ------------------------------------------------------------------ #
    def _register_screens(self):
        # Imported here to avoid importing Kivy widgets at module import time
        # (keeps `python -c "import readingland.core"` clean).
        from .screens.splash import SplashScreen
        from .screens.profile_select import ProfileSelectScreen
        from .screens.home_map import HomeMapScreen
        from .screens.stage1_visual import Stage1Screen
        from .screens.stage2_alphabet import Stage2Screen
        from .screens.stage3_phonics import Stage3Screen
        from .screens.stage4_words import Stage4Screen
        from .screens.stage5_sentences import Stage5Screen
        from .screens.stage6_stories import Stage6Screen
        from .screens.rewards_room import RewardsRoomScreen
        from .screens.parent_dashboard import ParentDashboardScreen

        for cls, name in [
            (SplashScreen, "splash"),
            (ProfileSelectScreen, "profiles"),
            (HomeMapScreen, "home"),
            (Stage1Screen, "stage1"),
            (Stage2Screen, "stage2"),
            (Stage3Screen, "stage3"),
            (Stage4Screen, "stage4"),
            (Stage5Screen, "stage5"),
            (Stage6Screen, "stage6"),
            (RewardsRoomScreen, "rewards"),
            (ParentDashboardScreen, "parent"),
        ]:
            self.sm.add_widget(cls(name=name))

    # ------------------------------------------------------------------ #
    # Navigation API used by every screen
    # ------------------------------------------------------------------ #
    def go(self, screen_name: str, direction: str = "left"):
        self.sm.transition.direction = direction if hasattr(self.sm.transition, "direction") else "left"
        self.sm.current = screen_name

    def open_stage(self, stage_id: int):
        if not self.session.profile:
            self.go("profiles")
            return
        if not self.session.progress.is_unlocked(self.session.pid, stage_id):
            self.audio.play_sfx("locked")
            return
        self.go(f"stage{stage_id}")

    def select_profile(self, profile_id: int):
        self.session.set_profile(profile_id)
        self.go("home")


def run():  # pragma: no cover - GUI entry point
    ReadingLandApp().run()
