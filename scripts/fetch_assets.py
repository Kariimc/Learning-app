#!/usr/bin/env python3
"""Generate ReadingLand's assets locally — offline, no API, no CDN.

**Pivot:** ReadingLand used to *download* an AI-generated art + voice pack from a
content-delivery network. It now **generates everything on-device** instead:

  * felt / plush-toy art  -> ``scripts/generate_art.py``   (Pillow)
  * narrator voice pack   -> ``scripts/generate_voice.py`` (offline neural TTS)

Both sets of assets are committed to the repo, so a fresh clone already has them
and the app runs with **zero network**. This script is kept under its old name so
existing docs/commands still work — it simply runs the two generators:

    python scripts/fetch_assets.py     # == generate_art.py + generate_voice.py

Build-time requirements (not needed to *run* the app, only to regenerate):
    pip install pillow numpy piper-tts
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    rc = 0
    for script in ("generate_art.py", "generate_voice.py"):
        print(f"\n=== {script} ===")
        rc |= subprocess.call([sys.executable, os.path.join(HERE, script)])
    if rc:
        print("\nSomething didn't generate cleanly — the app still runs with the "
              "committed assets (and falls back to placeholders/captions for any gap).",
              file=sys.stderr)
    else:
        print("\nAll assets generated. Run `python main.py` to see and hear the app.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
