#!/usr/bin/env python3
"""Render ReadingLand's narrator voice pack — fully OFFLINE, no API, no cloud.

The pivot: instead of fetching an AI voice pack from a CDN, we *render every
narrated line on-device* with an offline text-to-speech engine and bundle the
resulting audio in the app. No network at runtime, no API keys, no per-call
cost, and it works the same on Android where Python TTS engines don't.

Engines tried, best first (all offline / no API):
  1. **Piper** — small neural TTS (warm, natural). Model is pulled once from a
     GitHub *release* (not HuggingFace) into a local cache; ~56 MB, not committed.
  2. **pico2wave** (SVOX Pico) — tiny, clear, classic kids'-app voice.
  3. **espeak-ng** — always-available formant synth (robotic but never fails).

Output: ``assets/audio/voice/<pack>/<key>.ogg`` for every line in
``readingland.core.voice_lines.all_lines()`` — exactly the keys the app's
``AudioManager`` looks up (it falls back to on-screen captions for anything
missing). Re-run any time; pass ``--force`` to overwrite.

    python scripts/generate_voice.py                 # auto-pick best engine
    python scripts/generate_voice.py --engine pico   # force an engine
    python scripts/generate_voice.py --pack mabel    # voice-pack folder name
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from readingland.core import voice_lines  # noqa: E402

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "readingland", "voices")
# Piper voices used to ship as GitHub release assets (pre-HuggingFace). That host
# stays reachable where HuggingFace is blocked, so we fetch the model from here.
PIPER_NAME = "en-us-amy-low"
PIPER_URL = ("https://github.com/rhasspy/piper/releases/download/v0.0.2/"
             "voice-en-us-amy-low.tar.gz")
LENGTH_SCALE = 1.08  # >1 = a touch slower / calmer, nice for a narrator


# --------------------------------------------------------------------------- #
# Engines  (each returns a callable synth(text, wav_path) -> bool)
# --------------------------------------------------------------------------- #
def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def ensure_piper_model() -> str | None:
    onnx = os.path.join(CACHE, f"{PIPER_NAME}.onnx")
    cfg = onnx + ".json"
    if not (os.path.exists(onnx) and os.path.exists(cfg)):
        os.makedirs(CACHE, exist_ok=True)
        tgz = os.path.join(CACHE, "voice.tar.gz")
        print(f"  downloading Piper voice '{PIPER_NAME}' (~56 MB, one time)...")
        try:
            req = urllib.request.Request(PIPER_URL, headers={"User-Agent": "readingland"})
            with urllib.request.urlopen(req, timeout=120) as r, open(tgz, "wb") as fh:
                shutil.copyfileobj(r, fh)
            with tarfile.open(tgz) as tf:
                tf.extractall(CACHE)
        except Exception as exc:  # noqa: BLE001
            print(f"  Piper model download failed ({exc}); will try another engine.")
            return None
        finally:
            if os.path.exists(tgz):
                os.remove(tgz)
    # Nudge the pace to a calmer narrator cadence.
    try:
        with open(cfg) as fh:
            data = json.load(fh)
        data.setdefault("inference", {})["length_scale"] = LENGTH_SCALE
        with open(cfg, "w") as fh:
            json.dump(data, fh)
    except Exception:  # noqa: BLE001
        pass
    return onnx if os.path.exists(onnx) else None


def piper_engine():
    try:
        from piper import PiperVoice
    except Exception:  # noqa: BLE001
        return None
    onnx = ensure_piper_model()
    if not onnx:
        return None
    try:
        voice = PiperVoice.load(onnx, config_path=onnx + ".json")
    except Exception as exc:  # noqa: BLE001
        print(f"  Piper load failed ({exc}); trying another engine.")
        return None

    def synth(text: str, wav_path: str) -> bool:
        with wave.open(wav_path, "wb") as wf:
            voice.synthesize_wav(text, wf)
        return True

    return ("piper:" + PIPER_NAME, synth)


def pico_engine():
    if not _have("pico2wave"):
        return None

    def synth(text: str, wav_path: str) -> bool:
        subprocess.run(["pico2wave", "-l", "en-US", "-w", wav_path, text],
                       check=True, capture_output=True)
        return True

    return ("pico2wave", synth)


def espeak_engine():
    cmd = "espeak-ng" if _have("espeak-ng") else ("espeak" if _have("espeak") else None)
    if not cmd:
        return None

    def synth(text: str, wav_path: str) -> bool:
        # gentle: slower words-per-minute, a softer female-ish voice variant
        subprocess.run([cmd, "-v", "en-us+f3", "-s", "150", "-p", "60",
                        "-w", wav_path, text], check=True, capture_output=True)
        return True

    return ("espeak", synth)


ENGINES = {"piper": piper_engine, "pico": pico_engine, "espeak": espeak_engine}


def pick_engine(name: str):
    order = [name] if name != "auto" else ["piper", "pico", "espeak"]
    for key in order:
        eng = ENGINES[key]()
        if eng:
            return eng
    return None


# --------------------------------------------------------------------------- #
def to_ogg(wav_path: str, ogg_path: str) -> str:
    """Compress wav -> ogg (small, Kivy/Android-friendly). Falls back to wav."""
    if not _have("ffmpeg"):
        return wav_path
    try:
        subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-ac", "1",
                        "-c:a", "libvorbis", "-qscale:a", "4", ogg_path],
                       check=True, capture_output=True)
        os.remove(wav_path)
        return ogg_path
    except Exception:  # noqa: BLE001
        return wav_path


def main() -> int:
    ap = argparse.ArgumentParser(description="Render ReadingLand narration offline (no API).")
    ap.add_argument("--engine", choices=["auto", "piper", "pico", "espeak"], default="auto")
    ap.add_argument("--pack", default="mabel", help="voice-pack folder name")
    ap.add_argument("--force", action="store_true", help="overwrite existing audio")
    args = ap.parse_args()

    eng = pick_engine(args.engine)
    if not eng:
        print("No offline TTS engine available. Install one of:\n"
              "  pip install piper-tts        # neural, best quality\n"
              "  apt-get install libttspico-utils   # pico2wave\n"
              "  apt-get install espeak-ng", file=sys.stderr)
        return 1
    engine_name, synth = eng

    out_dir = os.path.join(ROOT, "assets", "audio", "voice", args.pack)
    os.makedirs(out_dir, exist_ok=True)
    lines = voice_lines.all_lines()
    print(f"Rendering {len(lines)} lines with [{engine_name}] -> {os.path.relpath(out_dir, ROOT)}")

    made = skipped = failed = 0
    tmp_wav = os.path.join(out_dir, "_tmp.wav")
    for key, text in sorted(lines.items()):
        ogg = os.path.join(out_dir, key + ".ogg")
        if os.path.exists(ogg) and not args.force:
            skipped += 1
            continue
        try:
            synth(text, tmp_wav)
            final = to_ogg(tmp_wav, ogg)
            made += 1
            print(f"  OK  {os.path.basename(final):28s} “{text}”")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  FAIL {key}: {exc}", file=sys.stderr)
    if os.path.exists(tmp_wav):
        os.remove(tmp_wav)

    print(f"\nDone: {made} rendered, {skipped} skipped, {failed} failed. Engine: {engine_name}")
    print("The app plays these automatically; missing lines fall back to captions.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
