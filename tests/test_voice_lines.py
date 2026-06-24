"""The recorded voice manifest and the bundled audio must stay in lock-step.

The narrator pack is generated offline (scripts/generate_voice.py) and committed.
If it drifts from the manifest the app silently falls back to captions for a line
that was supposed to have a warm recording - so we assert every manifest key has a
rendered audio file on disk and there are no orphan files.
"""
import os

from readingland.core import voice_lines

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE_DIR = os.path.join(ROOT, "assets", "audio", "voice", "mabel")
AUDIO_EXTS = (".ogg", ".mp3", ".wav")


def test_keys_are_filesystem_safe():
    for key in voice_lines.all_lines():
        assert key == voice_lines.slugify(key) or key.startswith(("ln_", "greet_",
               "locked_", "retry_", "finish_")), key
        assert "/" not in key and " " not in key


def test_every_manifest_line_is_rendered():
    for key in voice_lines.all_lines():
        paths = [os.path.join(VOICE_DIR, key + ext) for ext in AUDIO_EXTS]
        assert any(os.path.exists(p) for p in paths), (
            f"no rendered audio for voice key {key!r} - run scripts/generate_voice.py")


def test_no_orphan_voice_files():
    keys = set(voice_lines.all_lines())
    if not os.path.isdir(VOICE_DIR):
        return
    for fn in os.listdir(VOICE_DIR):
        if fn.endswith(AUDIO_EXTS):
            key = os.path.splitext(fn)[0]
            assert key in keys, f"rendered file {fn!r} has no manifest line"


def test_encouragement_keys_resolve():
    # The runtime key_for() must produce keys that exist in the manifest.
    lines = voice_lines.all_lines()
    for text in voice_lines.ENCOURAGE_CORRECT + voice_lines.ENCOURAGE_RETRY:
        assert voice_lines.key_for(text) in lines
