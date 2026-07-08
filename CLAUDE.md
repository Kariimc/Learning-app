# CLAUDE.md — playbook for working on ReadingLand

ReadingLand is an offline early-literacy app for young kids (Python + Kivy), 6
"lands" from picture-recognition to read-along storybooks. Pure-Python engine in
`readingland/core/` (never imports Kivy); content is data in
`readingland/content/*.json`.

## Standing preferences (the owner's rules — follow without being asked)

- **Always use the real generated assets, never placeholder/emoji versions.**
  The end-user experience uses the Higgsfield-generated art + Mabel voice pack.
  If something would render with placeholders, pull the real assets first
  (`python scripts/fetch_assets.py`). Don't ship the "developer/placeholder"
  look.
- **Take action; don't ask permission for obvious, in-scope steps.** Pull the
  assets, wire them in, commit. Only ask when there's a genuine fork.
- **Any command for the owner to run goes in a Markdown code block** (so the
  one-click copy button renders). Never make them hand-select text.
- **Check what already exists before building** (read `scripts/fetch_assets.py`,
  `assets/README.md`, look in `assets/`). Don't rebuild a placeholder when real
  art/pipeline already exists.

## Skills live in a separate repo: `Kariimc/my-skills` (public)

The owner's skills (e.g. **visual-prototype** = the "Interactive Prototype"
skill that builds a clickable single-file HTML mockup with a Tweak & Comment
review overlay) are in the public repo `Kariimc/my-skills` under `skills/`.

In a **cloud** session the GitHub MCP + `git` are scoped to this repo only, so
they can't read `my-skills`. Because it's **public**, fetch it directly via the
GitHub REST API over normal egress (this is allowed and fast — don't spend time
rediscovering it):

```bash
curl -s "https://api.github.com/repos/Kariimc/my-skills/git/trees/master?recursive=1" | grep -o 'skills/[^"]*'
curl -s -H "Accept: application/vnd.github.raw" "https://api.github.com/repos/Kariimc/my-skills/contents/skills/visual-prototype/SKILL.md?ref=master"
```

## Production assets: generated in Higgsfield, fetched by script

Real art (characters, land backgrounds, plush buttons, storybooks) and the
Mabel voice pack are generated in Higgsfield. **They now live in the repo,
tracked with Git LFS** (see `.gitattributes` — every `*.png/.jpg/.jpeg/.mp3/
.wav/.mp4/.glb/.ttf` is an LFS object). So the normal way to get the real files
into any clone is simply:

```bash
git lfs install
git lfs pull
```

`scripts/fetch_assets.py` maps every asset URL → its correct `assets/...` path;
the app auto-uses each file when present and falls back to placeholders + TTS
when not. Use it to (re)populate `assets/` or to add newly generated art.

**Cloud caveat:** the cloud environment's network policy 403s the Higgsfield
CDN (`*.cloudfront.net`), `drive.google.com`, and the bare LFS CDN host — but
`git lfs pull` works in the cloud anyway, because the objects are fetched over
GitHub's signed-URL LFS transfer, which the proxy allows. Do NOT route around
the egress policy. Three ways to get bytes in, in order of preference:
1. `git lfs pull` — the assets are already in LFS on the remote, so this is all
   you normally need, cloud or local.
2. From a local folder of the raw Higgsfield exports (e.g. a Google Drive
   download — the files are named by job id, exactly the tail of each CDN URL):
   `python scripts/fetch_assets.py --from <folder>` copies each into place, then
   `git add assets && git commit` re-stores them through LFS. Use this to
   recover/refresh if any LFS object is ever missing.
3. `python scripts/fetch_assets.py` (network) on a machine with open internet.

When new art is generated in Higgsfield, add its URL→path mapping to
`scripts/fetch_assets.py` so it self-files, and commit it (LFS handles the
binary).

## Prototypes

`prototypes/readingland-flow.html` — single-file clickable prototype of the full
child flow (map → activity → celebration), built with the visual-prototype
skill. It references the real Higgsfield asset URLs (rendering them when opened
with internet) and falls back to emoji/color when offline.
