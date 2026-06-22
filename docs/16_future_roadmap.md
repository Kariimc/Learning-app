# 16 · Future Expansion Roadmap

The architecture is built to grow. Below is a staged roadmap; everything maps to
an existing extensibility seam (see [`docs/15`](15_technical_design.md)).

## Near-term (content & polish)
- **More content packs:** vowel teams, consonant digraphs (sh/ch/th), blends
  (st/cr), word families, more sight-word levels, more storybooks. *(JSON only.)*
- **Production art & voice packs** replacing placeholders (`docs/06`, `docs/08`).
  *(In progress: AI-generated mascot portraits + app icon ship via
  `scripts/fetch_assets.py`; the `Mascot` widget already renders them.)*
- **Reduce-motion & high-contrast** accessibility toggles in the parent
  dashboard.
- ✅ **Letter tracing activities** — guided finger-trace of letter strokes with
  visual guides. *Done:* `core/tracing.py` + `screens/tracing.py`, reachable from
  the world map; feeds Stage 2 mastery.
- **Word-building mini-game** — drag letters to spell a pictured word.
- **Lowercase + cursive tracing** — extend `core/tracing.py` with lowercase and
  joined stroke sets.

## Mid-term (features)
- **More mini-games** that reinforce skills: sound-matching, rhyme-sort,
  beginning-sound sort, memory match — each a `BaseScreen` subclass reusing the
  widget kit and the adaptive engine.
- **Pronunciation practice (mic)** — optional speech check using on-device STT,
  privacy-preserving, to confirm a child said the sound/word.
- **Storybook authoring depth** — multi-character voices, branching "what happens
  next?" taps, simple comprehension questions per book.
- **Voice packs as content** — multiple narrator voices/languages selectable per
  child.
- **Localization / multilingual** — parallel content + voice + font packs;
  the loader and lookups already support packs.
- **Parent reports** — exportable weekly PDF summary, skill-gap highlights,
  "what to practice next" suggestions.

## Long-term (platform)
- **Opt-in cloud sync** — back up/restore and sync a child's progress across
  devices (privacy-first, off by default; schema already versioned for this).
- **Curriculum editor** — a tiny tool/UI for educators to author content packs
  without touching JSON by hand.
- **Classroom mode** — multiple profiles, teacher dashboard, group goals.
- **Adaptive content recommendation** — use the analytics log to auto-suggest the
  next pack/skill per child.
- **Plugin modules** — drop-in educational modules (numbers/math, shapes deep
  dive, science words) registered like stages.

## Stretch / research
- **Dyslexia-friendly mode** (OpenDyslexic font option, extra spacing, slowed
  blending).
- **Eye-/attention-aware pacing** on capable devices.
- **A/B-testable pacing knobs** already centralized in `config.py` for
  evidence-based tuning.

## Non-goals (kept deliberately out)
- ❌ Ads, in-app purchases, paywalls.
- ❌ Third-party tracking / data collection.
- ❌ Social features, chat, or external links in the child experience.

These boundaries are part of the product promise: a safe, focused, joyful place
to learn to read.
