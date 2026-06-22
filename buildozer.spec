[app]
# ReadingLand - Android/iOS packaging via Buildozer.
# Build APK:   buildozer -v android debug
# See docs/10_deployment.md for full instructions.

title = ReadingLand
package.name = readingland
package.domain = org.readingland

source.dir = .
source.include_exts = py,json,png,jpg,jpeg,ogg,wav,mp3,ttf,otf,atlas
source.include_patterns = readingland/content/*.json, assets/*

version = 1.0.0

# Kivy + optional TTS. (On Android, system TTS is used instead of pyttsx3.)
requirements = python3,kivy==2.3.1

orientation = landscape
fullscreen = 1

# Tablet-first: support a wide range of densities.
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = 1

# No internet permission requested - the app is fully offline by design.
android.permissions =

# Splash / icon (replace placeholders with final art - see docs/06_asset_list.md)
# icon.filename = assets/images/ui/app_icon.png
# presplash.filename = assets/images/ui/presplash.png

[buildozer]
log_level = 2
warn_on_root = 1

# --- iOS (via kivy-ios / toolchain) ---------------------------------------
# ReadingLand also targets iPad. Build with kivy-ios:
#   toolchain build python3 kivy
#   toolchain create ReadingLand /path/to/Learning-app
# Then open the generated Xcode project. See docs/10_deployment.md.
