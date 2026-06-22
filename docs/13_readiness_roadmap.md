# 13 · Readiness Roadmap — from pictures to independent reading

This is the child's journey: the concrete skills, the in-app experience, and the
"you're ready for the next thing" signals that move a learner from *recognizing a
picture* to *reading a storybook alone*.

```
 PICTURES → LETTERS → SOUNDS → WORDS → SENTENCES → STORIES → INDEPENDENT READER
   S1         S2        S3       S4        S5          S6
```

## Milestone ladder

### 🟢 Stage 1 — "I can recognize and match pictures"
- **Can do:** point to a named shape/color/animal/object; match picture to word
  spoken aloud.
- **In app:** narrated "Find the…" tap games; no text needed.
- **Ready for letters when:** reliably matches pictures by sight + sound
  (≥70% mastered) → **Letter Land unlocks**.

### 🟠 Stage 2 — "I know my letters and their sounds"
- **Can do:** name letters; produce/recognize each letter's sound; know the
  alphabetic principle (letters = sounds).
- **In app:** "A. Ah. Apple." teaching + find-the-letter games with picture cues.
- **Ready for phonics when:** recognizes most letters by name/sound (≥70%) →
  **Sound Forest unlocks**.

### 🟣 Stage 3 — "I can blend sounds into words"
- **Can do:** segment and **blend** c-a-t → "cat"; hear beginning/ending sounds;
  recognize rhymes. *(The pivotal decoding skill.)*
- **In app:** tap-the-sounds blending + match the picture.
- **Ready to read words when:** blends CVC words and maps them to meaning (≥70%)
  → **Word Town unlocks**.

### 🔴 Stage 4 — "I can read words"
- **Can do:** decode simple words; instantly recognize a bank of sight words.
- **In app:** picture → choose the matching word.
- **Ready for sentences when:** reads single words on sight (≥70%) → **Sentence
  River unlocks**.

### 🔵 Stage 5 — "I can read sentences"
- **Can do:** track left-to-right, read word-by-word, connect a sentence to
  meaning; basic fluency.
- **In app:** karaoke read-along (words highlight as spoken) + comprehension
  picture match.
- **Ready for stories when:** reads simple sentences with support fading (≥70%)
  → **Story Sky unlocks**.

### 🌸 Stage 6 — "I can read a book"
- **Can do:** read a short multi-page book, turn pages, follow a narrative, enjoy
  reading; print concepts.
- **In app:** interactive read-along books with word highlighting + tappable
  scenes; support gradually fades.
- **Independent reader when:** finishes books with minimal narration support and
  chooses to read for fun.

## How support fades (gradual release)
| | S1–2 | S3–4 | S5 | S6 |
|--|------|------|----|----|
| Narration | full, every item | full + sound-out | word highlight + replay | line read + child re-reads |
| Choices | 2 (then adaptive) | adaptive 2–4 | adaptive | self-paced pages |
| Child's role | match | blend | decode | read sentences | read & comprehend |

The adaptive engine ([`docs/12`](12_progress_tracking.md)) keeps each step in the
child's success zone, so confidence compounds.

## Typical age mapping (a guide, not a gate)
| Age | Likely land(s) |
|-----|----------------|
| 2–3 | Look & Learn |
| 3–4 | Letter Land |
| 4–5 | Sound Forest → Word Town |
| 5–6 | Word Town → Sentence River |
| 6–8 | Sentence River → Story Sky → independent |

Children roam freely; the map suggests but never forces. `ProfileManager.
suggested_stage(birth_year)` only sets a friendly starting point.

## The promise
By the end of Story Sky, a child has traveled the full arc — **picture → letter →
sound → word → sentence → story** — and reads beginner storybooks on their own,
having had fun the entire way and never once been told they were wrong.
