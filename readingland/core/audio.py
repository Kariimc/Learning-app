"""Audio narration manager.

Supports two narration sources, chosen per-line at runtime:

1. **Recorded narration** - pre-rendered ``.ogg``/``.mp3`` voice-over files in
   ``assets/audio/voice/<voice_pack>/<key>.ogg``. Highest quality; used when the
   file exists. This is how shipping voice packs (Reading Rabbit, Ollie Owl...)
   are delivered.
2. **Text-to-speech fallback** - if no recording exists (e.g. a brand-new word a
   content author just added), the manager speaks via an available TTS backend
   (``pyttsx3`` offline, or platform TTS on Android/iOS). This guarantees *every*
   piece of content is narrated even before a voice actor records it.

The manager degrades gracefully: if neither Kivy audio nor any TTS backend is
present (headless CI), it becomes a silent no-op that still records what *would*
have been spoken, so it stays unit-testable.
"""
from __future__ import annotations

import os
from typing import List, Optional

from .. import config


class AudioManager:
    def __init__(self, assets_dir: str = config.ASSETS_DIR, enabled: bool = True):
        self.assets_dir = assets_dir
        self.enabled = enabled
        # Narrator voice pack: warm "fairy godmother" (Mabel) recordings keyed by
        # line. Falls back to TTS for any line without a recording.
        self.voice_pack = "mabel"
        self.spoken_log: List[str] = []   # what was narrated (for tests/captions)
        self._tts = None
        self._sound_cache = {}
        self._init_tts()

    # ------------------------------------------------------------------ #
    def _init_tts(self) -> None:
        if not self.enabled:
            return
        try:                                   # offline desktop TTS
            import pyttsx3  # type: ignore
            self._tts = pyttsx3.init()
            self._tts.setProperty("rate", config.TTS_RATE)
            self._select_warm_voice()
        except Exception:
            self._tts = None  # fall back to recordings / captions only

    def _select_warm_voice(self) -> None:
        """Prefer a gentle female voice so the TTS fallback feels less robotic."""
        try:
            voices = self._tts.getProperty("voices") or []
        except Exception:
            return
        preferred = ("zira", "hazel", "susan", "samantha", "female", "eva", "fiona")
        for v in voices:
            blob = f"{getattr(v, 'name', '')} {getattr(v, 'id', '')} " \
                   f"{getattr(v, 'gender', '')}".lower()
            if any(p in blob for p in preferred):
                try:
                    self._tts.setProperty("voice", v.id)
                except Exception:
                    pass
                return

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def voice_path(self, key: str) -> Optional[str]:
        for ext in (".ogg", ".mp3", ".wav"):
            p = os.path.join(self.assets_dir, "audio", "voice", self.voice_pack, key + ext)
            if config.asset_file_exists(p):
                return p
        return None

    def narrate(self, text: str, key: Optional[str] = None) -> None:
        """Speak a line - real recorded Mabel voice only.

        Order: the recording keyed by ``key``; else the line composed from
        per-word recordings; else (only if TTS fallback is allowed) TTS.
        With ``ALLOW_TTS_FALLBACK = False`` the child never hears a synthetic
        voice - an uncovered line is silent and the on-screen text carries it.
        """
        self.spoken_log.append(text)
        if not self.enabled:
            return
        path = self.voice_path(key) if key else None
        if config.PREFER_RECORDED_AUDIO and path:
            self._play_file(path)
            return
        if self.narrate_words(text):
            return
        if getattr(config, "ALLOW_TTS_FALLBACK", False):
            self._speak_tts(text)

    def narrate_words(self, text: str) -> bool:
        """Speak ``text`` as a sequence of recorded word clips.

        Returns True only when EVERY word has a real recording (single letters
        map to their letter_<x> clip); otherwise plays nothing.
        """
        import re
        words = [re.sub(r"[^a-z']", "", w.lower()) for w in text.split()]
        words = [w for w in words if w]
        if not words:
            return False
        paths = []
        for w in words:
            p = self.voice_path(w)
            if not p and len(w) == 1:
                p = self.voice_path(f"letter_{w}")
            if not p:
                return False
            paths.append(p)
        self._play_files_seq(paths)
        return True

    def _play_files_seq(self, paths, gap: float = 0.12) -> None:
        """Play recorded clips back to back."""
        if not paths:
            return
        try:
            from kivy.clock import Clock
        except Exception:
            for p in paths:
                self._play_file(p)
            return
        delay = 0.0
        for p in paths:
            Clock.schedule_once(lambda dt, p=p: self._play_file(p), delay)
            snd = self._load(p)
            delay += (snd.length if snd and snd.length and snd.length > 0
                      else 0.6) + gap

    def play_sfx(self, name: str) -> None:
        """Play a short sound effect from assets/audio/sfx/<name>.ogg."""
        if not self.enabled:
            return
        for ext in (".ogg", ".wav", ".mp3"):
            p = os.path.join(self.assets_dir, "audio", "sfx", name + ext)
            if config.asset_file_exists(p):
                self._play_file(p)
                return

    def play_music(self, name: str, loop: bool = True, volume: float = 0.4) -> None:
        if not self.enabled:
            return
        for ext in (".ogg", ".mp3"):
            p = os.path.join(self.assets_dir, "audio", "music", name + ext)
            if config.asset_file_exists(p):
                snd = self._load(p)
                if snd:
                    snd.loop = loop
                    snd.volume = volume
                    snd.play()
                return

    # ------------------------------------------------------------------ #
    # Backends (import Kivy lazily so core stays importable headless)
    # ------------------------------------------------------------------ #
    def _load(self, path: str):
        if path in self._sound_cache:
            return self._sound_cache[path]
        try:
            from kivy.core.audio import SoundLoader  # type: ignore
            snd = SoundLoader.load(path)
            self._sound_cache[path] = snd
            return snd
        except Exception:
            return None

    def _play_file(self, path: str) -> None:
        snd = self._load(path)
        if snd:
            try:
                snd.stop()
                snd.play()
            except Exception:
                pass

    def _speak_tts(self, text: str) -> None:
        if self._tts is None:
            return
        try:
            self._tts.stop()
            self._tts.say(text)
            self._tts.runAndWait()
        except Exception:
            pass
