# 5 · Screen-by-Screen Flow

All screens are registered in `app.py` and switched via `App.go(name)`. Names:
`splash, profiles, home, stage1..stage6, rewards, parent`.

## Navigation graph

```
              ┌──────────┐
              │  splash  │  (tap anywhere)
              └────┬─────┘
                   ▼
              ┌──────────┐   👪 + math gate    ┌──────────┐
        ┌────▶│ profiles │────────────────────▶│  parent  │
        │     └────┬─────┘                      └────┬─────┘
        │   select child                             │ back
        │          ▼                                 ▼
   🔄   │     ┌──────────┐◀──────────────────────────┘
   switch│    │   home   │  (world map / hub)
        └─────┤  (map)   │
              └─┬─┬─┬─────┘
       open land│ │ │ 🎁 rewards
        ┌───────┘ │ └─────────────┐
        ▼         ▼                ▼
   ┌─────────┐  ...           ┌──────────┐
   │ stage1  │  stage2-6      │ rewards  │
   └────┬────┘                └────┬─────┘
        │ ← back                   │ ← back
        └──────────┬───────────────┘
                   ▼
                 home
```

## Per-screen contract

| Screen | Entry | Primary action | Exit |
|--------|-------|----------------|------|
| **splash** | app start | tap anywhere | → profiles |
| **profiles** | from splash / "switch child" / parent | tap child / "New" / "Parents" | → home / → parent (gated) |
| **home** | after profile chosen | tap unlocked land · 🎁 · 🔄 | → stageN / rewards / profiles |
| **stage1–6** | tap a land | answer activities | ← back → home |
| **tracing** | ✏️ Trace Letters card on map | finger-trace letter strokes | ← back → home |
| **rewards** | 🎁 from home | view collection · open daily chest | ← back → home |
| **parent** | 👪 + correct math gate | read analytics · settings | ← back → home |

The **tracing** activity reinforces Stage 2: completing a letter's strokes records
a correct answer for that letter, so it feeds the same mastery / stars / rewards
loop. Stroke geometry is defined in `core/tracing.py`; the trace box, dotted
guide, green start dot and animated demo live in `screens/tracing.py`.

## Activity loop (inside any stage)

```
on_pre_enter
  → refresh(): mascot.idle(); update progress bar; _next_round()
_next_round
  → session.next_item()         # adaptive, spaced
  → session.build_choices()     # adaptive count of distractors
  → render prompt + choices
  → mascot narrates the target
[child taps a choice]
  correct → lock; green flash; session.answer(correct=True)
          → star bump; particles; mascot.react()
          → if milestone: announce reward
          → after ~1.6s: _next_round()
  wrong   → coral flash; session.answer(correct=False)
          → "Good try!"; re-narrate; stay on same item (never blocked)
```

There is no "game over", no timer pressure, no failure screen. The loop simply
continues until the child taps **back**. Progress, stars and rewards persist
instantly to SQLite, so closing the app mid-activity loses nothing
(auto-save by design).

## Stage-specific deviations
- **Stage 3** adds a phoneme-tap pre-step before the picture choice.
- **Stage 5** runs a karaoke read-along before the picture choice; a **Read it!**
  button replays it.
- **Stage 6** has a **library → reader** sub-flow with page nav (◀ / 🔊 / ▶);
  finishing the last page masters the book and returns to the library.

## Session lifecycle & auto-save
- `select_profile()` starts a session timer (`LearningSession._session_start`).
- `app.on_stop()` logs the session duration (powers "time on task" analytics) and
  closes the DB. Every `answer()` is already committed immediately, so the app is
  crash-safe and resumes exactly where the child left off.
