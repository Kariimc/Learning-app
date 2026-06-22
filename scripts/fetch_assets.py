#!/usr/bin/env python3
"""Fetch ReadingLand's generated production assets into ``assets/``.

Character portraits, land backgrounds, storybook illustrations and the warm
"fairy godmother" (Mabel) voice pack were generated with AI models and are
hosted on a CDN. They're downloaded on demand so the binaries don't bloat git.
Run once after cloning:

    python scripts/fetch_assets.py

The app already *uses* every file when present (see ``readingland/ui/assets.py``,
the ``Mascot``/``BaseScreen`` widgets and ``readingland/core/audio.py``); until
fetched it falls back to programmatic placeholders + warm TTS, so it runs either
way. Re-running only fetches what's missing unless you pass ``--force``.
"""
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CDN = "https://d8j0ntlcm91z4.cloudfront.net/user_3F1n9RqGZCJVrB84dvcvAMuNMRC"

# target path (relative to repo root) -> source URL
ASSETS = {
    # --- Character portraits (transparent) + app icon --------------------- #
    "assets/images/characters/reading_rabbit/portrait.png":
        f"{CDN}/hf_20260622_050001_f2680efb-9adf-4d76-b580-b6c5dbe597f6.png",
    "assets/images/characters/benny_bear/portrait.png":
        f"{CDN}/hf_20260622_050005_40c735b0-cf7f-4472-ac17-77e09484a394.png",
    "assets/images/characters/penny_penguin/portrait.png":
        f"{CDN}/hf_20260622_050009_e75c48ae-df3b-4235-bf75-c0dc4eb657cb.png",
    "assets/images/characters/ollie_owl/portrait.png":
        f"{CDN}/hf_20260622_050013_df27ad85-491e-41bf-8776-9aaf80ede552.png",
    "assets/images/characters/milo_monkey/portrait.png":
        f"{CDN}/hf_20260622_050019_1860cb5d-bccc-4dae-b11d-87a28f772ac9.png",
    "assets/images/ui/app_icon.png":
        f"{CDN}/hf_20260622_045558_a0f5efd4-b314-45c2-9c9d-f89c3fdd58fd.png",

    # --- Land backgrounds (one per stage + world map) --------------------- #
    "assets/images/backgrounds/bg_visual.png":
        f"{CDN}/hf_20260622_060745_64a0d9aa-a9e2-423b-bf6e-daddaf3ddf46.png",
    "assets/images/backgrounds/bg_alphabet.png":
        f"{CDN}/hf_20260622_060750_a2379894-b558-447b-9340-6875389ee175.png",
    "assets/images/backgrounds/bg_phonics.png":
        f"{CDN}/hf_20260622_060756_f0d69cef-c8d1-4831-b085-cfce9b769f84.png",
    "assets/images/backgrounds/bg_words.png":
        f"{CDN}/hf_20260622_060801_8f089e3d-0cad-49b9-aa32-05792e18aa28.png",
    "assets/images/backgrounds/bg_sentences.png":
        f"{CDN}/hf_20260622_060806_a34290b3-e871-4e0a-8e63-feabe36eba4f.png",
    "assets/images/backgrounds/bg_stories.png":
        f"{CDN}/hf_20260622_060811_810a207a-f2a3-4504-8d64-234cc76053d0.png",
    "assets/images/backgrounds/bg_map.png":
        f"{CDN}/hf_20260622_060817_2e2e5e79-a93a-4400-a400-f9ba00052ef3.png",

    # --- Storybook page illustrations (cards/<book>_p<page>) -------------- #
    "assets/images/cards/story_cat_nap_p0.png":
        f"{CDN}/hf_20260622_062325_2cc7b7c1-1380-4e9b-b1f1-2e04ec259097.png",
    "assets/images/cards/story_cat_nap_p1.png":
        f"{CDN}/hf_20260622_062329_3075dfcb-d318-4ead-ae50-42a402cec311.png",
    "assets/images/cards/story_cat_nap_p2.png":
        f"{CDN}/hf_20260622_062334_a7eac6c2-ae96-4018-a65c-6862c628cad0.png",
    "assets/images/cards/story_cat_nap_p3.png":
        f"{CDN}/hf_20260622_062339_428eec05-c26e-42cf-9a27-88ebb7d1aed4.png",
    "assets/images/cards/story_big_dog_p0.png":
        f"{CDN}/hf_20260622_062346_4a5ddbda-4825-4f20-950c-10c61e2815e0.png",
    "assets/images/cards/story_big_dog_p1.png":
        f"{CDN}/hf_20260622_062352_32c4f0ee-cb83-42ca-be6f-a79a45fb4329.png",
    "assets/images/cards/story_big_dog_p2.png":
        f"{CDN}/hf_20260622_062358_3eeb1eb6-9802-4da5-bb42-7e124a4ff109.png",
    "assets/images/cards/story_big_dog_p3.png":
        f"{CDN}/hf_20260622_062403_e92b31c2-5446-467d-9666-f0113c1e0bf0.png",
    "assets/images/cards/story_sun_and_bird_p0.png":
        f"{CDN}/hf_20260622_062408_eeeba652-eb9a-4a1a-93c4-0e45c4f0da94.png",
    "assets/images/cards/story_sun_and_bird_p1.png":
        f"{CDN}/hf_20260622_062416_fd572c9e-b35a-480d-8f42-a56316e369d4.png",
    "assets/images/cards/story_sun_and_bird_p2.png":
        f"{CDN}/hf_20260622_062420_e3c90776-c25e-49f8-8fc0-be37097c4927.png",
    "assets/images/cards/story_sun_and_bird_p3.png":
        f"{CDN}/hf_20260622_062425_ef0f300c-7749-47ca-ad58-07a113685d70.png",

    # --- Mabel voice pack (audio/voice/mabel/<key>.mp3) ------------------- #
    "assets/audio/voice/mabel/greet_home.mp3":
        f"{CDN}/hf_20260622_062446_46c6a65c-ad4b-439a-9570-533f43fe9137.mp3",
    "assets/audio/voice/mabel/greet_story.mp3":
        f"{CDN}/hf_20260622_062450_5da94f28-c9ea-4f9f-9ae2-1b16da4f9a4f.mp3",
    "assets/audio/voice/mabel/locked_stage.mp3":
        f"{CDN}/hf_20260622_062454_512ae0d6-5d68-4778-ab07-859f0ae657f4.mp3",
    "assets/audio/voice/mabel/locked_tracing.mp3":
        f"{CDN}/hf_20260622_062458_eb6eb5a9-b06f-426d-a463-e5ae99a16f93.mp3",
    "assets/audio/voice/mabel/finish_book.mp3":
        f"{CDN}/hf_20260622_062501_39306b1a-176c-4da1-8df1-aeb8754b8c14.mp3",
    "assets/audio/voice/mabel/retry_listen.mp3":
        f"{CDN}/hf_20260622_062508_83444f92-0fd9-4abf-9bc6-8b0ad968f12f.mp3",
    "assets/audio/voice/mabel/retry_sound.mp3":
        f"{CDN}/hf_20260622_062512_1a434299-b31c-4731-9dc7-a513ccfd4486.mp3",
    "assets/audio/voice/mabel/retry_read.mp3":
        f"{CDN}/hf_20260622_062516_a2567392-2fe6-4522-9e41-e27ed555bee2.mp3",
    "assets/audio/voice/mabel/ln_great_job.mp3":
        f"{CDN}/hf_20260622_062520_e63421d1-b00c-4114-aef0-50182c8453e6.mp3",
    "assets/audio/voice/mabel/ln_fantastic_reading.mp3":
        f"{CDN}/hf_20260622_062524_c0ccd07e-8355-4f69-bca6-0b8a292f6180.mp3",
    "assets/audio/voice/mabel/ln_you_did_it.mp3":
        f"{CDN}/hf_20260622_062527_79d13456-c7eb-4958-8a7e-ed66aec2dea5.mp3",
    "assets/audio/voice/mabel/ln_wonderful.mp3":
        f"{CDN}/hf_20260622_062531_db55d087-66d9-495a-b035-b4ed540a8802.mp3",
    "assets/audio/voice/mabel/ln_super_star.mp3":
        f"{CDN}/hf_20260622_062535_13effa6d-392c-4ef6-aba3-8b1c50199c7d.mp3",
    "assets/audio/voice/mabel/ln_you_found_it.mp3":
        f"{CDN}/hf_20260622_062539_8e60af26-0a77-4c6c-8aac-02229e5fecad.mp3",
    "assets/audio/voice/mabel/ln_brilliant.mp3":
        f"{CDN}/hf_20260622_062543_d208457a-d52d-42bf-8bde-468b9109152f.mp3",
    "assets/audio/voice/mabel/ln_good_try_let_s_try_again.mp3":
        f"{CDN}/hf_20260622_062548_0a926df2-2f01-48b5-b62c-3804404ea6ee.mp3",
    "assets/audio/voice/mabel/ln_almost_try_once_more.mp3":
        f"{CDN}/hf_20260622_062552_5f5cdc13-b60f-4c54-a016-8c85ae052852.mp3",
    "assets/audio/voice/mabel/ln_nice_try_listen_again.mp3":
        f"{CDN}/hf_20260622_062556_57d627c3-4905-4119-af3c-fe2c680396e5.mp3",
    "assets/audio/voice/mabel/ln_let_s_find_it_together.mp3":
        f"{CDN}/hf_20260622_062600_e3c1da6c-d665-419d-ae10-b88a0bd861b1.mp3",
}


def main() -> int:
    force = "--force" in sys.argv
    failures = skipped = fetched = 0
    for rel, url in ASSETS.items():
        dest = os.path.join(ROOT, rel)
        if os.path.exists(dest) and not force:
            skipped += 1
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "readingland-fetch"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if len(data) < 1024:
                raise ValueError(f"suspiciously small ({len(data)} bytes)")
            with open(dest, "wb") as fh:
                fh.write(data)
            fetched += 1
            print(f"OK   {rel}  ({len(data) // 1024} KB)")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAIL {rel}: {exc}", file=sys.stderr)
    print(f"\nFetched {fetched}, skipped {skipped} (already present), failed {failures}.")
    if failures:
        print("The app still runs with placeholders + TTS for anything missing.",
              file=sys.stderr)
        return 1
    print("All assets ready. Run `python main.py` to see and hear the full app.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
