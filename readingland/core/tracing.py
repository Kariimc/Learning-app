"""Letter stroke geometry for the tracing activity.

Each uppercase letter is described as an ordered list of **strokes**; each stroke
is a polyline of normalized ``(x, y)`` points in ``[0, 1]`` with **y pointing up**
(Kivy convention). Stroke order and direction follow how the letter is taught by
hand (top-to-bottom, left-to-right).

This is deterministic geometry, so it lives in ``core`` (pure Python) and is
unit-tested. The UI maps these normalized points into the on-screen trace box.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

Point = Tuple[float, float]
Stroke = List[Point]

# Drawing box within the normalized square (margins keep strokes off the edge).
LEFT, RIGHT = 0.28, 0.72
TOP, BOTTOM = 0.86, 0.14
MIDX, MIDY = 0.50, 0.50


def _line(p0: Point, p1: Point, n: int = 14) -> Stroke:
    return [(p0[0] + (p1[0] - p0[0]) * i / (n - 1),
             p0[1] + (p1[1] - p0[1]) * i / (n - 1)) for i in range(n)]


def _poly(points: List[Point], n_each: int = 10) -> Stroke:
    """Chain several corner points into one smooth-sampled polyline stroke."""
    out: Stroke = []
    for a, b in zip(points, points[1:]):
        seg = _line(a, b, n_each)
        out.extend(seg if not out else seg[1:])
    return out


def _arc(cx: float, cy: float, rx: float, ry: float,
         a0: float, a1: float, n: int = 28) -> Stroke:
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / (n - 1)),
             cy + ry * math.sin(a0 + (a1 - a0) * i / (n - 1))) for i in range(n)]


def _build() -> Dict[str, List[Stroke]]:
    P = math.pi
    s: Dict[str, List[Stroke]] = {}

    s["A"] = [_line((MIDX, TOP), (LEFT, BOTTOM)),
              _line((MIDX, TOP), (RIGHT, BOTTOM)),
              _line((0.37, 0.42), (0.63, 0.42))]
    s["B"] = [_line((LEFT, TOP), (LEFT, BOTTOM)),
              _arc(LEFT, 0.68, 0.19, 0.18, P / 2, -P / 2),
              _arc(LEFT, 0.32, 0.21, 0.18, P / 2, -P / 2)]
    s["C"] = [_arc(0.50, 0.50, 0.22, 0.36, P / 3, 5 * P / 3)]
    s["D"] = [_line((LEFT, TOP), (LEFT, BOTTOM)),
              _arc(LEFT, MIDY, 0.34, 0.36, P / 2, -P / 2)]
    s["E"] = [_line((LEFT, TOP), (LEFT, BOTTOM)),
              _line((LEFT, TOP), (RIGHT, TOP)),
              _line((LEFT, MIDY), (0.62, MIDY)),
              _line((LEFT, BOTTOM), (RIGHT, BOTTOM))]
    s["F"] = [_line((LEFT, TOP), (LEFT, BOTTOM)),
              _line((LEFT, TOP), (RIGHT, TOP)),
              _line((LEFT, MIDY), (0.62, MIDY))]
    s["G"] = [_arc(0.50, 0.50, 0.22, 0.36, P / 3, 5 * P / 3),
              _line((0.50, 0.40), (0.66, 0.40)),
              _line((0.66, 0.40), (0.66, 0.20))]
    s["H"] = [_line((LEFT, TOP), (LEFT, BOTTOM)),
              _line((RIGHT, TOP), (RIGHT, BOTTOM)),
              _line((LEFT, MIDY), (RIGHT, MIDY))]
    s["I"] = [_line((0.38, TOP), (0.62, TOP)),
              _line((MIDX, TOP), (MIDX, BOTTOM)),
              _line((0.38, BOTTOM), (0.62, BOTTOM))]
    s["J"] = [_line((0.40, TOP), (0.68, TOP)),
              _poly([(0.60, TOP), (0.60, 0.30)]) + _arc(0.46, 0.30, 0.14, 0.16, 0.0, -P / 2)[1:]]
    s["K"] = [_line((LEFT, TOP), (LEFT, BOTTOM)),
              _line((RIGHT, TOP), (LEFT, MIDY)),
              _line((LEFT, MIDY), (RIGHT, BOTTOM))]
    s["L"] = [_line((LEFT, TOP), (LEFT, BOTTOM)),
              _line((LEFT, BOTTOM), (RIGHT, BOTTOM))]
    s["M"] = [_poly([(LEFT, BOTTOM), (LEFT, TOP), (MIDX, 0.45), (RIGHT, TOP), (RIGHT, BOTTOM)])]
    s["N"] = [_poly([(LEFT, BOTTOM), (LEFT, TOP), (RIGHT, BOTTOM), (RIGHT, TOP)])]
    s["O"] = [_arc(0.50, 0.50, 0.24, 0.36, P / 2, P / 2 + 2 * P)]
    s["P"] = [_line((LEFT, TOP), (LEFT, BOTTOM)),
              _arc(LEFT, 0.68, 0.20, 0.18, P / 2, -P / 2)]
    s["Q"] = [_arc(0.50, 0.50, 0.24, 0.36, P / 2, P / 2 + 2 * P),
              _line((0.58, 0.30), (0.72, 0.12))]
    s["R"] = [_line((LEFT, TOP), (LEFT, BOTTOM)),
              _arc(LEFT, 0.68, 0.20, 0.18, P / 2, -P / 2),
              _line((LEFT, 0.50), (RIGHT, BOTTOM))]
    s["S"] = [_poly([(0.64, 0.78), (0.50, 0.84), (0.36, 0.78), (0.36, 0.62),
                     (0.50, 0.54), (0.64, 0.46), (0.64, 0.28), (0.50, 0.20),
                     (0.36, 0.26)])]
    s["T"] = [_line((0.28, TOP), (0.72, TOP)),
              _line((MIDX, TOP), (MIDX, BOTTOM))]
    s["U"] = [_line((LEFT, TOP), (LEFT, 0.30)) +
              _arc(0.50, 0.30, 0.22, 0.16, P, 2 * P)[1:] +
              _line((RIGHT, 0.30), (RIGHT, TOP))[1:]]
    s["V"] = [_poly([(LEFT, TOP), (MIDX, BOTTOM), (RIGHT, TOP)])]
    s["W"] = [_poly([(LEFT, TOP), (0.40, BOTTOM), (MIDX, 0.55), (0.60, BOTTOM), (RIGHT, TOP)])]
    s["X"] = [_line((LEFT, TOP), (RIGHT, BOTTOM)),
              _line((RIGHT, TOP), (LEFT, BOTTOM))]
    s["Y"] = [_line((LEFT, TOP), (MIDX, MIDY)),
              _line((RIGHT, TOP), (MIDX, MIDY)),
              _line((MIDX, MIDY), (MIDX, BOTTOM))]
    s["Z"] = [_poly([(LEFT, TOP), (RIGHT, TOP), (LEFT, BOTTOM), (RIGHT, BOTTOM)])]
    return s


LETTER_STROKES: Dict[str, List[Stroke]] = _build()


def get_strokes(letter: str) -> Optional[List[Stroke]]:
    """Return the stroke list for an uppercase letter, or None if undefined."""
    return LETTER_STROKES.get((letter or "").strip().upper()[:1])


def stroke_count(letter: str) -> int:
    strokes = get_strokes(letter)
    return len(strokes) if strokes else 0
