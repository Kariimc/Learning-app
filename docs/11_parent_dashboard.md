# 11 · Parent Dashboard

A calm, data-rich area for grown-ups, kept behind a **child-lock math gate** so
young children can't wander in. Implemented in
`readingland/screens/parent_dashboard.py`; data from `core/analytics.py`.

## Access
Profile Select → **👪 Parents** → `ParentGate` ("For grown-ups: what is 7 × 8?")
→ on correct answer, opens the dashboard. A wrong answer simply re-rolls the
question.

## What it shows

### Overview KPIs (per child)
| KPI | Source |
|-----|--------|
| Overall progress % | mastered ÷ total items across all stages |
| Current land | highest unlocked stage |
| Stars earned | `stars.total` |
| Accuracy | correct ÷ total answers (event log) |
| Items mastered | e.g. 23 / 89 |
| Day streak 🔥 | consecutive active days |
| Time (7 days) | from `session` events (≈ engaged minutes) |

### Progress by land
A chunky progress bar per stage (Look & Learn → Story Sky) showing
mastered/total and %, with a 🔒 marker on locked lands — an at-a-glance map of
where the child is and what's next.

### Recent activity
The last ~8 events with timestamps and a ✓ / ↻ marker (correct / retried), so a
parent can see what was practiced and how it went.

### Settings / management
- **Sound On/Off** (`AudioManager.enabled`).
- **Switch child** (back to profile select).
- (Extensible: rename/delete profile, reduce-motion, daily-goal size, reset
  progress — all backed by existing `ProfileManager` / `config` hooks.)

## Privacy & analytics philosophy
- **100% on-device.** Every number is computed locally from the SQLite event log;
  nothing is uploaded or shared. No accounts, no tracking, no ads.
- The dashboard is **insight, not surveillance** — it celebrates growth (streaks,
  mastery, time) and points to the next skill, never shames mistakes.

## How analytics are computed (`Analytics.report`)
```
accuracy            = SUM(correct) / COUNT(answers)
active_days_streak  = consecutive calendar days with ≥1 event (today/yesterday start)
minutes_last_7_days = SUM(session seconds)/60, else ≈ answers×20s estimate
current_stage       = highest unlocked stage
stage_breakdown     = per-stage mastered/total/% (+ unlocked flag)
recent_activity     = last N events, humanized
```
Returns a `DashboardReport` dataclass the screen renders into cards.

## Roadmap (see [`docs/16`](16_future_roadmap.md))
Weekly email-free PDF summary export, multi-child comparison, skill-gap
highlights ("ready for blends!"), and recommended next activities.
