
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
