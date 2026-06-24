#!/usr/bin/env python3
"""Synthesize ReadingLand's sound effects + theme music — offline, no API.

The brief is *audio-first*: "every tap makes a sound." These are generated from
pure math with numpy (gentle, kid-friendly, never harsh — wrong answers get a
soft encouraging "boop", not a buzzer) and written as small ``.ogg`` files that
``core/audio.py`` plays by name. No samples, no API, no network.

    python scripts/generate_sfx.py        # writes assets/audio/{sfx,music}/*.ogg

Build-time only (numpy + ffmpeg for ogg encoding); the app just plays the files.
"""
from __future__ import annotations

import os
import struct
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
TWO_PI = 2 * np.pi

# Pentatonic-friendly note frequencies (Hz) — consonant in any combination.
N = {"C4": 261.63, "D4": 293.66, "E4": 329.63, "G4": 392.00, "A4": 440.00,
     "C5": 523.25, "D5": 587.33, "E5": 659.25, "G5": 783.99, "A5": 880.00,
     "C6": 1046.50, "E6": 1318.51, "C3": 130.81, "G3": 196.00, "E3": 164.81}


def _t(dur):
    return np.linspace(0, dur, int(SR * dur), False)


def bell(freq, dur, decay=6.0, vol=0.5):
    """A soft bell/marimba tone: fundamental + gentle harmonics, exp decay."""
    t = _t(dur)
    w = (np.sin(TWO_PI * freq * t)
         + 0.5 * np.sin(TWO_PI * 2 * freq * t)
         + 0.22 * np.sin(TWO_PI * 3 * freq * t))
    e = np.exp(-t * decay)
    e *= np.clip(t / 0.004, 0, 1)            # tiny attack so it doesn't click
    return (w * e * vol).astype(np.float32)


def sweep(f0, f1, dur, vol=0.5):
    t = _t(dur)
    freq = np.linspace(f0, f1, t.size)
    phase = np.cumsum(TWO_PI * freq / SR)
    e = np.exp(-t * 18) * np.clip(t / 0.003, 0, 1)
    return (np.sin(phase) * e * vol).astype(np.float32)


def noise_swish(dur, vol=0.4):
    """Soft paper-turn: shaped white noise with a smooth rise-fall envelope."""
    n = int(SR * dur)
    rng = np.random.default_rng(7)
    x = rng.normal(0, 1, n).astype(np.float32)
    # smooth it (simple moving average) for an airy, not hissy, texture
    k = 24
    x = np.convolve(x, np.ones(k) / k, mode="same")
    t = _t(dur)
    e = np.sin(np.pi * t / dur) ** 2
    return (x / (np.abs(x).max() or 1) * e * vol).astype(np.float32)


def mix(*arrs):
    """Sum buffers of differing lengths (zero-padded to the longest)."""
    n = max(a.size for a in arrs)
    out = np.zeros(n, np.float32)
    for a in arrs:
        out[: a.size] += a
    return out


def seq(notes, gap=0.0, **kw):
    """Concatenate (freq, dur) bell notes into one buffer."""
    parts = []
    for freq, dur in notes:
        parts.append(bell(freq, dur, **kw))
        if gap:
            parts.append(np.zeros(int(SR * gap), np.float32))
    return np.concatenate(parts)


def chord_pad(freqs, dur, vol=0.5):
    """A soft sustained chord with a slow shimmer — calm background bed."""
    t = _t(dur)
    out = np.zeros(t.size, np.float32)
    for i, f in enumerate(freqs):
        lfo = 0.85 + 0.15 * np.sin(TWO_PI * (0.12 + 0.03 * i) * t)  # gentle tremolo
        out += np.sin(TWO_PI * f * t) * lfo
        out += 0.3 * np.sin(TWO_PI * 2 * f * t) * lfo
    return (out / (np.abs(out).max() or 1) * vol).astype(np.float32)


def loopify(x, fade=1.0):
    """Make a seamless loop: cross-fade the tail back over the head."""
    f = int(SR * fade)
    f = min(f, x.size // 3)
    head, tail = x[:f].copy(), x[-f:].copy()
    ramp = np.linspace(0, 1, f, dtype=np.float32)
    x[:f] = tail * (1 - ramp) + head * ramp
    return x[:-f]


def normalize(x, peak=0.9):
    m = np.abs(x).max() or 1.0
    return (x / m * peak).astype(np.float32)


def write_ogg(x, name, folder):
    out_dir = os.path.join(ROOT, "assets", "audio", folder)
    os.makedirs(out_dir, exist_ok=True)
    wav = os.path.join(out_dir, name + ".wav")
    ogg = os.path.join(out_dir, name + ".ogg")
    data = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    try:
        subprocess.run(["ffmpeg", "-y", "-i", wav, "-c:a", "libvorbis", "-qscale:a", "4", ogg],
                       check=True, capture_output=True)
        os.remove(wav)
        target = ogg
    except Exception:
        target = wav  # keep wav if ffmpeg missing (Kivy plays wav too)
    print(f"  OK  {os.path.relpath(target, ROOT)}  ({x.size / SR:.2f}s)")


def build_sfx():
    print("Sound effects:")
    # tap: soft short wood-block "tok"
    write_ogg(normalize(bell(N["A4"], 0.10, decay=40, vol=0.6), 0.7), "tap", "sfx")
    # pop: little bubble pop (quick upward blip)
    write_ogg(normalize(mix(sweep(320, 880, 0.09), bell(N["E5"], 0.06, decay=45, vol=0.3)), 0.8),
              "pop", "sfx")
    # correct: bright rising major arpeggio
    write_ogg(normalize(seq([(N["C5"], 0.12), (N["E5"], 0.12), (N["G5"], 0.20)], decay=6)),
              "correct", "sfx")
    # wrong: gentle, encouraging two-note "boo-boop" (never harsh)
    write_ogg(normalize(seq([(N["E4"], 0.16), (N["C4"], 0.22)], decay=7, vol=0.5), 0.75),
              "wrong", "sfx")
    # locked: soft low muted double-blip
    write_ogg(normalize(seq([(N["G3"], 0.12), (N["G3"], 0.16)], gap=0.02, decay=10, vol=0.5), 0.7),
              "locked", "sfx")
    # page: airy paper turn
    write_ogg(normalize(noise_swish(0.24), 0.7), "page", "sfx")
    # chest: magical sparkle arpeggio
    write_ogg(normalize(seq([(N["C5"], 0.10), (N["E5"], 0.10), (N["G5"], 0.10),
                             (N["C6"], 0.12), (N["E6"], 0.30)], decay=5)), "chest", "sfx")


def build_music():
    print("Theme music:")
    # A calm, seamless C-major pad bed — soft enough to sit under narration.
    pad = chord_pad([N["C4"], N["E4"], N["G4"], N["C5"]], 13.0, vol=0.5)
    # add a sparse, gentle music-box motif over the top (pentatonic, never clashes)
    motif = [("C6", 0.0), ("G5", 1.6), ("E5", 3.0), ("A5", 4.6),
             ("G5", 6.2), ("C6", 7.8), ("E5", 9.2), ("D5", 10.8)]
    bed = pad.copy()
    for note, start in motif:
        s = int(SR * start)
        tone = bell(N[note], 1.2, decay=3.0, vol=0.22)
        bed[s:s + tone.size] += tone[: bed.size - s]
    theme = loopify(normalize(bed, 0.8), fade=1.2)
    write_ogg(theme, "theme", "music")


def main():
    build_sfx()
    build_music()
    print("\nDone. The app plays these by name (taps, rewards, page turns, theme).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
