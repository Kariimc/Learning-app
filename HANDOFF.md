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

## The art Kariim wanted is now in the project — 2026-08-22

52 pictures and 37 voice clips are now at `assets/source-art/reading-land/`.
They sat on his desktop, outside any project, with no backup anywhere.

THE IMPORTANT PART, in his own words on 2026-08-22:

> "The reading land art is the actual assets for the app that I wanted. I had to
> settle for what is in the app currently because the model could not place them
> correctly/successfully."

So `assets/images/` is a fallback he settled for, NOT the intended art
direction. The blocker was placement, not the assets. Read the README in the
new folder before touching the app's pictures.

Known problems with the wanted art, from a Gemini look at all 52 on 2026-08-22:
the words inside the pictures are garbled and need redoing, and there is heavy
repetition across the story scenes and buttons. The rendering itself is good.
The 37 voice clips have not been listened to by anyone.

NEXT STEP: find out why placement failed. Do not generate replacement art first.

## CORRECTION, same day: placement never failed — 2026-08-22

The entry written earlier today said the app's pictures were a fallback Kariim
settled for after placement failed. THAT WAS WRONG and is corrected here.

What was actually true: his July placement work succeeded. All 117 finished
assets are committed through Git LFS and present on the remote. His laptop clone
held 132-byte LFS pointer stubs instead of pictures, because `git lfs pull` had
never been run here. Every screen therefore looked empty, which read as failed
placement.

PROVED on 2026-08-22:
  before  all 56 files under assets/images were 132 bytes
  command git lfs pull --include="assets/images/**,assets/audio/**"
  after   50 real pictures (up to 10MB) and 47 real voice clips; the only small
          files left are empty .gitkeep markers, and no LFS pointer remains
  Gemini looked at all 50 and reported finished polished art, nothing broken.

ANY session that finds this app looking empty should run `git lfs pull` FIRST.

Two real defects in the art, worth fixing but not blockers:
- words printed inside the pictures are garbled
- character portraits have a checkerboard baked into the image instead of real
  transparency, so they will not sit cleanly on a background

STILL TO DO: local main is 3 commits behind origin/main and is missing the
July placement work itself (the --from local-folder mode, the magic-byte
validation, and the never-fallback guarantee). A merge was refused by the
environment's safety classifier, so it has not been done. The work is safe on
branch rescue/laptop-sweep meanwhile.

DEAD ROUTE: the Higgsfield CDN links inside scripts/fetch_assets.py were all
refused on 2026-08-22, including a file already held locally, while the CDN host
itself answered. Do not spend time on them. Git LFS is the route that works.
