# 7 · Animation Requirements

**Principle: no static screens.** Something is always gently moving, and *every
tap produces animation + sound + visual response*. Animations are implemented
with `kivy.animation.Animation` and the procedural effects in
`readingland/ui/particles.py`.

## Ambient (always-on) motion
| Element | Behaviour | Where |
|---------|-----------|-------|
| Sky | two-band gradient base | `BaseScreen` canvas |
| Clouds | 4 clouds drift L→R, wrap around, varied speeds | `BaseScreen._drift_clouds` (30 fps) |
| Mascot idle | slow opacity "breathing" loop | `Mascot.idle()` |
| "Tap to start" | pulsing opacity | `SplashScreen` |
| Bubbles | occasional rising bubbles | `particles.rising_bubbles` |

## Interaction feedback (per tap)
| Trigger | Animation | Sound |
|---------|-----------|-------|
| Button press | opacity dip + (hook for scale) | `pop` |
| Tile tap | opacity dip | `tap` |
| Correct | tile **green flash**, mascot **hop** (`out_back`/`out_bounce`), star counter bump, star-pop particles | `correct` |
| Wrong | tile **coral flash** (color animates back), mascot gentle react | `wrong` (soft) |
| Word read (Stages 5/6) | each word **scales up + tints**, then settles (karaoke) | per-word VO |
| Blend (Stage 3) | phoneme tiles flash on tap, then fade together | per-phoneme VO |
| Page turn (Stage 6) | (hook for slide) + re-narrate | `page` |

## Celebration system (`particles.celebrate`)
Triggered on mastered item / stage unlock / chest / book finish:
- **Confetti burst** (20–44 rounded particles, gravity arcs, fade).
- **Balloons** float up (big wins).
- **Bubbles** rise (big wins).
- **Star pop** radial burst at the tapped tile (small wins).

```
celebrate(big=True)  → confetti(44) + balloons(5) + bubbles(10)
celebrate(big=False) → confetti(20)
star_pop(center)     → 10 stars radiate & shrink
```

## Mascot reaction set (per character, see character bible)
`idle · happy(hop) · encourage · point · talk · celebrate`. Placeholder mascot
uses a drawn blob + emoji face with hop/breathe; production uses sprite-sheet or
rigged (Spine) animation swapped behind the same `Mascot` API
(`idle()`, `react()`, `say()`).

## Timing & easing guidelines
- Feedback animations: **80–250 ms** (snappy, toddler attention).
- Celebrations: **0.7–1.5 s** particle lifetimes.
- Auto-advance after correct: **~1.6–1.8 s** (time to enjoy the win).
- Easings: `out_back`/`out_bounce` for playful pops; `out_quad`/`in_out_sine`
  for particles and drifts.

## Performance budget (tablet-first)
- Target **60 fps**; particles are lightweight `Widget`s that **self-remove** on
  completion (no leaks).
- Cap simultaneous particles (~44 confetti) to stay smooth on low-end Android.
- Prefer `Animation` (GPU-friendly property tweens) over per-frame Python loops.
- Cloud drift runs at 30 fps (ambient, imperceptible vs 60).

## Accessibility toggles (future-ready)
A "reduce motion" setting (parent dashboard) can disable ambient drift and shrink
celebrations for sensory-sensitive children — see
[`docs/16_future_roadmap.md`](16_future_roadmap.md).
