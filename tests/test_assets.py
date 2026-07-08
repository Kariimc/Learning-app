"""The real generated assets must be present and always win - never fallback.

Guards the owner's standing rule: the app ships the Higgsfield art + Mabel
voice pack; placeholder/emoji/TTS looks must never appear when assets exist,
and a checkout with un-pulled LFS stubs must fail loudly.
"""
import os

import pytest

from readingland import config
from readingland.core.audio import AudioManager
from readingland.ui import assets


def test_verify_assets_passes_on_real_checkout():
    assets.verify_assets()


def test_required_assets_are_real_bytes_not_stubs():
    for parts in assets._REQUIRED_ASSETS:
        p = os.path.join(config.ASSETS_DIR, *parts)
        assert os.path.isfile(p), f"missing required asset: {p}"
        assert not config.is_lfs_pointer(p), f"LFS stub, not real bytes: {p}"


def test_resolvers_return_real_art_for_all_stages_and_guides():
    for stage in config.STAGES:
        bg = assets.background_image(stage["key"])
        assert bg and os.path.getsize(bg) > 10_000, f"no real bg for {stage['key']}"
        portrait = assets.character_image(stage["guide"])
        assert portrait and os.path.getsize(portrait) > 10_000, \
            f"no real portrait for {stage['guide']}"


def test_mabel_voice_pack_resolves_to_recordings():
    am = AudioManager(enabled=False)
    for key in ("greet_home", "letter_a", "cat", "ln_you_did_it"):
        p = am.voice_path(key)
        assert p and p.endswith(".mp3") and os.path.getsize(p) > 1_000, \
            f"no real Mabel recording for {key}"


def test_narrate_prefers_recording_over_tts(monkeypatch):
    am = AudioManager(enabled=True)
    played, spoken = [], []
    monkeypatch.setattr(am, "_play_file", lambda p: played.append(p))
    monkeypatch.setattr(am, "_speak_tts", lambda t: spoken.append(t))
    am.narrate("Cat", key="cat")
    assert played and not spoken, "recorded Mabel line must win over TTS"


def test_lfs_pointer_stub_is_rejected_loudly(tmp_path):
    stub = tmp_path / "bg_map.png"
    stub.write_bytes(
        b"version https://git-lfs.github.com/spec/v1\n"
        b"oid sha256:" + b"0" * 64 + b"\nsize 12345\n"
    )
    assert config.is_lfs_pointer(str(stub))
    with pytest.raises(RuntimeError, match="git lfs"):
        config.asset_file_exists(str(stub))


def test_verify_assets_fails_on_stub_checkout(tmp_path):
    d = tmp_path / "assets" / "images" / "backgrounds"
    d.mkdir(parents=True)
    (d / "bg_map.png").write_bytes(
        b"version https://git-lfs.github.com/spec/v1\noid sha256:"
        + b"0" * 64 + b"\nsize 1\n"
    )
    with pytest.raises(RuntimeError):
        assets.verify_assets(str(tmp_path / "assets"))
