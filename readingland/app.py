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

        # --- TEMP on-device asset diagnostics ----------------------------- #
        # Shows, right on the tablet, exactly what the running APK sees for
        # fonts/art. Lets us tell an old APK (no banner) from a new one, and
        # whether emoji/art files actually shipped. Remove once verified.
        self._show_asset_diagnostics(Window)

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

    # ------------------------------------------------------------------ #
    # TEMP diagnostics — remove once assets are confirmed on-device.
    # ------------------------------------------------------------------ #
    BUILD_TAG = "DIAG-1"

    def _show_asset_diagnostics(self, Window):
        import glob
        from kivy.uix.label import Label
        from kivy.graphics import Color, Rectangle

        adir = config.ASSETS_DIR
        font_path = os.path.join(adir, "fonts", "NotoEmoji-Regular.ttf")
        try:
            emoji_ok = theme.register_fonts()
        except Exception as e:  # pragma: no cover - defensive
            emoji_ok = "ERR:%s" % e
        imgs = glob.glob(os.path.join(adir, "images", "**", "*.png"), recursive=True)
        audio = glob.glob(os.path.join(adir, "audio", "**", "*.mp3"), recursive=True)
        # A glyph the emoji font must cover; with markup it renders in the emoji
        # font while the rest stays readable. If it shows as a box the font
        # isn't rendering even though it registered.
        cat = "\U0001F431"
        cat_markup = ("[font=%s]%s[/font]" % (theme.EMOJI_FONT_NAME, cat)
                      if emoji_ok is True else cat)
        msg = (
            "[{tag}] test-glyph={cat}  fontfile={ff}  registered={reg}  "
            "imgs={ni}  audio={na}\nassets_dir exists={ex}".format(
                tag=self.BUILD_TAG,
                cat=cat_markup,
                ff=os.path.exists(font_path),
                reg=emoji_ok,
                ni=len(imgs),
                na=len(audio),
                ex=os.path.isdir(adir),
            )
        )
        lbl = Label(
            text=msg, font_size="14sp", color=(1, 1, 1, 1), markup=True,
            size_hint=(1, None), height="60dp", halign="center", valign="middle",
            pos_hint={"x": 0, "top": 1},
        )
        lbl.bind(size=lambda *_: setattr(lbl, "text_size", lbl.size))
        with lbl.canvas.before:
            Color(0, 0, 0, 0.66)
            self._diag_rect = Rectangle(pos=lbl.pos, size=lbl.size)
        lbl.bind(
            pos=lambda *_: setattr(self._diag_rect, "pos", lbl.pos),
            size=lambda *_: setattr(self._diag_rect, "size", lbl.size),
        )
        Window.add_widget(lbl)

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
        from .screens.tracing import TracingScreen
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
            (TracingScreen, "tracing"),
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
