# 14 · Folder Structure

```
Learning-app/
├── main.py                     # Entry point: `python main.py`
├── requirements.txt            # Runtime + dev deps
├── buildozer.spec              # Android/iOS packaging config
├── README.md                   # Overview + deliverables index
├── .gitignore
│
├── readingland/                # ── Application package ──
│   ├── __init__.py
│   ├── app.py                  # ReadingLandApp (Kivy App) + navigation API
│   ├── config.py               # Palette, stages, tunables (NO Kivy)
│   │
│   ├── core/                   # Pure-Python engine (NO Kivy — testable)
│   │   ├── __init__.py
│   │   ├── database.py         # SQLite persistence + schema
│   │   ├── content.py          # Data-driven curriculum loader
│   │   ├── profiles.py         # Multiple child profiles
│   │   ├── progress.py         # Mastery, stars, stage unlocking
│   │   ├── adaptive.py         # Adaptive difficulty + spaced practice
│   │   ├── rewards.py          # Stickers, badges, chests, daily goals
│   │   ├── analytics.py        # Parent-dashboard reporting
│   │   ├── audio.py            # Recorded narration + TTS fallback + SFX
│   │   └── session.py          # LearningSession facade (UI entry point)
│   │
│   ├── ui/                     # Reusable Kivy widgets & effects
│   │   ├── __init__.py
│   │   ├── theme.py            # Fonts, type scale, emoji detection
│   │   ├── widgets.py          # BigButton, GlyphTile, Mascot, cards, bars
│   │   └── particles.py        # Confetti, bubbles, balloons, stars
│   │
│   ├── screens/                # One Kivy Screen per view
│   │   ├── __init__.py
│   │   ├── base.py             # BaseScreen: living bg + top bar
│   │   ├── splash.py
│   │   ├── profile_select.py
│   │   ├── home_map.py
│   │   ├── _matching.py        # Shared find/match game (S1/S2/S4)
│   │   ├── stage1_visual.py
│   │   ├── stage2_alphabet.py
│   │   ├── stage3_phonics.py
│   │   ├── stage4_words.py
│   │   ├── stage5_sentences.py
│   │   ├── stage6_stories.py
│   │   ├── rewards_room.py
│   │   └── parent_dashboard.py # + ParentGate
│   │
│   └── content/                # ── Data-driven curriculum (JSON) ──
│       ├── characters.json
│       ├── stage1_visual.json
│       ├── alphabet.json
│       ├── phonics.json
│       ├── words.json
│       ├── sentences.json
│       └── stories.json
│
├── assets/                     # ── Art & audio (placeholders → production) ──
│   ├── README.md               # Asset specifications
│   ├── images/                 # characters/ backgrounds/ ui/ cards/ stories/ effects/
│   ├── audio/                  # voice/<pack>/ sfx/ music/
│   └── fonts/
│
├── docs/                       # ── Design & technical documentation (this set) ──
│   ├── 01_architecture.md  …  17_content_authoring.md
│
├── scripts/
│   └── smoke_run.py            # Headless end-to-end screen test + screenshots
│
└── tests/                      # Pytest suite for the pure-Python engine
    ├── conftest.py
    ├── test_content.py
    ├── test_progress.py
    ├── test_adaptive.py
    └── test_rewards.py
```

## Conventions
- **One responsibility per file**, short modules — easy for humans and AI agents.
- **`core` never imports Kivy**; **content is JSON, not code**.
- Screen files are named `stageN_<key>.py`; the registry is in `app.py`.
- Stage metadata (title, content file, guide) is declared once in
  `config.STAGES` — adding a stage touches `config.py`, a content file, and one
  new screen.
- Asset lookups are convention-based (`content id == file stem`), so dropping in
  art/audio needs no code changes.
