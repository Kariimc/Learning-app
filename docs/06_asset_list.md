# 6 · Master Asset List

This is the production art/audio bill of materials. The app **runs today** with
programmatic placeholders (emoji + drawn shapes + type); production swaps in the
assets below **without layout changes** (the theme is fixed). Drop files into
`assets/` using the naming conventions here and they are picked up automatically.

Art style across everything: **cohesive, colorful, rounded cartoon** — soft
shapes, chunky outlines, big friendly eyes, the `config.PALETTE` colors.

---

## 1. Character artwork — `assets/images/characters/<id>/`
Per character (`reading_rabbit, benny_bear, penny_penguin, ollie_owl,
milo_monkey`), a sprite sheet / pose set:

| Pose | Use |
|------|-----|
| `idle` (2–3 frames) | gentle breathing/wiggle loop |
| `happy` | correct answer reaction |
| `encourage` | gentle "try again" |
| `point` | pointing at a word/letter |
| `celebrate` | milestone / reward |
| `talk` (2 frames) | mouth open/closed while narrating |

Format: PNG with transparency, ~1024×1024 master, or a `.atlas` sheet. Recommend
Spine/DragonBones rigs for smooth animation (optional — frame sheets work too).

## 2. Background artwork — `assets/images/backgrounds/`
One themed parallax background per land + shared sky pieces:

| File | Screen |
|------|--------|
| `sky_gradient.png` (or runtime gradient) | global base |
| `clouds_*.png` (3–4) | drifting cloud layer |
| `bg_stage1_meadow.png` | Look & Learn |
| `bg_stage2_letterland.png` | Letter Land |
| `bg_stage3_forest.png` | Sound Forest |
| `bg_stage4_town.png` | Word Town |
| `bg_stage5_river.png` | Sentence River |
| `bg_stage6_night_sky.png` | Story Sky |
| `bg_rewards_room.png` | Rewards Room |

## 3. UI assets — `assets/images/ui/`
`app_icon.png` (1024²), `presplash.png`, button shapes (or runtime rounded
rects), `star.png`, `star_empty.png`, progress-bar caps, `lock.png`,
`speaker.png`, `back_arrow.png`, `chest_closed.png`, `chest_open.png`,
`badge_frame.png`, `sticker_slot.png`.

## 4. Content picture cards — `assets/images/cards/`
One illustration per teachable item that has a picture (Stages 1, 2 example
words, 3 CVC words, 4 nouns/verbs, story scenes). Naming mirrors content ids,
e.g. `apple.png`, `cat.png`, `nest.png`, `story_cat_nap_p1.png`. Until provided,
the matching emoji renders.

## 5. Sound effects — `assets/audio/sfx/<name>.ogg`
| Name | Trigger |
|------|---------|
| `tap` | any tile tap |
| `pop` | button press |
| `correct` | right answer |
| `wrong` | gentle wrong (soft, non-negative) |
| `chest` | open treasure chest |
| `page` | storybook page turn |
| `locked` | tapping a locked land |
| `sticker`, `badge`, `levelup` | reward stings |

## 6. Music — `assets/audio/music/<name>.ogg`
`theme` (home/menus, warm & loopable), optional per-land ambient loops
(`stage1`…`stage6`), `celebrate` (short reward jingle). Keep gentle, low-tempo,
loopable; default volume 0.25.

## 7. Voice-over — `assets/audio/voice/<voice_pack>/<key>.ogg`
Per character voice pack. Record: the **common lines** from the character bible
(`greet, correct, retry`, …) and the **per-item words** keyed by content id
(`A.ogg`, `apple.ogg`, `cat.ogg`, `the.ogg`, `s_cat_runs.ogg`, …). Missing keys
fall back to TTS automatically. Full list:
[`docs/08_audio_requirements.md`](08_audio_requirements.md).

## 8. Animation sprites — `assets/images/effects/`
Optional pre-rendered particle art: `confetti_*.png`, `bubble.png`,
`balloon.png`, `star_spark.png`. The app generates these procedurally
(`ui/particles.py`) if absent.

## 9. Storybook illustrations — `assets/images/stories/<story_id>/`
One full-bleed illustration per page (`p1.png`, `p2.png`, …) plus the tappable
object cutout. Match `content/stories.json` page count.

## 10. Fonts — `assets/fonts/`
A rounded, highly-legible kids font (e.g. a Baloo/Quicksand-style face) for
display/body, plus a color-emoji font for placeholder pictographs. Register in
`ui/theme.py`.

---

## Naming & lookup rules (so assets "just work")
- **Voice:** `AudioManager.voice_path(key)` → `audio/voice/<pack>/<key>.{ogg,mp3,wav}`.
- **SFX:** `play_sfx(name)` → `audio/sfx/<name>.{ogg,wav,mp3}`.
- **Music:** `play_music(name)` → `audio/music/<name>.{ogg,mp3}`.
- **Content id == file stem** wherever possible, so authors drop in art that
  matches a JSON `id` with zero wiring.

## Delivery / optimization
- Export `@1x/@2x` or a single high-res that scales; target ≤ 2048px.
- Compress audio to OGG Vorbis ~96–128kbps; keep VO clips short.
- Bundle everything in the app (offline); see `buildozer.spec` include rules.
