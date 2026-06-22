# 17 · Content Authoring Guide

ReadingLand's curriculum is **data, not code**. You can add letters, words,
sentences, stories, characters and even whole modules by editing JSON in
`readingland/content/` — no Python changes, no rebuilds of the engine.

## Golden rules
1. Every item needs a **unique `id`** within its pack.
2. `label` is what's shown/read; `narration` is what the narrator says.
3. `id` doubles as the **asset stem** — name art/voice files to match
   (`cat.png`, `voice/<pack>/cat.ogg`) and they're picked up automatically.
4. Run `pytest tests/test_content.py` after editing — it validates every pack.

## Item schema (common)
```json
{
  "id": "cat",
  "label": "cat",
  "narration": "cat",
  "emoji": "🐱",
  "color": "#FF9F1C"
}
```
Anything extra you add (e.g. `phonemes`, `words`, `pages`, `kind`) is preserved
in `ContentItem.data` and read by that stage's screen.

## Add a new letter (Stage 2)
Append to `content/alphabet.json → items`:
```json
{ "id": "Æ", "label": "Æ", "lower": "æ", "name": "ash", "sound": "a",
  "word": "Ash", "emoji": "🌳", "color": "#7AC74F", "narration": "Æ. a. Ash." }
```

## Add a new word (Stage 4)
```json
{ "id": "moon", "label": "moon", "kind": "noun", "emoji": "🌙",
  "color": "#9B5DE5", "narration": "moon" }
```
`kind`: `noun` / `verb` / `sight` (sight words show no picture hint).

## Add a CVC blend (Stage 3)
```json
{ "id": "hen", "label": "hen", "phonemes": ["h","e","n"],
  "sounds": ["huh","eh","nnn"], "emoji": "🐔", "color": "#FF6B6B",
  "rhymes": ["pen","ten"], "narration": "huh, eh, nnn. hen!" }
```

## Add a sentence (Stage 5)
Use only words children have already met. `words` drives the karaoke highlight.
```json
{ "id": "s_moon_up", "label": "The moon is up.",
  "words": ["The","moon","is","up","."], "emoji": "🌙",
  "color": "#9B5DE5", "narration": "The moon is up." }
```

## Add a storybook (Stage 6)
```json
{
  "id": "story_little_hen", "label": "The Little Hen", "emoji": "🐔",
  "color": "#FF6B6B", "narration": "Let's read The Little Hen.",
  "pages": [
    { "text": "The hen ran.", "words": ["The","hen","ran","."],
      "scene": "yard", "interactive": { "emoji": "🐔", "tap_says": "cluck!" } }
  ]
}
```

## Add a character
Append to `content/characters.json → characters` with `id, name, role, color,
emoji, personality, catchphrase, voice, voice_lines`. Reference its `id` as a
stage `guide` in `config.STAGES` or as an unlockable in `core/rewards.py`.

## Add a whole new stage/module
1. Add an entry to `config.STAGES` (`id, key, title, content, guide`).
2. Create `content/<your>.json`.
3. Add a `screens/stageN_*.py` (subclass `BaseScreen`, or `MatchingStageScreen`
   if it's a find/match game).
4. Register it in `app.py._register_screens`.
That's the entire surface area — the engine, progress, rewards and analytics pick
it up automatically.

## Validation
```bash
pytest tests/test_content.py     # packs load, no duplicate ids, non-empty
python -c "from readingland.core.content import ContentLibrary as C; print(C().validate() or 'OK')"
```

## Tips for good content
- Keep `narration` short and warm; match how the sound is taught aloud.
- Re-use earlier vocabulary as you climb stages (spiral review).
- Pick emoji/art that's unambiguous for a 2–5 year old.
- Use the per-item `color` to make tiles pop and aid memory.
