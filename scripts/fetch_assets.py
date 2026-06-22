#!/usr/bin/env python3
"""Fetch ReadingLand's generated production art into ``assets/``.

The five character portraits (transparent PNGs) and the app icon were generated
with an AI image model. They are hosted on a CDN and downloaded on demand so the
binaries don't bloat the git history. Run once after cloning:

    python scripts/fetch_assets.py

The app already *uses* these files when present (see ``readingland/ui/assets.py``
and the ``Mascot`` widget); until fetched it falls back to the built-in
programmatic placeholders, so the app runs either way.
"""
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CDN = "https://d8j0ntlcm91z4.cloudfront.net/user_3F1n9RqGZCJVrB84dvcvAMuNMRC"

# target path (relative to repo root) -> source URL
ASSETS = {
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
}


def main() -> int:
    failures = 0
    for rel, url in ASSETS.items():
        dest = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "readingland-fetch"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if len(data) < 2048:
                raise ValueError(f"suspiciously small ({len(data)} bytes)")
            with open(dest, "wb") as fh:
                fh.write(data)
            print(f"OK   {rel}  ({len(data)//1024} KB)")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAIL {rel}: {exc}", file=sys.stderr)
    if failures:
        print(f"\n{failures} asset(s) failed. The app still runs with placeholders.",
              file=sys.stderr)
        return 1
    print("\nAll assets fetched. Run `python main.py` to see the real characters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
