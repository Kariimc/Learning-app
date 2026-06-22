#!/usr/bin/env python3
"""Headless smoke test: build the real app, drive it through every screen,
capture screenshots, then exit cleanly. Run under a virtual display:

    xvfb-run -s "-screen 0 1280x900x24" python scripts/smoke_run.py

Exits non-zero if any screen fails to build or a navigation step raises.
"""
import os
import sys

os.environ.setdefault("KIVY_NO_ARGS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kivy.clock import Clock  # noqa: E402

from readingland.app import ReadingLandApp  # noqa: E402

SHOTS_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")
os.makedirs(SHOTS_DIR, exist_ok=True)

errors = []


class SmokeApp(ReadingLandApp):
    def on_start(self):
        from kivy.core.window import Window
        # Ensure a child profile exists and is active.
        if not self.session.profiles.list():
            prof = self.session.profiles.create("Smoke Kid", avatar="reading_rabbit")
        else:
            prof = self.session.profiles.list()[0]
        self.session.set_profile(prof.id)

        # Pre-seed some progress so dashboards/rewards have data to render.
        for letter in ["A", "B", "C", "D", "E"]:
            item = self.content.item(2, letter)
            for _ in range(3):
                self.session.answer(2, item, True)

        self._steps = [
            "splash", "profiles", "home", "stage1", "stage2", "stage3",
            "stage4", "stage5", "stage6", "rewards", "parent", "home",
        ]
        self._i = 0
        Clock.schedule_interval(self._tick, 0.6)

    def _tick(self, dt):
        from kivy.core.window import Window
        if self._i >= len(self._steps):
            print("SMOKE OK: visited", len(self._steps), "screens")
            self.stop()
            return False
        name = self._steps[self._i]
        try:
            self.sm.current = name
            # Force a layout/draw tick then snapshot.
            shot = os.path.join(SHOTS_DIR, f"{self._i:02d}_{name}.png")
            Window.screenshot(name=shot.replace(".png", "_%(counter)s.png"))
            print("visited", name)
        except Exception as exc:  # noqa: BLE001
            errors.append((name, repr(exc)))
            print("ERROR on", name, repr(exc))
        self._i += 1
        return True


if __name__ == "__main__":
    SmokeApp().run()
    if errors:
        print("SMOKE FAILED:", errors)
        sys.exit(1)
    sys.exit(0)
