# Assets

ReadingLand runs with **programmatic placeholders** (emoji + drawn shapes + big
type) so there are no missing-file crashes. Drop production art/audio here using
the conventions below and it's picked up automatically — **no code changes**.

## ⬇️ Fetch the generated character art
The five mascot portraits (transparent PNGs) and the app icon were produced with
an AI image model and are hosted on a CDN. Pull them in with one command:

```bash
python scripts/fetch_assets.py
```

This populates `images/characters/<id>/portrait.png` and `images/ui/app_icon.png`.
The `Mascot` widget then renders the real characters instead of the drawn
placeholders (`readingland/ui/assets.py` does the lookup). The app runs fine
either way.

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
