# 4 · UI/UX Mockups

Landscape, tablet-first. Every screen has the living animated sky behind it
(gradient + drifting clouds + occasional bubbles). Wireframes below are the
*implemented* layouts — run `scripts/smoke_run.py` to generate real PNG
screenshots of each into `screenshots/`.

> UX laws applied: huge tap targets (≥88dp), one-tap actions, no typing, no
> reading required to navigate, immediate audio-visual feedback on every tap,
> and a child-lock math gate in front of anything parent-facing.

---

## Splash / Welcome
```
┌───────────────────────────────────────────────┐
│                 ReadingLand                     │  ← big wordmark
│             From pictures to stories!           │
│                                                 │
│                   ( 🐰 )                         │  ← Reading Rabbit, idle bounce
│                                                 │
│             ✨ Tap anywhere to start ✨          │  ← pulsing
└───────────────────────────────────────────────┘
Tap anywhere → Profile Select.  Rabbit greets aloud.
```

## Profile Select — "Who's reading today?"
```
┌───────────────────────────────────────────────┐
│            Who's reading today?                 │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│   │  Mia    │  │ Sam     │  │   New   │         │
│   │  ( 🐰 ) │  │ ( 🐧 )  │  │   ➕    │         │
│   └─────────┘  └─────────┘  └─────────┘         │
│                                    [ 👪 Parents ]│  ← gated
└───────────────────────────────────────────────┘
Tap a child → Home. "New" → avatar picker (no keyboard).
```

## Home World Map — the hub
```
┌───────────────────────────────────────────────┐
│ [🔄]      Hi, Mia!            ⭐ 42      ( 🐰 ) │  top bar
│  ┌───────────────────────────────────────────┐ │
│  │ [👀] Look & Learn      ▓▓▓▓▓▓▓░░  12/20    │ │ scrollable
│  │ [🔤] Letter Land       ▓▓▓░░░░░░   5/26    │ │ "land path"
│  │ [🔒] Sound Forest      locked              │ │
│  │ ...                                        │ │
│  └───────────────────────────────────────────┘ │
│ [🎁]            ⭐ Daily goal: 3/5              │
└───────────────────────────────────────────────┘
Unlocked land → its stage.  🎁 → Rewards Room.
```

## Stage activity (find/match — Stages 1, 2, 4)
```
┌───────────────────────────────────────────────┐
│ [←]        Letter Land        ⭐ 42      [🔊]   │
│             Find N!  N is for Nest              │  ← prompt bubble
│ (🐻)   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐      │
│        │ 🐋   │ │ 👑   │ │ 🎩   │ │ 🪺   │      │  ← picture
│        │  W   │ │  Q   │ │  H   │ │  N   │      │  ← letter
│        └──────┘ └──────┘ └──────┘ └──────┘      │
│  ▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░ (stage progress)       │
└───────────────────────────────────────────────┘
Correct → green flash + confetti + mascot hop + star.
Wrong   → coral flash + "Good try!" + re-narrate (no block).
```

## Stage 3 — Phonics blending
```
┌───────────────────────────────────────────────┐
│            Tap each sound, then find the pic!   │
│ (🐻)        [ c ]  [ a ]  [ t ]                 │  ← tap L→R, each plays its sound
│                  ↓ blend ↓                      │
│                  "cat!"                          │
│             ┌────┐  ┌────┐  ┌────┐              │
│             │ 🐱 │  │ 🐶 │  │ 🐷 │              │  ← pick matching picture
│             └────┘  └────┘  └────┘              │
└───────────────────────────────────────────────┘
```

## Stage 5 — Sentence read-along (karaoke)
```
┌───────────────────────────────────────────────┐
│   The   cat   runs   .                          │  ← each word enlarges+tints as spoken
│ (🐧)        [ ▶  Read it! ]                     │
│         Read, then find the picture!            │
│        ┌────┐   ┌────┐   ┌────┐                 │
│        │ 🐱 │   │ 🐶 │   │ 🐦 │                 │
│        └────┘   └────┘   └────┘                 │
└───────────────────────────────────────────────┘
```

## Stage 6 — Storybook reader
```
┌───────────────────────────────────────────────┐
│ Library:  [ 🐱 The Cat Nap ] [ 🐶 The Big Dog ] │
│                ── open a book ──                │
│  ┌───────────────────────────────────────────┐ │
│  │                 ( 🐱 )                     │ │  ← scene, tappable object
│  └───────────────────────────────────────────┘ │
│        The   cat   sat   .                      │  ← word highlighting
│     [ ◀ ]      [ 🔊 Read ]      [ ▶ ]   (🦉)    │
└───────────────────────────────────────────────┘
Finish last page → big celebration, book mastered.
```

## Rewards Room — sticker book + badges
```
┌───────────────────────────────────────────────┐
│ [←]        My Treasures        ⭐ 42     (🐵)   │
│            [ 🎁 Open daily chest ]              │
│  My Stickers:  🌟 🍎 🐱 ❔ ❔ ❔ ❔ ❔             │  ← owned bright, locked faded
│  My Badges:    👣 🔤 🔒 🔒 🔒 🔒 🔒             │
└───────────────────────────────────────────────┘
```

## Parent Dashboard (behind math gate)
```
┌───────────────────────────────────────────────┐
│ Mia — overview                                  │
│  Overall 6%   Current land: Letter Land         │
│  Stars 42     Accuracy 92%                       │
│  Mastered 5/89  Streak 🔥3   Time(7d) 24 min     │
│  Progress by land:  ▓▓▓▓░░  per-stage bars       │
│  Recent activity:   timestamps + ✓/↻            │
│  Settings: [Sound On] [Switch child]            │
└───────────────────────────────────────────────┘
```

## Visual language
- **Palette:** `config.PALETTE` — bright sky blues, sun yellow, coral, mint,
  grape, bubblegum, cream surfaces, soft ink text. Each land has its own accent.
- **Shapes:** big rounded rectangles (radius ~28dp), soft drop shadows, no hard
  edges, no dense text.
- **Type scale:** display 96 / title 40 / heading 30 / body 22 / label 18.
- **Feedback:** green = correct, coral = gentle retry (never red/harsh).
- **Motion:** nothing is ever fully still (see [`docs/07`](07_animation_requirements.md)).
