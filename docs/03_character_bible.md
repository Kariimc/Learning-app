# 3 · Character Bible

ReadingLand's cast are recurring friends. Children should feel attached to them,
so each has a clear personality, role, voice and animation set. The canonical
data lives in [`readingland/content/characters.json`](../readingland/content/characters.json)
(swap art/voice without code changes).

---

## 🐰 Reading Rabbit — *Primary teacher*
- **Role:** the friendly face of the app; guides Stages 1–2 (visuals & letters).
- **Personality:** warm, patient, endlessly encouraging. Never rushes.
- **Color:** bubblegum pink `#FF8FB1`. **Catchphrase:** "Hop along, let's learn!"
- **Voice:** high pitch, gentle pace, high warmth.
- **Signature animations:** ear-wiggle idle, big hop on correct, ears-droop
  "let's try again" (soft, never sad).
- **Key lines:** greet, intro_letter, correct, retry, goodbye.

## 🐻 Benny Bear — *Phonics coach*
- **Role:** Stage 3 — sounds & blending.
- **Personality:** big, gentle, steady; turns blending into a clap/drum game.
- **Color:** tangerine `#FF9F1C`. **Catchphrase:** "Let's sound it out!"
- **Voice:** low pitch, steady pace, high warmth.
- **Signature animations:** claps per phoneme, "slides" letters together on
  blend, paws-up cheer.

## 🐧 Penny Penguin — *Reading buddy*
- **Role:** Stages 4–5 — words & sentences.
- **Personality:** bubbly, sporty, quick; makes reading a race the child wins.
- **Color:** sky blue `#2E9BD6`. **Catchphrase:** "Slide into reading!"
- **Voice:** mid pitch, lively pace, high warmth.
- **Signature animations:** belly-slide entrance, flipper point at each word as
  it highlights, flappy celebration.

## 🦉 Ollie Owl — *Storyteller*
- **Role:** Stage 6 — read-along books.
- **Personality:** wise, cozy, theatrical; reads with character voices by
  lamplight. The bedtime-story friend.
- **Color:** grape `#9B5DE5`. **Catchphrase:** "Once upon a time…"
- **Voice:** mid pitch, expressive pace, high warmth.
- **Signature animations:** wing turns the page, head-tilt "whoo?", glasses
  glint, gentle blink while narrating.

## 🐵 Milo Monkey — *Celebration host*
- **Role:** rewards, stickers, treasure chests, daily goals — appears on wins.
- **Personality:** silly, bouncy, confetti-everywhere joy.
- **Color:** mint `#3DDC97`. **Catchphrase:** "Party time! You earned it!"
- **Voice:** high pitch, excited pace, high warmth.
- **Signature animations:** somersault, balloon release, chest-open drumroll.

---

## Voice-line matrix (recording checklist)

Each character needs these lines recorded per voice pack. Keys map to
`AudioManager.voice_path()` lookups.

| Character | Lines |
|-----------|-------|
| Reading Rabbit | greet · intro_letter · correct · retry · goodbye |
| Benny Bear | greet · blend · correct · retry · goodbye |
| Penny Penguin | greet · read_word · correct · retry · goodbye |
| Ollie Owl | greet · read_line · page_turn · the_end · goodbye |
| Milo Monkey | celebrate · sticker · chest · badge |

Templated lines use `{label}`, `{word}`, `{p1}/{p2}/{p3}` placeholders. For
shipped packs, record the common phrases and the per-item words (e.g. each
letter, each sight word). Any item lacking a recording is covered by the TTS
fallback so nothing is ever silent. See [`docs/08_audio_requirements.md`](08_audio_requirements.md).

## Unlock schedule (collectible cast)
Children "collect" characters as they progress, reinforcing attachment:

| Unlocks at | Character |
|------------|-----------|
| Start | Reading Rabbit |
| Stage 2 unlocked | Milo Monkey |
| Stage 3 unlocked | Benny Bear |
| Stage 4 unlocked | Penny Penguin |
| Stage 6 unlocked | Ollie Owl |

(Implemented in `core/rewards.py → evaluate_milestones`.)

## Art direction for characters
Rounded, soft, chunky shapes; big expressive eyes; 2–3 frame "squash & stretch"
reactions; consistent 1px-free vector look. Each character ships as a sprite
sheet of poses (idle, happy, encourage, point, celebrate) — see
[`docs/06_asset_list.md`](06_asset_list.md) and [`docs/07_animation_requirements.md`](07_animation_requirements.md).
