# 15 · Technical Design Documentation

## Tech stack
| Concern | Choice | Why |
|---------|--------|-----|
| Language | Python 3.11 | simple, AI-assist friendly, fast to iterate |
| UI | Kivy 2.3 | true cross-platform touch (Android/iOS/desktop), GPU canvas, gesture support |
| Storage | SQLite (stdlib) | zero-dep, offline, transactional, crash-safe |
| Audio | Kivy `SoundLoader` + `pyttsx3`/platform TTS | recorded VO with universal TTS fallback |
| Packaging | Buildozer (Android), kivy-ios (iOS) | standard Kivy mobile toolchains |
| Tests | pytest | engine is pure-Python → fast headless CI |

## Design tenets
1. **Separation of brain and skin.** `core/` (logic) has *zero* Kivy imports; the
   UI renders state and forwards taps. This makes the learning logic fully
   unit-testable and lets the art be replaced freely.
2. **Data-driven content.** Curriculum and characters are JSON. Adding content
   never edits Python (`docs/17`).
3. **Single facade.** Screens talk only to `LearningSession`. One `answer()` call
   does progress + adaptivity + rewards and returns a `TurnOutcome`.
4. **Convention over configuration.** Asset lookups, stage registry and content
   ids follow predictable patterns so new pieces "just work".
5. **Fail soft.** Missing audio backend → captions; missing art → emoji/shapes;
   missing content pack → skipped with a validation warning. The app never
   crashes on absent assets.

## Module responsibilities (core)
```
session.LearningSession   facade: holds active profile, composes the rest
progress.ProgressTracker  mastery, stars, stage unlock; emits AnswerResult
adaptive.AdaptiveEngine   difficulty/streak, next_item, num_choices, distractors
rewards.RewardSystem      catalogue + milestone rules (idempotent grants)
analytics.Analytics       event log → DashboardReport
profiles.ProfileManager   CRUD for child profiles
content.ContentLibrary    load/validate JSON packs + characters
database.Database         SQLite schema, transactions, event log
audio.AudioManager        narration source selection, SFX, music
```

## Key types (dataclasses)
`ContentItem`, `ContentPack`, `Profile`, `AnswerResult`, `StageSummary`,
`TurnOutcome`, `RewardGrant`, `DashboardReport`, `StageState`. Small, explicit,
serializable-shaped — easy to reason about and test.

## Concurrency & threading
The UI runs on Kivy's main thread; `Clock.schedule_*` drives timed sequences
(auto-advance, karaoke). The DB connection uses `check_same_thread=False` with
transactions serialized through `Database.tx()`. Audio playback is non-blocking;
TTS `runAndWait` is short and acceptable on the main loop (can be moved to a
worker thread if a recorded-only build is shipped).

## Error handling & resilience
- Every DB write is wrapped in a transaction with rollback on error.
- `AudioManager` and asset loaders swallow backend errors and degrade.
- `ContentLibrary.validate()` returns human-readable problems (covered by a test)
  so broken content is caught in CI, not on a child's screen.

## Performance
- Particle widgets self-remove on animation complete (no leaks); counts capped.
- Sounds cached after first load.
- Property tweens (`Animation`) instead of per-frame Python where possible.
- Target 60 fps on mid-range Android tablets; ambient cloud drift at 30 fps.

## Testing strategy
- **Unit (headless):** content validity, mastery/stars/unlock, adaptivity,
  rewards idempotency, profile isolation — `pytest`.
- **Integration (headless GUI):** `scripts/smoke_run.py` builds the real app
  under `xvfb`, visits every screen, captures screenshots, exits non-zero on any
  failure. Good for CI gating.
- **Manual device pass:** tap ergonomics, audio, 60fps (checklist in `docs/10`).

## Security & privacy
- No network permission; no analytics SDKs; no accounts; no ads/IAP.
- All data is local SQLite in `user_data_dir`.
- Parent area gated by a math challenge; child data never leaves the device.

## Extensibility seams (where to add things)
| Want to add… | Touch |
|--------------|-------|
| Letters/words/stories | `content/*.json` only |
| A whole new stage | `config.STAGES` + a content file + one screen |
| A reward type | `rewards.py` catalogue + a rule |
| A new character/voice | `characters.json` + `assets/audio/voice/<pack>/` |
| A new mini-game | new screen subclassing `BaseScreen`, reuse widgets |
| Localization | parallel content packs + voice packs + font |
