# Handoff — wire real Higgsfield assets into the app (no fallbacks)

## The goal
Make the running app show the **real generated plush art everywhere a child sees a
picture** — no emoji/tofu fallback should ever appear on screen. Then the owner
reviews before anything merges.

## HARD RULES (do not violate)
- **Do NOT merge to `main`.** Merging triggers the APK build (`.github/workflows/build-apk.yml`)
  which costs the owner credits. Push to the feature branch only; owner merges.
- **Do NOT generate anything in Higgsfield** (no credits). Use assets the owner provides.
- **Do NOT browse the owner's Higgsfield account.**
- The owner must **never see a fallback emoji** before merge. Every picture tile/cover
  must resolve to a real asset.

## Branch / state
- Branch: `claude/app-setup-google-drive-j6crmn` (based on latest `main`).
- Already merged to main this session: PR #5 (fetch_assets `--from` + LFS docs), PR #6
  (fetch_assets magic-byte hardening). Both are done — do not reopen.
- Assets live in **Git LFS**. To hydrate a clone: `git lfs install && git lfs pull`.
- This branch has a **WIP commit** wiring existing cutouts into tiles (see below). Incomplete.

## What the WIP commit does (5 files)
- `readingland/ui/assets.py` — adds `content_icon(item_id, emoji)` resolver + an
  emoji→slug map (mirrors `prototypes/readingland-flow.html`).
- `readingland/ui/widgets.py` — `GlyphTile` gained an `image` property (shows a plush
  cutout in place of the emoji; text label below).
- `readingland/screens/_matching.py` — `PICTURE_TILES` flag; when set, tiles use
  `content_icon(...)` with emoji fallback.
- `readingland/screens/stage1_visual.py` — `PICTURE_TILES = True`.
- `readingland/screens/stage6_stories.py` — story covers use each book's first page art
  (`card_image("<book_id>_p0")`). **This is fully covered (3/3) and safe.**

## THE BLOCKER (why it's not mergeable yet)
There are only **15 content cutouts** in `assets/images/cards/icon_*.png`
(apple, ball, bird, car, cat, circle, dog, egg, fish, goat, hat, heart, square, star, triangle),
but the content needs far more. Verified coverage gaps:

- **Stage 1 (20 picture tiles): 9 have NO cutout** → would show emoji:
  `color_blue, color_yellow, color_green, color_purple, animal_cow, animal_duck,
  animal_frog, object_cup, object_sun`
- **Stage 6 covers: 3/3 covered — safe.**
- **Stages 2–5** still render small emoji hints (26 letters, 20 words, etc.), mostly
  without cutouts — these are NOT wired yet and are additional fallback surfaces.

## The owner has the missing assets ON THEIR COMPUTER
The owner said the needed cutouts are on their local machine. Next agent (running
locally / with access to that folder) should:

1. Get the missing `icon_*.png` cutouts into `assets/images/cards/` (transparent PNGs,
   named `icon_<slug>.png`). The app resolves them by content `id` (`icon_<id>.png`)
   OR by the item's emoji via the map in `assets.py`. Cover at minimum the 9 Stage-1
   gaps above; ideally every content item across stages the owner wants pictured.
   - Colors are abstract — decide with the owner whether colors get a cutout or leave
     that category as-is.
2. `git add assets && git commit` (LFS stores them automatically).
3. Decide with the owner whether to also wire Stages 2/4 tile pictures (set
   `PICTURE_TILES = True` on those screens) or keep letters/words text-first.
4. **Verify ZERO fallback before proposing merge** — run the coverage check:
   ```
   PYTHONPATH=. python3 - <<'PY'
   import json, glob, os
   from readingland.ui import assets as A
   s1 = json.load(open("readingland/content/stage1_visual.json"))["items"]
   miss = [it["id"] for it in s1 if not A.content_icon(it["id"], it.get("emoji"))]
   print("Stage1 uncovered:", miss or "NONE")
   PY
   ```
   `miss` must be empty for every pictured stage.
5. Only then push the branch and let the **owner** merge.

## How to see the app live (headless, no display)
The app is Kivy. To render screens without a display:
```
apt-get install -y xvfb x11-apps imagemagick libmtdev1 >/dev/null
PYTHONPATH=. LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a -s "-screen 0 1024x720x24" python3 main.py
```
Capture a frame with `DISPLAY=:<n> import -window root shot.png`. (Kivy's
`Window.screenshot()` returns black under software GL — use the X grab instead.)

## Known cosmetic note (owner said leave the assets as-is, do NOT re-cut)
Three mascot portraits (`benny_bear`, `ollie_owl`, `milo_monkey`), the six `land_*`
signposts, and `btn_mint`/`btn_coral` are flat RGB with a transparency checkerboard
baked into the pixels, so they render with a grey checker in-app. The owner has said
the assets are fine — do not modify or regenerate them unless the owner asks.

## Tests
`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy KIVY_AUDIO=mock python3 -m pytest -q` → 28 pass.
