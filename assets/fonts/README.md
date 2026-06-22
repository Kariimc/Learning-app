# Fonts

ReadingLand draws all **UI chrome** (back/home, speaker, gift, page arrows,
lock...) as crisp **vector icons** (`readingland/ui/icons.py`), so the interface
never depends on a system emoji font and never shows "tofu" boxes.

**Content emoji** (animals, objects, food used as picture cues) still render via
the platform emoji font when available. `readingland/ui/theme.py` auto-detects
one — including Windows `seguiemj.ttf` and macOS Apple Color Emoji.

To guarantee identical emoji rendering on every platform, drop a colour-emoji
font here named **`NotoColorEmoji.ttf`** (or any `*Emoji*.ttf`). It is picked up
automatically and bundled into the APK (see `buildozer.spec`). Get it from
https://github.com/googlefonts/noto-emoji (OFL licensed).
