# 12 · Progress Tracking & Adaptive Learning

Two cooperating systems: **ProgressTracker** (what the child has learned) and
**AdaptiveEngine** (how hard to make the next question). Both are pure-Python and
unit-tested (`tests/test_progress.py`, `tests/test_adaptive.py`).

## Mastery model
- Each content item has a **mastery score** `0 … MASTERY_THRESHOLD` (default 3).
- A **correct** answer +1 (capped at threshold); an item at threshold is
  **mastered**.
- A **wrong** answer **never decreases** mastery, never costs stars, never blocks
  progress — it only signals the adaptive engine to add support.

```python
result = progress.record_answer(pid, stage, item_id, correct)
# → AnswerResult(correct, first_try, mastery, mastered_now,
#                stars_awarded, stage_unlocked)
```

## Stars (motivation, never punitive)
- First-try correct: **+3** (`STARS_PER_PERFECT`).
- Later correct: **+1** (`STARS_PER_CORRECT`).
- Stars only accumulate; spent only on cosmetic delight (chest bonuses).

## Stage unlocking
When a child masters **≥ 70%** (`STAGE_UNLOCK_RATIO`) of a land's items, the next
land unlocks (with a character + sticker celebration). Stage 1 is always
unlocked. Logic: `ProgressTracker._maybe_unlock_next`.

## Adaptive difficulty (`AdaptiveEngine`)
A per-(child, stage) `difficulty ∈ [0,1]` and a running `streak`:
- **3 correct in a row** (`ADAPTIVE_STREAK_UP`) → difficulty **+0.12**, streak
  resets.
- **Any miss** → difficulty **−0.18** (more support immediately) and streak
  resets.

Difficulty drives **scaffolding**:
| difficulty | answer choices | hints |
|------------|----------------|-------|
| < 0.34 | 2 | on |
| 0.34–0.67 | 3 | on (<0.5) |
| ≥ 0.67 | 4 | off |

So a confident child gets more options and less hand-holding; a struggling child
gets a gentle 2-choice, hint-rich experience. The child is always in their
**zone of proximal development** and success stays frequent.

## Spaced practice (item selection)
`AdaptiveEngine.next_item` weights items by `(MASTERY_THRESHOLD − mastery) + 1`,
so **unseen and weak items surface most**, mastered items least (but still recur
for review). `session_plan` builds a short, varied daily set, avoiding immediate
repeats.

## Daily goals & streaks
- Completing `DAILY_GOAL_ACTIVITIES` (default 5) activities fills the **daily
  treasure chest** (claimable in the Rewards Room for bonus stars).
- Consecutive active days build a **streak** shown to parents and rewarded with
  the "On Fire" badge.

## Auto-save & resume
Every answer is committed immediately (SQLite transaction). There is no "save"
button and no way to lose progress — closing or crashing the app resumes exactly
where the child left off.

## Summaries surfaced to UI
```python
session.stage_summary(stage)   # StageSummary(unlocked, total, mastered, %, ratio)
progress.overall_percent(pid)  # whole-app %
progress.item_mastery(pid, s)  # {item_id: mastery} for map dots / story library
```

## Tuning
All knobs live in `readingland/config.py` (`MASTERY_THRESHOLD`,
`STAGE_UNLOCK_RATIO`, `STARS_PER_*`, `ADAPTIVE_*`, `DAILY_GOAL_ACTIVITIES`) — one
file to retune pacing for an age band or a research finding.
