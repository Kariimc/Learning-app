# 10 · Mobile Deployment

Target platforms: **Android tablets, iPads, touchscreen PCs**. The app is fully
offline — no backend to deploy, no network permission requested.

## Desktop (dev / touchscreen PC)
```bash
pip install -r requirements.txt
python main.py
```
Windows/macOS/Linux touchscreen PCs run this directly. For kiosk-style use,
launch fullscreen (already set via `buildozer.spec` for mobile; on desktop set
`Window.fullscreen = True` or press F11).

## Android (tablets) — Buildozer
Buildozer config is in [`buildozer.spec`](../buildozer.spec).

**Prereqs (Linux/WSL recommended):**
```bash
pip install buildozer cython
sudo apt install -y git zip unzip openjdk-17-jdk autoconf libtool \
    pkg-config zlib1g-dev libncurses5-dev libffi-dev libssl-dev
```

**Build a debug APK:**
```bash
buildozer -v android debug
# output: bin/readingland-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

**Install on a connected tablet:**
```bash
buildozer android deploy run        # or: adb install -r bin/*.apk
```

**Release (signed) build:**
```bash
buildozer android release
# then sign with apksigner / zipalign using your keystore, or produce an .aab
```
Notes:
- `orientation = landscape`, `fullscreen = 1`, `minapi = 24` (Android 7+),
  `archs = arm64-v8a, armeabi-v7a` cover the vast majority of tablets.
- **No permissions** requested (`android.permissions =`) — reinforces the offline,
  child-safe, privacy-first promise.
- On Android, the system TTS engine backs the narration fallback (no `pyttsx3`).

## iPad / iOS — kivy-ios
```bash
pip install kivy-ios
toolchain build python3 kivy
toolchain create ReadingLand /path/to/Learning-app
open ReadingLand-ios/ReadingLand.xcodeproj
```
In Xcode: set the bundle id, signing team, **landscape** orientation, iPad
device family, then build to a device/simulator. Submit via App Store Connect
(category: Education / Kids). Use the iOS native `AVSpeechSynthesizer` path for
TTS fallback (recorded packs preferred).

## Asset bundling
`buildozer.spec` includes `json, png, jpg, ogg, wav, mp3, ttf, otf, atlas` and
the `readingland/content/*.json` + `assets/*` patterns, so all curriculum and art
ship inside the app for offline use.

## Pre-release checklist
- [ ] `pytest` green (engine).
- [ ] `xvfb-run python scripts/smoke_run.py` green (every screen builds).
- [ ] Real device pass: tap targets comfortable, audio plays, no jank at 60fps.
- [ ] Replace placeholder art/audio per [`docs/06`](06_asset_list.md) (optional
      for internal builds; required for store).
- [ ] App icon + splash set in `buildozer.spec`.
- [ ] Kids-category compliance (no ads, no IAP, no external links, no data
      collection) — already true by design.

## Store positioning
- **Category:** Education / Kids (ages 2–8).
- **Privacy:** "No data collected" — everything is on-device.
- **Monetization:** none. Free, no ads, no in-app purchases (see
  [`README`](../README.md) deliverable #12).
