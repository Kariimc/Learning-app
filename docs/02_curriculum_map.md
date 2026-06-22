# 2 · Educational Curriculum Map

ReadingLand's curriculum is grounded in the **science of reading**: a structured,
systematic, explicit progression from oral/visual skills → phonemic awareness →
phonics → fluency → comprehension. Each stage is a "land" on the world map and a
JSON content pack the app loads at runtime.

## Progression overview

```
Stage 1  VISUAL RECOGNITION   ──►  Stage 2  ALPHABET MASTERY
   shapes/colors/animals            letter names + sounds
   (pre-reading, ages 2-3)          (ages 3-4)
        │                                 │
        ▼                                 ▼
Stage 3  PHONICS FOUNDATIONS  ──►  Stage 4  WORD READING
   blending c-a-t → cat              nouns, verbs, sight words
   (ages 4-5)                        (ages 4-6)
        │                                 │
        ▼                                 ▼
Stage 5  SENTENCE READING     ──►  Stage 6  STORY READING
   "The cat runs." karaoke           interactive read-along books
   (ages 5-7)                        (ages 5-8)
```

## Stage detail

### Stage 1 — Visual Recognition (Look & Learn)
- **Goal:** build attention, vocabulary, visual discrimination & matching. *No
  reading.* Everything narrated.
- **Content:** 5 shapes, 5 colors, 5 animals (with animal sounds), 5 objects.
- **Activity:** "Find the …" picture matching.
- **Mastery skill:** match a named picture to its image by sight + sound.

### Stage 2 — Alphabet Mastery (Letter Land)
- **Goal:** letter names, **letter sounds** (the foundation of phonics), and the
  alphabetic principle (letters map to sounds).
- **Content:** all 26 letters, each with name, sound, and an example word
  (`A → Apple → "ah"`).
- **Activity:** hear name+sound+word → find the matching letter.
- **Mastery skill:** recognize a letter from its name and/or sound.

### Stage 3 — Phonics Foundations (Sound Forest)
- **Goal:** **phonemic awareness + blending** — the single biggest predictor of
  reading success. Beginning/ending sounds, rhyming families, sound blending.
- **Content:** 12 CVC words, each split into phonemes with per-phoneme sounds and
  rhyme families.
- **Activity:** tap each sound left-to-right (`c-a-t`), watch them blend, then
  pick the matching picture.
- **Mastery skill:** orally blend phonemes into a word and map it to meaning.

### Stage 4 — Word Reading (Word Town)
- **Goal:** decode and instantly recognize first words; build a sight-word bank.
- **Content:** picture nouns, action verbs, and high-frequency **sight words**
  (the, is, a, can, see, go, happy).
- **Activity:** see a picture/prompt → choose the matching written word.
- **Mastery skill:** read a single word (decodable or sight) on sight.

### Stage 5 — Sentence Reading (Sentence River)
- **Goal:** fluency, left-to-right tracking, word-by-word reading, basic syntax.
- **Content:** simple sentences built **only from words the child has met**
  ("The cat runs.", "The bird can fly.").
- **Activity:** karaoke read-along — each word highlights as it's spoken — then
  match the sentence to a picture (comprehension check).
- **Mastery skill:** read a full sentence and connect it to meaning.

### Stage 6 — Story Reading (Story Sky)
- **Goal:** comprehension, stamina, joy of reading; print concepts (pages,
  left-to-right, return sweep).
- **Content:** very short multi-page interactive storybooks with one tappable
  object per page.
- **Activity:** read-along with word highlighting and character voices; turn
  pages; finish the book.
- **Mastery skill:** read a short book start-to-finish with support fading.

## Skill scaffolding within every activity

| Lever | Easier | Harder |
|-------|--------|--------|
| Answer choices | 2 | 3 → 4 |
| Hints / extra narration | on | off |
| Item selection | weak/unseen items surfaced first (spaced practice) | |

Difficulty auto-adjusts per child (see `core/adaptive.py`,
[`docs/12_progress_tracking.md`](12_progress_tracking.md)).

## Spiral review
The adaptive engine weights **unseen and not-yet-mastered** items higher but
keeps recycling mastered items at a low rate, so earlier skills stay fresh as new
ones are introduced.

## Extending the curriculum
Every list above lives in `readingland/content/*.json`. Add vowel teams,
digraphs, blends, longer stories, a second language pack, etc. by adding items or
a new pack — see [`docs/17_content_authoring.md`](17_content_authoring.md).
