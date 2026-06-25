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
    # --- Character portraits (3-D plush style, transparent bg) ------------ #
    "assets/images/characters/reading_rabbit/portrait.png":
        f"{CDN}/hf_20260624_124607_68b15c80-dd9b-4bcd-9acd-cf815a92dbee.png",
    "assets/images/characters/benny_bear/portrait.png":
        f"{CDN}/hf_20260624_124639_07dbdb38-ff3f-4bd3-8f4f-41bbe75fff00.png",
    "assets/images/characters/penny_penguin/portrait.png":
        f"{CDN}/hf_20260624_124641_f62cc169-c0fb-4f64-8df8-d57013907565.jpeg",
    "assets/images/characters/ollie_owl/portrait.png":
        f"{CDN}/hf_20260624_124642_94de2730-cbd4-4be4-a000-ef0ef194436a.png",
    "assets/images/characters/milo_monkey/portrait.png":
        f"{CDN}/hf_20260624_124644_517889d9-5272-4638-aab0-e6b316153b9c.png",
    "assets/images/ui/app_icon.png":
        f"{CDN}/hf_20260624_124646_60dc1a70-1e12-4e16-a003-e058cdb45ed4.png",

    # --- Land backgrounds (one per stage + world map) --------------------- #
    "assets/images/backgrounds/bg_visual.png":
        f"{CDN}/hf_20260624_124648_00574061-bed6-49d3-9ef3-7373a128b5b9.png",
    "assets/images/backgrounds/bg_alphabet.png":
        f"{CDN}/hf_20260624_124650_73a4235b-810c-46cc-ac49-7d1d01c9bb52.png",
    "assets/images/backgrounds/bg_phonics.png":
        f"{CDN}/hf_20260624_124651_570a66e4-ae7e-411c-9c82-9f0fcba10b79.png",
    "assets/images/backgrounds/bg_words.png":
        f"{CDN}/hf_20260624_124656_09abb280-5031-402e-9138-c8e89126eda2.png",
    "assets/images/backgrounds/bg_sentences.png":
        f"{CDN}/hf_20260624_124657_0af94c30-05fe-45ab-a74a-9e19a3ba6d81.png",
    "assets/images/backgrounds/bg_stories.png":
        f"{CDN}/hf_20260624_124659_a4cc5385-9874-4ff1-a5fa-683c17f47620.png",
    "assets/images/backgrounds/bg_map.png":
        f"{CDN}/hf_20260624_124703_331c9d87-aed5-4be3-b401-c796998d9ea5.png",

    # --- Storybook page illustrations (cards/<book>_p<page>) -------------- #
    "assets/images/cards/story_cat_nap_p0.png":
        f"{CDN}/hf_20260624_124704_906ceca1-9f06-4510-a588-2ec7b322c14c.jpeg",
    "assets/images/cards/story_cat_nap_p1.png":
        f"{CDN}/hf_20260624_124705_87f80398-05a1-4705-8a18-7e6f917ce176.png",
    "assets/images/cards/story_cat_nap_p2.png":
        f"{CDN}/hf_20260624_124706_a8eaf407-2741-4035-8105-8f9edd4554e0.png",
    "assets/images/cards/story_cat_nap_p3.png":
        f"{CDN}/hf_20260624_124707_5c3b95b1-5122-4b0a-ba71-db00db9ad068.png",
    "assets/images/cards/story_big_dog_p0.png":
        f"{CDN}/hf_20260624_124711_94539d13-230a-427f-9e1e-a43d2ab640e1.png",
    "assets/images/cards/story_big_dog_p1.png":
        f"{CDN}/hf_20260624_124713_0a6fcdc0-a655-4d66-ae9d-c898b974c008.png",
    "assets/images/cards/story_big_dog_p2.png":
        f"{CDN}/hf_20260624_124714_377b5627-d4ea-4620-9578-4b9d7647482c.png",
    "assets/images/cards/story_big_dog_p3.png":
        f"{CDN}/hf_20260624_124715_e509bfb3-3903-4232-ab8e-f4f98c2ea370.png",
    "assets/images/cards/story_sun_and_bird_p0.png":
        f"{CDN}/hf_20260624_124716_308d6c84-9644-4986-8ebc-1239d795767f.png",
    "assets/images/cards/story_sun_and_bird_p1.png":
        f"{CDN}/hf_20260624_124718_3345b9fe-9ed9-4b6b-89d4-99a641f6af25.png",
    "assets/images/cards/story_sun_and_bird_p2.png":
        f"{CDN}/hf_20260624_124719_3f01c6ea-715d-46dc-887a-07780fcc996a.png",
    "assets/images/cards/story_sun_and_bird_p3.png":
        f"{CDN}/hf_20260624_124720_2901d86a-b640-4881-8cdb-2f89e6d79620.png",

    # --- 3-D plush button textures (ui/btn_<colour>.png) ------------------ #
    "assets/images/ui/btn_mint.png":
        f"{CDN}/hf_20260624_124726_78ddae20-065c-4f9d-8013-3adca54766cd.png",
    "assets/images/ui/btn_coral.png":
        f"{CDN}/hf_20260624_124727_cb13215e-83da-4430-91a6-68e5c7ed2a07.png",
    "assets/images/ui/btn_gold.png":
        f"{CDN}/hf_20260624_124728_7e236b3f-f150-448e-bb39-1f5cd2ddef6d.png",

    # --- Fonts ------------------------------------------------------------ #
    # Google now ships Fredoka only as a variable font (the old static/
    # Fredoka-Bold.ttf 404s). Kivy/SDL2_ttf can't apply variation axes, so this
    # renders at the default weight, but it's still the rounded Fredoka shape and
    # is a TTF (fontsource only ships woff2, which SDL2_ttf can't load). Saved
    # under the name theme.register_main_font() looks for first.
    "assets/fonts/Fredoka-Bold.ttf":
        "https://github.com/google/fonts/raw/main/ofl/fredoka/Fredoka%5Bwdth%2Cwght%5D.ttf",

    # --- Mabel voice pack (audio/voice/mabel/<key>.mp3) ------------------- #
    "assets/audio/voice/mabel/greet_home.mp3":
        f"{CDN}/hf_20260622_064607_511bb017-548d-4913-84bd-526708372f04.mp3",
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
        f"{CDN}/hf_20260622_064608_d36ca47a-fb02-4dd1-a0fb-45f9051b4b39.mp3",
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

    # --- Letter sounds (audio/voice/mabel/letter_<x>.mp3) ----------------- #
    "assets/audio/voice/mabel/letter_a.mp3":
        f"{CDN}/hf_20260622_064609_74679fa6-12b1-4f86-86bd-72b384c7d9a1.mp3",
    "assets/audio/voice/mabel/letter_b.mp3":
        f"{CDN}/hf_20260622_064610_3b3310b0-5e44-45f1-b599-476150aba5f0.mp3",
    "assets/audio/voice/mabel/letter_c.mp3":
        f"{CDN}/hf_20260622_064611_e011c5d3-d0ed-46fb-9b38-9e745bda88db.mp3",
    "assets/audio/voice/mabel/letter_d.mp3":
        f"{CDN}/hf_20260622_064617_d0aaa644-36a4-47e2-8fed-9243e76f9522.mp3",
    "assets/audio/voice/mabel/letter_e.mp3":
        f"{CDN}/hf_20260622_064618_c349d157-353a-4a77-8ab9-936eca17fbfd.mp3",
    "assets/audio/voice/mabel/letter_f.mp3":
        f"{CDN}/hf_20260622_064619_401f7189-6bc3-41cd-b15a-d3ed03f65591.mp3",
    "assets/audio/voice/mabel/letter_g.mp3":
        f"{CDN}/hf_20260622_064620_d3f27b79-4466-4f2f-80ce-9f1eb6599052.mp3",
    "assets/audio/voice/mabel/letter_h.mp3":
        f"{CDN}/hf_20260622_064621_f33df3b4-0003-4a19-8c11-081f90858b18.mp3",
    "assets/audio/voice/mabel/letter_i.mp3":
        f"{CDN}/hf_20260622_064627_049d7b1e-af2b-4cb8-a542-ee2e591e4648.mp3",
    "assets/audio/voice/mabel/letter_j.mp3":
        f"{CDN}/hf_20260622_064628_0af0076c-ce72-4be4-9ce7-f3cd6851d8c8.mp3",
    "assets/audio/voice/mabel/letter_k.mp3":
        f"{CDN}/hf_20260622_064629_1db577b7-b577-4ccc-b33e-e641dd8312c9.mp3",
    "assets/audio/voice/mabel/letter_l.mp3":
        f"{CDN}/hf_20260622_064631_3cee25fd-afe2-4a69-b861-855510da82b8.mp3",
    "assets/audio/voice/mabel/letter_m.mp3":
        f"{CDN}/hf_20260622_064632_0c2ec460-fe46-4cec-9af9-e13369303b5a.mp3",
    "assets/audio/voice/mabel/letter_n.mp3":
        f"{CDN}/hf_20260622_064639_ce17dca0-2fcb-470d-9604-033885427c93.mp3",
    "assets/audio/voice/mabel/letter_o.mp3":
        f"{CDN}/hf_20260622_064639_bb43173a-5094-4ad9-8700-5b1c8d57aa9b.mp3",
    "assets/audio/voice/mabel/letter_p.mp3":
        f"{CDN}/hf_20260622_064641_4534be2d-faaf-41ec-9077-6da69f61740d.mp3",
    "assets/audio/voice/mabel/letter_q.mp3":
        f"{CDN}/hf_20260622_064641_39a1ced0-03f2-4b49-98f5-b74be42eb45f.mp3",
    "assets/audio/voice/mabel/letter_r.mp3":
        f"{CDN}/hf_20260622_064644_cdf125eb-fbfa-4caf-9ab3-f0f700790188.mp3",
    "assets/audio/voice/mabel/letter_s.mp3":
        f"{CDN}/hf_20260622_064648_a275270d-b913-4211-b426-8b54d3b6736b.mp3",
    "assets/audio/voice/mabel/letter_t.mp3":
        f"{CDN}/hf_20260622_064649_e15e0e59-782c-488c-9906-a864e48487f2.mp3",
    "assets/audio/voice/mabel/letter_u.mp3":
        f"{CDN}/hf_20260622_064649_b459bf07-409a-4510-93ef-a47af5d1bb6b.mp3",
    "assets/audio/voice/mabel/letter_v.mp3":
        f"{CDN}/hf_20260622_064650_b75f211e-9cc8-4b1e-8a1a-3284518c5508.mp3",
    "assets/audio/voice/mabel/letter_w.mp3":
        f"{CDN}/hf_20260622_064651_0e9deee2-eea9-43d2-b577-ffbe7acbcc99.mp3",
    "assets/audio/voice/mabel/letter_x.mp3":
        f"{CDN}/hf_20260622_064655_8b659e73-5676-4744-ad9a-541e60319e96.mp3",
    "assets/audio/voice/mabel/letter_y.mp3":
        f"{CDN}/hf_20260622_064656_ec1b8747-88df-4f14-b44d-60d1ce728805.mp3",
    "assets/audio/voice/mabel/letter_z.mp3":
        f"{CDN}/hf_20260622_064657_e9bbe8b1-f648-45c9-9936-b4679b8aee26.mp3",

    # --- Stage 4 sight words (audio/voice/mabel/<word>.mp3) --------------- #
    "assets/audio/voice/mabel/cat.mp3":
        f"{CDN}/hf_20260622_064657_fe9c0c06-bb20-4065-8d77-28be45aa1e1b.mp3",
    "assets/audio/voice/mabel/dog.mp3":
        f"{CDN}/hf_20260622_064658_2b25d727-c357-424c-b941-fa7c54c5dedd.mp3",
    "assets/audio/voice/mabel/sun.mp3":
        f"{CDN}/hf_20260622_064702_462af9ac-7ab0-437c-84aa-7e1c60dcde65.mp3",
    "assets/audio/voice/mabel/ball.mp3":
        f"{CDN}/hf_20260622_064702_afd7bafa-9764-436c-9a04-5aecf152b1d9.mp3",
    "assets/audio/voice/mabel/fish.mp3":
        f"{CDN}/hf_20260622_064703_baca7423-a458-4bf5-842d-40ee0eeaaa6c.mp3",
    "assets/audio/voice/mabel/tree.mp3":
        f"{CDN}/hf_20260622_064704_553fb0b0-074f-4274-b97a-3b5d754d73d2.mp3",
    "assets/audio/voice/mabel/star.mp3":
        f"{CDN}/hf_20260622_064705_3c5596e0-8474-4a56-b2c4-0ea3791421cd.mp3",
    "assets/audio/voice/mabel/bird.mp3":
        f"{CDN}/hf_20260622_064708_31756380-cf62-4179-9dd1-55e26afacd7b.mp3",
    "assets/audio/voice/mabel/run.mp3":
        f"{CDN}/hf_20260622_064709_3fec843f-6d85-4663-861a-0c06f993dab4.mp3",
    "assets/audio/voice/mabel/jump.mp3":
        f"{CDN}/hf_20260622_064710_9ba5fe6c-243b-4988-923c-f054fdc80b2b.mp3",
    "assets/audio/voice/mabel/fly.mp3":
        f"{CDN}/hf_20260622_064711_406b09f4-86a1-4d96-80bb-494d404b3f68.mp3",
    "assets/audio/voice/mabel/look.mp3":
        f"{CDN}/hf_20260622_064712_edd2d6eb-6e6a-4a3d-a8ef-bd434f0ecac2.mp3",
    "assets/audio/voice/mabel/play.mp3":
        f"{CDN}/hf_20260622_064716_7a9d0a63-dd33-4327-8ee2-f371c598a50d.mp3",
    "assets/audio/voice/mabel/the.mp3":
        f"{CDN}/hf_20260622_064717_7bdf2610-b9fe-42e6-a67b-09d9d3fa80af.mp3",
    "assets/audio/voice/mabel/is.mp3":
        f"{CDN}/hf_20260622_064717_62d81a31-9fcb-424a-b702-2a564373a537.mp3",
    "assets/audio/voice/mabel/can.mp3":
        f"{CDN}/hf_20260622_064718_fd10e685-4169-4e28-8e24-39ad836319d1.mp3",
    "assets/audio/voice/mabel/see.mp3":
        f"{CDN}/hf_20260622_064719_6527c4ba-8e5e-430d-b545-4d8f638278dd.mp3",
    "assets/audio/voice/mabel/go.mp3":
        f"{CDN}/hf_20260622_064723_e3b74be4-8117-4735-9bc1-b0f71072f103.mp3",
    "assets/audio/voice/mabel/happy.mp3":
        f"{CDN}/hf_20260622_064724_db479e9b-4e76-4521-963f-c04278181097.mp3",
    "assets/audio/voice/mabel/a.mp3":
        f"{CDN}/hf_20260622_064809_01e308ae-38dc-4a61-b1e0-692ceb0a4871.mp3",
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
