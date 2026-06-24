# 🐰 ReadingLand

**An animated, interactive cartoon world that takes children from recognizing
pictures all the way to reading storybooks independently.**

ReadingLand is a premium-feeling, fully **offline**, monetization-free early
literacy app built in **Python + Kivy** for **Android tablets, iPads and
touchscreen PCs**. Every screen is alive with color, characters, animation and
narration. It is usable by a 2-year-old: large buttons, one-tap interaction, no
typing, no reading required to navigate.

---

## The learning journey (6 stages)

| Stage | Land | Teaches | Guide |
|------:|------|---------|-------|
| 1 | 👀 Look & Learn | Shapes, colors, animals, objects (visual recognition) | Reading Rabbit |
| 2 | 🔤 Letter Land | Letter names & sounds, beginning phonics | Reading Rabbit |
| 3 | 🔊 Sound Forest | Blending sounds into words (c-a-t → cat) | Benny Bear |
| 4 | 📕 Word Town | Reading first words & sight words | Penny Penguin |
| 5 | 📑 Sentence River | Reading sentences with word highlighting | Penny Penguin |
| 6 | 📖 Story Sky | Read-along interactive storybooks | Ollie Owl |

A child advances by **mastering** items (3 correct = mastered). Master ~70% of a
land and the **next land unlocks**, with a character + sticker celebration.
Mistakes are **never** punished — a wrong tap just gently asks them to try again.

> Full progression detail: [`docs/13_readiness_roadmap.md`](docs/13_readiness_roadmap.md)

---

## Quick start (desktop)

```bash
pip install -r requirements.txt
python main.py                   # runs with the committed felt art + voice pack
```

All art and narration are **generated offline** (no API, no cloud) and committed
to the repo, so the app runs with zero network. To re-generate them yourself:

```bash
pip install pillow numpy piper-tts        # build-time only
python scripts/generate_art.py            # felt buttons, mascots, backgrounds, icon
python scripts/generate_voice.py          # narrator voice pack (offline neural TTS)
python scripts/generate_sfx.py            # taps, chimes, page-turns + theme music
```

Run the headless self-test (builds the real app, visits every screen, captures
screenshots — needs a display or `xvfb`):

```bash
xvfb-run -s "-screen 0 1280x900x24" python scripts/smoke_run.py
```

Run the unit tests (pure-Python engine, no display needed):

```bash
pytest
```

Package for Android / iPad: see [`docs/10_deployment.md`](docs/10_deployment.md).

---

## Architecture at a glance

```
readingland/
├── core/        Pure-Python engine (NO Kivy) — testable headless
│   ├── database.py    SQLite persistence (offline)
│   ├── content.py     Data-driven curriculum loader
│   ├── profiles.py    Multiple child profiles
│   ├── progress.py    Mastery, stars, stage unlocking
│   ├── adaptive.py    Adaptive difficulty + spaced practice
│   ├── rewards.py     Stickers, badges, chests, daily goals
│   ├── analytics.py   Parent-dashboard reporting
│   ├── audio.py       Recorded narration + TTS fallback
│   └── session.py     LearningSession facade (UI talks to this)
├── ui/          Reusable Kivy widgets, particles, placeholder assets
├── screens/     One Screen per view (splash, map, 6 stages, letter-tracing,
│                rewards, parent)
└── content/     JSON curriculum packs — add content without touching code
```

**The golden rule:** `core` never imports Kivy, and **content is data, not
code**. New letters/words/stories/characters are added by editing JSON.

> Deep dive: [`docs/01_architecture.md`](docs/01_architecture.md) ·
> [`docs/15_technical_design.md`](docs/15_technical_design.md)

---

## Art & audio — a cohesive felt / plush look, generated offline

ReadingLand's art set is a hand-crafted **felt toy** world: buttons that look
like stuffed felt pillows, mascots built from stitched felt cut-outs, and soft
felt-craft land backgrounds. Every piece is **generated procedurally with
Pillow** (`scripts/generate_art.py`) — multiplicative felt-shading so a single
tintable texture turns any palette colour into plush felt, fibre-grain noise, and
cream stitch outlines. No image-gen API, no CDN, fully reproducible.

The narrator voice is likewise rendered **fully offline** by a small neural TTS
(`scripts/generate_voice.py`, Piper — with `pico2wave`/`espeak-ng` fallbacks):
every line in the manifest is baked to a small `.ogg` and bundled, so there is
**no API key, no per-call cost, and no runtime TTS dependency** on any platform.

Anything not yet generated still degrades gracefully to programmatic placeholders
+ on-screen captions, so the app never crashes on a missing file.

> Asset specs: [`docs/06_asset_list.md`](docs/06_asset_list.md) ·
> [`assets/README.md`](assets/README.md)

---

## Deliverables index

| # | Deliverable | Where |
|--:|-------------|-------|
| 1 | App architecture | [`docs/01_architecture.md`](docs/01_architecture.md) |
| 2 | Curriculum map | [`docs/02_curriculum_map.md`](docs/02_curriculum_map.md) |
| 3 | Character bible | [`docs/03_character_bible.md`](docs/03_character_bible.md) |
| 4 | UI/UX mockups | [`docs/04_ui_ux_mockups.md`](docs/04_ui_ux_mockups.md) |
| 5 | Screen-by-screen flow | [`docs/05_screen_flow.md`](docs/05_screen_flow.md) |
| 6 | Asset list | [`docs/06_asset_list.md`](docs/06_asset_list.md) |
| 7 | Animation requirements | [`docs/07_animation_requirements.md`](docs/07_animation_requirements.md) |
| 8 | Audio requirements | [`docs/08_audio_requirements.md`](docs/08_audio_requirements.md) |
| 9 | Database structure | [`docs/09_database_structure.md`](docs/09_database_structure.md) |
| 10 | Python source code | `readingland/`, `main.py` |
| 11 | Mobile deployment | [`docs/10_deployment.md`](docs/10_deployment.md) |
| 12 | Monetization-free | No ads/IAP anywhere; no network permission (`buildozer.spec`) |
| 13 | Parent dashboard | [`docs/11_parent_dashboard.md`](docs/11_parent_dashboard.md) |
| 14 | Progress tracking | [`docs/12_progress_tracking.md`](docs/12_progress_tracking.md) |
| 15 | Readiness roadmap | [`docs/13_readiness_roadmap.md`](docs/13_readiness_roadmap.md) |
| 16 | Folder structure | [`docs/14_folder_structure.md`](docs/14_folder_structure.md) |
| 17 | Technical design | [`docs/15_technical_design.md`](docs/15_technical_design.md) |
| 18 | Future expansion | [`docs/16_future_roadmap.md`](docs/16_future_roadmap.md) |
| + | Content authoring guide | [`docs/17_content_authoring.md`](docs/17_content_authoring.md) |

---

## Design principles

- **Extremely visual** — animated sky, drifting clouds, particle confetti,
  bubbles, balloons and stars; no static screens.
- **Audio-first** — every interaction is narrated; every tap makes a sound.
- **Toddler-usable** — generous tap targets, one-tap, no reading to navigate.
- **Never punish** — only encouragement; rewards are earned, never lost.
- **Offline & private** — all data stays on-device in local SQLite.
- **Modular & AI-friendly** — small files, clear seams, data-driven content.
