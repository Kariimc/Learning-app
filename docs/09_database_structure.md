# 9 · Database Structure

Storage is **local SQLite** (`readingland/core/database.py`), created in the
OS-appropriate `user_data_dir`. No server, no network — the app is fully offline
and private. Schema is created idempotently and versioned (`meta.schema_version`)
for forward migration.

## Entity-relationship overview

```
profiles 1───∞ progress        (mastery per content item)
profiles 1───∞ stage_state      (unlock + adaptive difficulty per stage)
profiles 1───∞ rewards          (stickers, badges, characters, chests)
profiles 1───1 stars            (running star total)
profiles 1───∞ events           (analytics log: answers, sessions, rewards)
meta (key/value)                (schema_version, etc.)
```
All child tables use `ON DELETE CASCADE`, so deleting a profile cleans up
everything for that child.

## Tables

### `profiles`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| name | TEXT | first name / nickname (≤24 chars) |
| avatar | TEXT | character id (default `reading_rabbit`) |
| birth_year | INTEGER | optional; suggests a starting stage |
| created_at / last_active | REAL | epoch seconds |
| settings | TEXT (JSON) | per-child prefs |

### `progress` — mastery per item
| Column | Type | Notes |
|--------|------|-------|
| profile_id | FK | |
| stage | INTEGER | 1–6 |
| item_id | TEXT | content id |
| mastery | INTEGER | 0 … `MASTERY_THRESHOLD` (3) |
| attempts / correct | INTEGER | counters |
| last_seen | REAL | for spaced practice |
| | | `UNIQUE(profile_id, stage, item_id)` |

### `stage_state` — unlock + adaptivity
| Column | Type | Notes |
|--------|------|-------|
| profile_id, stage | PK | |
| unlocked | INTEGER | 0/1 |
| difficulty | REAL | 0..1 adaptive level |
| streak | INTEGER | correct-in-a-row |

### `rewards`
| Column | Type | Notes |
|--------|------|-------|
| profile_id | FK | |
| kind | TEXT | `sticker · badge · character · chest` |
| reward_id | TEXT | catalogue id |
| earned_at | REAL | |
| | | `UNIQUE(profile_id, kind, reward_id)` → idempotent |

### `stars`
`profile_id PK`, `total INTEGER`. Stars are only ever added.

### `events` — analytics log
| Column | Type | Notes |
|--------|------|-------|
| profile_id | FK | |
| ts | REAL | epoch |
| kind | TEXT | `answer · session · reward · stage_unlock` |
| stage, item_id | | context |
| correct | INTEGER | 0/1/NULL |
| payload | TEXT | e.g. session seconds |

Indexes: `idx_events_profile_ts`, `idx_progress_profile`.

## Why a single local SQLite file?
- **Offline-first & private** — no data leaves the device; COPPA-friendly.
- **Crash-safe auto-save** — every answer is committed immediately in a
  transaction (`Database.tx()`), so closing the app loses nothing.
- **Cheap analytics** — the event log is all the parent dashboard needs; reports
  are computed on demand (`core/analytics.py`).

## Migration strategy
`SCHEMA_VERSION` + the `meta` table gate future `ALTER`/backfill steps. New
tables/columns are added in `_create_schema` with `IF NOT EXISTS`, keeping
upgrades non-destructive. (Roadmap: cloud sync/export is opt-in only — see
[`docs/16`](16_future_roadmap.md).)

## Example: a child's day, in rows
```
events:   answer stage=2 item=A correct=1   (×3 over the day)
progress: (2, A) mastery 3, attempts 3, correct 3
rewards:  sticker 'happy_apple' (mastered A)  ·  badge 'first_steps'
stars:    total += 3 + 1 + 1
stage_state: (2) difficulty 0.12, streak reset; later (3) unlocked=1
```
