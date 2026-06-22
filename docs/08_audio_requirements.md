# 8 · Audio Requirements

ReadingLand is **audio-first**: every screen is narrated, every tap makes a
sound, and pronunciation guidance is built into the teaching. Audio is managed by
`readingland/core/audio.py` (`AudioManager`).

## Two narration sources (auto-selected)
1. **Recorded voice-over** (preferred) — pro/character voice files at
   `assets/audio/voice/<voice_pack>/<key>.{ogg,mp3,wav}`. Used whenever the file
   exists.
2. **Text-to-speech fallback** — `pyttsx3` offline on desktop, platform TTS on
   mobile. Guarantees *every* line is spoken even before it's recorded (e.g. a
   word an author just added). If no TTS backend exists, the app shows on-screen
   captions and stays silent rather than crashing.

```python
audio.narrate("This is the letter A.", key="A")
#  → plays voice/reading_rabbit/A.ogg if present, else speaks via TTS
```

## What needs narration
| Context | Example line |
|---------|--------------|
| Greetings | "Hi friend! Let's learn together!" |
| Instructions | "Find the letter A!", "Tap each sound." |
| Letter teaching | "A. Ah. Apple." |
| Blending | "c… a… t… cat!" |
| Word/sentence reading | "cat", "The cat runs." (word-by-word) |
| Story narration | full lines + character voices |
| Encouragement (correct) | "Great job!", "Fantastic reading!", "You did it!" |
| Encouragement (retry) | "Good try! Let's try again." (warm, never negative) |
| Rewards | "You earned a sticker!", "You filled the chest!" |

Encouragement pools live in `core/session.py` (`ENCOURAGE_CORRECT`,
`ENCOURAGE_RETRY`) and are spoken via the mascot.

## Sound effects (`play_sfx`)
`tap, pop, correct, wrong, chest, page, locked, sticker, badge, levelup`.
`wrong` must be **soft and non-punitive** (a gentle "boop", never a buzzer).

## Music (`play_music`)
Warm, loopable `theme` for menus (vol ~0.25); optional per-land ambient loops;
short `celebrate` jingle. Music ducks naturally because narration is short.

## Voice pack recording checklist
Record per voice pack (one per shipped character voice):

**Common keys:** `greet, correct, retry, goodbye, celebrate, sticker, chest,
badge, page_turn, the_end`.

**Per-item keys (by content id):**
- Stage 2: each letter `A`–`Z` (name + sound + word, e.g. "A. Ah. Apple.").
- Stage 3: each CVC word + its phoneme sounds.
- Stage 4: each word (`cat, dog, the, is, happy, …`).
- Stage 5: each sentence id (`s_cat_runs, …`) **and** each individual word for
  karaoke highlighting.
- Stage 6: each story line + per-word clips + interactive-object lines.

Any missing key → TTS fallback, so packs can ship incrementally.

## Pronunciation guidance
Letter `sound` fields use child-friendly phonetic spellings ("buh", "kuh",
"ah") rather than IPA, matching how the sounds are taught aloud. Blending plays
each phoneme then the whole word, modeling the blend.

## Technical
- Format: **OGG Vorbis** (Kivy `SoundLoader`), ~96–128 kbps; keep VO clips < 3 s.
- Sounds are **cached** after first load (`AudioManager._sound_cache`).
- All audio is **bundled** for offline use.
- A global **Sound On/Off** toggle lives in the parent dashboard
  (`AudioManager.enabled`); when off, narration logs to captions only.
- `AudioManager.spoken_log` records every narrated line — used by unit tests and
  available to drive an on-screen caption/subtitle accessibility feature.
