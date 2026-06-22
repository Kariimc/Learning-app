"""The recorded voice manifest and the fetch script must stay in lock-step.

If these drift, the app silently falls back to TTS for a line that was supposed
to have a warm recording - so we assert every manifest key has a matching
download entry and vice-versa.
"""
import importlib.util
import os

from readingland.core import voice_lines

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_fetch_assets():
    path = os.path.join(ROOT, "scripts", "fetch_assets.py")
    spec = importlib.util.spec_from_file_location("fetch_assets", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_keys_are_filesystem_safe():
    for key in voice_lines.all_lines():
        assert key == voice_lines.slugify(key) or key.startswith(("ln_", "greet_",
               "locked_", "retry_", "finish_")), key
        assert "/" not in key and " " not in key


def test_every_manifest_line_has_a_download():
    fa = _load_fetch_assets()
    voiced = {p for p in fa.ASSETS if p.startswith("assets/audio/voice/mabel/")}
    for key in voice_lines.all_lines():
        rel = f"assets/audio/voice/mabel/{key}.mp3"
        assert rel in voiced, f"missing download for voice key {key!r}"


def test_no_orphan_voice_downloads():
    fa = _load_fetch_assets()
    keys = set(voice_lines.all_lines())
    for p in fa.ASSETS:
        if p.startswith("assets/audio/voice/mabel/"):
            key = os.path.splitext(os.path.basename(p))[0]
            assert key in keys, f"download {key!r} has no manifest line"


def test_encouragement_keys_resolve():
    # The runtime key_for() must produce keys that exist in the manifest.
    lines = voice_lines.all_lines()
    for text in voice_lines.ENCOURAGE_CORRECT + voice_lines.ENCOURAGE_RETRY:
        assert voice_lines.key_for(text) in lines
