# The raw generated art, and the placement story (SOLVED 2026-08-22)

## Read this first: the app is NOT short of art

For a long time this app appeared to be showing nothing. Kariim's own account on
2026-08-22:

> "The reading land art is the actual assets for the app that I wanted. I had to
> settle for what is in the app currently because the model could not place them
> correctly/ successfully."

**That reading was wrong, and the fix took one command.** The placement work he
did in July SUCCEEDED. All 117 finished assets were committed to this repo
through Git LFS and are on the remote. What his laptop held were 132-byte
pointer stubs, not pictures, because `git lfs pull` had never been run in this
clone. So every screen looked empty and it read like placement had failed.

The fix, run and proved on 2026-08-22:

    git lfs pull

Before: all 56 images in `assets/images/` were 132 bytes. After: 50 real
pictures up to 10MB each, plus 47 real voice clips. Gemini looked at every one
and reported finished, polished, high-resolution art with nothing broken or
missing.

**If the app ever looks empty again, run that command before assuming anything
is lost.**

## What is in THIS folder

The 52 raw generated pictures and 37 raw voice clips, exactly as Higgsfield
produced them on 2026-06-24, named by job id. They sat on Kariim's desktop
outside any project with no backup until 2026-08-22.

They are the RAW SOURCE. `assets/images/` holds the finished, placed versions.
This folder is the archive you come back to when a picture needs recutting.

`scripts/fetch_assets.py` maps each finished path to its source job id. It wants
115 generated files; 52 of them are here and the other 63 (mostly the June 22
voice pack) were never in this pile. That does not matter while Git LFS holds
the finished set.

## Known flaws in the raw art

From a Gemini look at all 52 on 2026-08-22, score 6 out of 10:

- **words inside the pictures are garbled** and need redoing before any picture
  carrying text ships
- the character portraits have a **checkerboard pattern baked into the image**
  rather than real transparency
- heavy repetition across "The Cat Nap", "The Sun and The Bird" and the buttons
- rendering itself is good: plush and clay textures, soft light, bright pastels

## The one download route that no longer works

`fetch_assets.py` can also pull from the Higgsfield CDN. Every asset link there
was refused from Kariim's machine on 2026-08-22, including one whose file he
already had, while the CDN host itself still answered. Treat those links as
gone. Git LFS is the working route.
