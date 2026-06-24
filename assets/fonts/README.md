# Fonts

ReadingLand draws all **UI chrome** (back/home, speaker, gift, page arrows,
lock...) as crisp **vector icons** (`readingland/ui/icons.py`), so the interface
never depends on a system emoji font and never shows "tofu" boxes.

**Content emoji** (animals, objects, food used as picture cues) render via
**`NotoEmoji-Regular.ttf`**, which is committed here and bundled into the APK
(see `buildozer.spec`). `readingland/ui/theme.py` registers it automatically.

Why monochrome (not colour) emoji: Android has no system emoji font Kivy can
reach, so without a bundled font every picture cue showed as a "tofu" box and
the matching games were unplayable. Monochrome Noto Emoji renders reliably
through Kivy's SDL_ttf/FreeType backend on **every** platform; colour-emoji
fonts (CBDT/SBIX bitmap tables) are not reliably supported by the version of
SDL_ttf that python-for-android bundles, so they would re-introduce tofu on the
tablet. The glyphs are tinted per-tile in the UI, giving a clean coloring-book
look. Source: https://github.com/googlefonts/noto-emoji (OFL licensed).

`theme.py` still auto-detects a platform/colour font (`*Emoji*.ttf`,
`seguiemj.ttf`, Apple Color Emoji) for desktop dev, but the committed font is
listed first so behaviour is identical everywhere.
