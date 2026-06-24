# Assets

ReadingLand runs with **programmatic placeholders** (emoji + drawn shapes + big
type) so there are no missing-file crashes. Drop production art/audio here using
the conventions below and it's picked up automatically — **no code changes**.

## 🧶 Generate the felt art + voice (offline, no API)
Mascot portraits, the app icon, button/panel textures, land backgrounds and the
warm narrator voice pack are **generated on-device** — felt/plush art with Pillow
and narration with an offline neural TTS — and committed to the repo. A fresh
clone already has them. To re-generate (no API, no CDN, no network):

```bash
pip install pillow numpy piper-tts
python scripts/generate_art.py        # --only buttons|characters|backgrounds
python scripts/generate_voice.py      # --engine piper|pico|espeak  --force
# (scripts/fetch_assets.py runs both, for backward-compatible muscle memory)
```

This populates:
- `images/ui/felt_button.png`, `felt_panel.png` — tintable plush-felt textures
  (buttons/cards multiply their colour by these; see `ui/assets.felt_texture`)
- `images/characters/<id>/portrait.png` — felt mascots (`Mascot` widget)
- `images/ui/app_icon.png` — felt app icon
- `images/backgrounds/bg_<land>.jpg` — per-land felt backgrounds (`BaseScreen`)
- `audio/voice/mabel/<key>.ogg` — narrator lines (`core/audio.py`)

Every file is optional: `readingland/ui/assets.py` / `core/audio.py` look them up
and fall back to programmatic placeholders + captions, so the app runs either way.
Storybook page illustrations (`images/cards/story_<book>_p<n>.png`) aren't
generated — Stage 6 falls back to big emoji scenes.

Full bill of materials & specs: [`../docs/06_asset_list.md`](../docs/06_asset_list.md).
Audio specifics: [`../docs/08_audio_requirements.md`](../docs/08_audio_requirements.md).

## Folder layout
```
assets/
├── images/
│   ├── characters/<id>/      idle, happy, encourage, point, talk, celebrate
│   ├── backgrounds/          per-land parallax + clouds
│   ├── ui/                   app_icon, presplash, star, lock, speaker, chest…
│   ├── cards/                content pictures: <item_id>.png
│   ├── stories/<story_id>/   p1.png, p2.png … + tappable cutouts
│   └── effects/              confetti, bubble, balloon, star_spark (optional)
├── audio/
│   ├── voice/<voice_pack>/   <key>.ogg  (e.g. A.ogg, cat.ogg, greet.ogg)
│   ├── sfx/                  tap, pop, correct, wrong, chest, page, locked…
│   └── music/                theme, stage1…stage6, celebrate
└── fonts/                    rounded kids display font + color-emoji font
```

## Lookup rules (how the app finds files)
| Call | Path searched |
|------|---------------|
| `AudioManager.narrate(text, key="A")` | `audio/voice/<pack>/A.{ogg,mp3,wav}` |
| `AudioManager.play_sfx("correct")` | `audio/sfx/correct.{ogg,wav,mp3}` |
| `AudioManager.play_music("theme")` | `audio/music/theme.{ogg,mp3}` |
| content picture | `images/cards/<item_id>.png` |

**Convention:** a content item's `id` == its asset file stem. Match the `id` in
`readingland/content/*.json` and the asset wires itself up.

## Art style (keep cohesive)
Rounded, chunky cartoon; soft shadows; big friendly eyes; the `config.PALETTE`
colors; no thin lines or dense detail. Export ≤ 2048px, PNG w/ transparency for
sprites; OGG Vorbis ~96–128 kbps for audio. Everything is bundled for **offline**
use (`buildozer.spec`).

> `.gitkeep` files keep the empty subfolders in version control until real assets
> land.
