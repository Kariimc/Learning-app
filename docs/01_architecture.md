# 1 · Application Architecture

ReadingLand uses a **layered architecture** with one strict dependency rule that
keeps the whole project testable, maintainable and AI-assist friendly:

> **`core` (the learning brain) never imports Kivy.**
> The UI depends on the core; the core never depends on the UI.

```
┌──────────────────────────────────────────────────────────────┐
│                         main.py / app.py                       │
│        ReadingLandApp  →  ScreenManager  +  global services    │
└───────────────┬───────────────────────────────┬───────────────┘
                │                                 │
        ┌───────▼────────┐                ┌───────▼────────┐
        │   screens/     │  uses widgets  │     ui/        │
        │  (Kivy views)  │───────────────▶│ widgets,       │
        │  splash, map,  │                │ particles,     │
        │  6 stages,     │                │ theme, assets  │
        │  rewards,      │                └───────┬────────┘
        │  parent        │                        │ (Kivy)
        └───────┬────────┘                        │
                │ calls LearningSession           │
        ┌───────▼─────────────────────────────────▼───────┐
        │                  core/  (NO Kivy)                 │
        │  session ─ progress ─ adaptive ─ rewards ─        │
        │  analytics ─ profiles ─ content ─ audio ─ database│
        └───────┬───────────────────────────────┬──────────┘
                │                                 │
        ┌───────▼────────┐                ┌───────▼────────┐
        │  content/*.json│                │  SQLite (local)│
        │  curriculum    │                │  user_data_dir │
        └────────────────┘                └────────────────┘
```

## Layers

### 1. App shell — `readingland/app.py`
`ReadingLandApp` (a Kivy `App`) owns the long-lived **services** and the
`ScreenManager`. It exposes the global navigation API (`go`, `open_stage`,
`select_profile`) so screens stay thin. Services created once at startup:

| Service | Responsibility |
|---------|----------------|
| `Database` | SQLite connection + schema (in `user_data_dir`) |
| `ContentLibrary` | Loads JSON curriculum + character roster |
| `LearningSession` | Facade composing the engine for the active child |
| `AudioManager` | Recorded narration + TTS fallback + SFX/music |

### 2. Core engine — `readingland/core/` (pure Python)
The "learning brain". No Kivy import anywhere, so it runs in headless CI and is
covered by unit tests. Components:

- **`content.py`** — loads/validates data-driven curriculum packs.
- **`database.py`** — idempotent SQLite schema + helpers; everything offline.
- **`profiles.py`** — multiple children, isolated progress.
- **`progress.py`** — records answers, advances mastery, awards stars, unlocks
  stages.
- **`adaptive.py`** — per-child difficulty, spaced-practice item selection,
  scaffolding (number of choices, hints).
- **`rewards.py`** — stickers, badges, character unlocks, treasure chests, daily
  goals (catalogue + rules).
- **`analytics.py`** — turns the event log into parent-dashboard reports.
- **`audio.py`** — narration source selection; degrades gracefully to captions.
- **`session.py`** — `LearningSession`, the single object the UI talks to. One
  `answer()` call records progress, updates difficulty, evaluates rewards and
  returns a tidy `TurnOutcome` for the screen to celebrate.

### 3. UI toolkit — `readingland/ui/`
Reusable, **oversized, child-friendly** Kivy widgets that only render state:
`BigButton`, `GlyphTile`, `Mascot`, `RoundedCard`, `ChunkyProgressBar`,
`StarCounter`, `ShapeWidget`; plus `particles` (confetti/bubbles/balloons/stars)
and `theme` (palette + type scale + emoji-font detection).

### 4. Screens — `readingland/screens/`
One Kivy `Screen` per view. `BaseScreen` paints the living animated background
and the top bar; subclasses add content. Stages 1/2/4 share `_matching.py`
(find-the-X game); Stages 3/5/6 are bespoke (blending, sentence karaoke,
storybook reader).

## Key data flows

**A child answers a question**
```
GlyphTile tap
  → screen._on_choice(item)
    → LearningSession.answer(stage, item, correct)
        → ProgressTracker.record_answer()   # mastery, stars, stage unlock
        → AdaptiveEngine.register_result()   # difficulty, streak
        → RewardSystem.evaluate_milestones() # new badges/stickers/characters
      ← TurnOutcome(result, new_rewards, celebrate, encouragement)
  → screen celebrates (particles + mascot.react + audio) and advances
```

**Picking the next question**
```
LearningSession.next_item(stage)
  → AdaptiveEngine.next_item()  # weight unseen/weak items higher (spaced practice)
LearningSession.build_choices(stage, target)
  → AdaptiveEngine.num_choices()  # 2/3/4 based on difficulty (scaffolding)
  → AdaptiveEngine.distractors()  # wrong options
```

## Why this shape?

- **Testability** — 100% of learning logic is unit-tested without a GPU.
- **Maintainability** — small single-responsibility modules; clear seams.
- **Extensibility** — add content via JSON; add a stage by appending to
  `config.STAGES` + a screen; add a reward by editing the catalogue.
- **AI-assist friendly** — each file is short, named for its job, and free of
  hidden cross-dependencies, so an agent can edit one piece safely.
