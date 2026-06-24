#!/usr/bin/env python3
"""Generate ReadingLand's felt / plush-toy art set — fully offline, no API.

Everything the app shows is rendered here from code with Pillow + numpy: a
tintable **plush-pillow** button/panel texture, five **felt-cutout** mascot
portraits, and soft **felt-craft** land backgrounds. Output lands in
``assets/images/`` using the exact names ``readingland/ui/assets.py`` looks for,
so the app picks the art up with **no code changes** (it still falls back to
programmatic placeholders if a file is missing).

The look: stuffed-felt volume (soft interior bulge, darker sewn edges), fuzzy
fibre grain, and cream stitch outlines — like a hand-sewn felt toy.

    python scripts/generate_art.py                 # everything
    python scripts/generate_art.py --only buttons  # buttons | characters | backgrounds

Build-time only: the *app* never imports Pillow; it just loads the PNGs.
"""
from __future__ import annotations

import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "images")

SS = 3  # supersample factor; everything is drawn big then shrunk for smooth edges

INK = (43, 45, 66)        # config PALETTE "ink"
CREAM = (255, 246, 233)   # config PALETTE "cream"
THREAD = (255, 250, 240, 230)  # cream stitch thread


# --------------------------------------------------------------------------- #
# Colour helpers
# --------------------------------------------------------------------------- #
def hex_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, f: float):
    """Lighten (f>1) or darken (f<1) an RGB colour, clamped."""
    return tuple(int(max(0, min(255, ch * f))) for ch in c[:3])


def mix(c1, c2, t: float):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1[:3], c2[:3]))


# --------------------------------------------------------------------------- #
# Felt material
# --------------------------------------------------------------------------- #
def felt_grain(w, h, rng, fine=0.05, soft=0.05):
    """Multiplicative fibre noise around 1.0 — fine speckle + soft mottling."""
    g = rng.normal(1.0, fine, (h, w)).astype(np.float32)
    sh, sw = max(2, h // 14), max(2, w // 14)
    s = rng.normal(1.0, soft, (sh, sw)).astype(np.float32)
    s = np.asarray(
        Image.fromarray(np.clip(s * 128, 0, 255).astype("uint8")).resize((w, h), Image.BILINEAR),
        np.float32,
    ) / 128.0
    return np.clip(g * s, 0.7, 1.3)


def felt_fill(mask, color, rng, light_top=0.18, light_left=0.08, contrast=0.46):
    """Render a felt piece: soft stuffed volume + fibre grain, clipped to mask."""
    bbox = mask.getbbox()
    if bbox is None:
        return Image.new("RGBA", mask.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = bbox
    pad = 6
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(mask.width, x1 + pad), min(mask.height, y1 + pad)
    sub = mask.crop((x0, y0, x1, y1))
    w, h = sub.size
    a = np.asarray(sub, np.float32) / 255.0

    # "thickness" = how far inside the shape — blur of the mask. Fat interior is
    # bright/raised, thin edge is dark — the stuffed-felt pillow look.
    br = max(2.0, 0.11 * min(w, h))
    thick = np.asarray(sub.filter(ImageFilter.GaussianBlur(br)), np.float32) / 255.0
    tmax = float(thick.max()) or 1.0
    tnorm = thick / tmax
    shmap = (1.0 - contrast) + contrast * tnorm

    # gentle directional light from top-left
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    shmap = shmap * (1.0 + light_top * (1.0 - 2.0 * yy / max(1, h - 1))
                     + light_left * (1.0 - 2.0 * xx / max(1, w - 1)))
    shmap *= felt_grain(w, h, rng)
    shmap = np.clip(shmap, 0.40, 1.16)

    col = np.array(color[:3], np.float32)
    rgb = np.clip(col[None, None, :] * shmap[..., None], 0, 255).astype(np.uint8)
    out = np.dstack([rgb, (a * 255).astype(np.uint8)])
    res = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    res.paste(Image.fromarray(out, "RGBA"), (x0, y0))
    return res


def drop_shadow(piece, dx, dy, blur, alpha=90):
    a = piece.split()[3].point(lambda v: min(v, alpha))
    canvas = Image.new("L", piece.size, 0)
    canvas.paste(a, (dx, dy))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new("RGBA", piece.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", piece.size, (25, 18, 38, 255)), (0, 0), canvas)
    return sh


# --------------------------------------------------------------------------- #
# Stitch outlines
# --------------------------------------------------------------------------- #
def inset_points(pts, k):
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    out = []
    for x, y in pts:
        dx, dy = cx - x, cy - y
        L = math.hypot(dx, dy) or 1.0
        out.append((x + dx / L * k, y + dy / L * k))
    return out


def stitch(draw, pts, color=THREAD, dash=15, gap=11, width=5, closed=True):
    dash, gap, width = dash * SS, gap * SS, max(1, width * SS // 2)
    n = len(pts)
    last = n if closed else n - 1
    pen, acc = True, 0.0
    for i in range(last):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg < 1e-6:
            continue
        ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
        d = 0.0
        while d < seg:
            target = (dash if pen else gap) - acc
            adv = min(target, seg - d)
            if pen:
                ax, ay = x0 + ux * d, y0 + uy * d
                bx, by = x0 + ux * (d + adv), y0 + uy * (d + adv)
                draw.line([(ax, ay), (bx, by)], fill=color, width=width)
            d += adv
            acc += adv
            if acc >= (dash if pen else gap) - 1e-6:
                acc = 0.0
                pen = not pen


def out_ellipse(cx, cy, rx, ry, rot=0.0, n=150):
    rot = math.radians(rot)
    ca, sa = math.cos(rot), math.sin(rot)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        ex, ey = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + ex * ca - ey * sa, cy + ex * sa + ey * ca))
    return pts


def out_rrect(x0, y0, x1, y1, r, steps=10):
    pts = []
    for cx, cy, a0, a1 in [(x1 - r, y0 + r, -90, 0), (x1 - r, y1 - r, 0, 90),
                           (x0 + r, y1 - r, 90, 180), (x0 + r, y0 + r, 180, 270)]:
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def curve_pts(points, n=60):
    """Sample a smooth-ish open curve through control points (Catmull-Rom)."""
    pts = []
    P = [points[0]] + list(points) + [points[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            pts.append((x, y))
    pts.append(points[-1])
    return pts


# --------------------------------------------------------------------------- #
# Felt canvas — build a character from stacked felt pieces
# --------------------------------------------------------------------------- #
class FeltCanvas:
    def __init__(self, w, h, seed=0):
        self.w, self.h = w, h
        self.W, self.H = w * SS, h * SS
        self.img = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        self.rng = np.random.default_rng(seed)

    # --- shape builders (working coords) -> (mask, outline in SS coords) --- #
    def ellipse(self, cx, cy, rx, ry, rot=0.0):
        m = Image.new("L", (self.W, self.H), 0)
        if rot:
            tmp = Image.new("L", (self.W, self.H), 0)
            ImageDraw.Draw(tmp).ellipse(
                [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=255)
            m = tmp.rotate(rot, center=(cx * SS, cy * SS), resample=Image.BICUBIC)
        else:
            ImageDraw.Draw(m).ellipse(
                [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=255)
        return m, out_ellipse(cx * SS, cy * SS, rx * SS, ry * SS, rot)

    def rrect(self, x0, y0, x1, y1, r):
        m = Image.new("L", (self.W, self.H), 0)
        ImageDraw.Draw(m).rounded_rectangle(
            [x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r * SS, fill=255)
        return m, out_rrect(x0 * SS, y0 * SS, x1 * SS, y1 * SS, r * SS)

    def poly(self, pts):
        m = Image.new("L", (self.W, self.H), 0)
        sp = [(x * SS, y * SS) for x, y in pts]
        ImageDraw.Draw(m).polygon(sp, fill=255)
        return m, sp

    # --- placement --------------------------------------------------------- #
    def place(self, mask, color, outline=None, shadow=None, do_stitch=True,
              stitch_inset=11, alpha=1.0, **stitch_kw):
        piece = felt_fill(mask, color, self.rng)
        if alpha < 1.0:
            r, g, b, al = piece.split()
            al = al.point(lambda v: int(v * alpha))
            piece = Image.merge("RGBA", (r, g, b, al))
        if shadow:
            self.img.alpha_composite(drop_shadow(piece, *shadow))
        self.img.alpha_composite(piece)
        if do_stitch and outline is not None:
            d = ImageDraw.Draw(self.img, "RGBA")
            stitch(d, inset_points(outline, stitch_inset * SS), **stitch_kw)

    def stroke(self, points, color=THREAD, **kw):
        """Open stitched line through working-coord control points (whiskers, smiles)."""
        sp = [(x * SS, y * SS) for x, y in points]
        stitch(ImageDraw.Draw(self.img, "RGBA"), curve_pts(sp), color=color, closed=False, **kw)

    def eye(self, cx, cy, r, look=(0.12, 0.12)):
        """Embroidered felt eye: white disc + dark pupil + catchlight."""
        m, o = self.ellipse(cx, cy, r, r)
        self.place(m, (255, 255, 255), o, shadow=(0, int(2 * SS), 3 * SS, 60),
                   stitch_inset=4, dash=8, gap=6, width=3)
        pr = r * 0.62
        px, py = cx + r * look[0], cy + r * look[1]
        m, o = self.ellipse(px, py, pr, pr)
        self.place(m, INK, o, do_stitch=False)
        hr = r * 0.22
        m, _ = self.ellipse(px - pr * 0.32, py - pr * 0.36, hr, hr)
        self.place(m, (255, 255, 255), do_stitch=False)

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.img.resize((self.w, self.h), Image.LANCZOS).save(path)
        print(f"  OK  {os.path.relpath(path, ROOT)}")


# --------------------------------------------------------------------------- #
# Mascot recipes  (portrait, transparent, head + shoulders)
# --------------------------------------------------------------------------- #
W, H = 600, 690


def _shoulders(c, color, belly):
    body, o = c.rrect(118, 470, 482, 700, 150)
    c.place(body, color, o, shadow=(0, int(6 * SS), 9 * SS, 80), stitch_inset=16)
    bel, o = c.ellipse(300, 600, 120, 110)
    c.place(bel, belly, o, stitch_inset=10, dash=11, gap=9)


def char_reading_rabbit(path):
    c = FeltCanvas(W, H, seed=11)
    base = hex_rgb("#FF8FB1")
    inner = shade(base, 1.18)
    # ears (behind head)
    for sx in (-1, 1):
        m, o = c.ellipse(300 + sx * 78, 158, 42, 138, rot=-sx * 12)
        c.place(m, base, o, shadow=(int(sx * 3 * SS), int(4 * SS), 7 * SS, 70), stitch_inset=12)
        m, o = c.ellipse(300 + sx * 78, 168, 22, 104, rot=-sx * 12)
        c.place(m, inner, o, do_stitch=False)
    _shoulders(c, base, CREAM)
    # head
    head, o = c.ellipse(300, 320, 186, 172)
    c.place(head, base, o, shadow=(0, int(5 * SS), 9 * SS, 70), stitch_inset=15)
    # cheeks
    for sx in (-1, 1):
        m, _ = c.ellipse(300 + sx * 118, 360, 38, 30)
        c.place(m, shade(base, 0.9), do_stitch=False, alpha=0.55)
    # muzzle
    mz, o = c.ellipse(300, 392, 96, 74)
    c.place(mz, CREAM, o, stitch_inset=9, dash=10, gap=8)
    c.eye(238, 300, 34, look=(0.1, 0.18))
    c.eye(362, 300, 34, look=(-0.1, 0.18))
    # nose + mouth
    nm, o = c.ellipse(300, 372, 22, 16)
    c.place(nm, hex_rgb("#FF6B6B"), o, do_stitch=False)
    c.stroke([(300, 388), (300, 404), (272, 416)], width=4)
    c.stroke([(300, 404), (328, 416)], width=4)
    # whiskers
    for sy in (-1, 1):
        c.stroke([(330, 392 + sy * 10), (392, 386 + sy * 18)], width=3, dash=40, gap=8)
        c.stroke([(270, 392 + sy * 10), (208, 386 + sy * 18)], width=3, dash=40, gap=8)
    c.save(path)


def char_benny_bear(path):
    c = FeltCanvas(W, H, seed=22)
    base = hex_rgb("#FF9F1C")
    for sx in (-1, 1):
        m, o = c.ellipse(300 + sx * 132, 196, 60, 58)
        c.place(m, base, o, shadow=(int(sx * 2 * SS), int(3 * SS), 6 * SS, 70), stitch_inset=11)
        m, _ = c.ellipse(300 + sx * 132, 200, 30, 28)
        c.place(m, shade(base, 1.2), do_stitch=False)
    _shoulders(c, base, mix(base, CREAM, 0.7))
    head, o = c.ellipse(300, 326, 196, 176)
    c.place(head, base, o, shadow=(0, int(5 * SS), 9 * SS, 70), stitch_inset=15)
    mz, o = c.ellipse(300, 388, 116, 92)
    c.place(mz, mix(base, CREAM, 0.7), o, stitch_inset=10, dash=11, gap=9)
    c.eye(244, 300, 26, look=(0.12, 0.12))
    c.eye(356, 300, 26, look=(-0.12, 0.12))
    nm, o = c.ellipse(300, 366, 30, 22)
    c.place(nm, INK, o, do_stitch=False)
    c.stroke([(300, 388), (300, 408)], width=4)
    c.stroke([(300, 408), (270, 420)], width=4)
    c.stroke([(300, 408), (330, 420)], width=4)
    c.save(path)


def char_penny_penguin(path):
    c = FeltCanvas(W, H, seed=33)
    base = hex_rgb("#2E9BD6")
    # wings
    for sx in (-1, 1):
        m, o = c.ellipse(300 + sx * 196, 520, 52, 150, rot=-sx * 16)
        c.place(m, shade(base, 0.92), o, shadow=(int(sx * 3 * SS), int(4 * SS), 7 * SS, 70),
                stitch_inset=13)
    body, o = c.rrect(118, 430, 482, 700, 160)
    c.place(body, base, o, shadow=(0, int(6 * SS), 9 * SS, 80), stitch_inset=16)
    head, o = c.ellipse(300, 300, 188, 178)
    c.place(head, base, o, shadow=(0, int(5 * SS), 9 * SS, 70), stitch_inset=15)
    # white face + belly panel
    face, o = c.ellipse(300, 330, 150, 158)
    c.place(face, (255, 255, 255), o, stitch_inset=12, dash=12, gap=10)
    belly, o = c.ellipse(300, 590, 132, 118)
    c.place(belly, (255, 255, 255), o, stitch_inset=12, dash=12, gap=10)
    c.eye(242, 286, 32, look=(0.12, 0.1))
    c.eye(358, 286, 32, look=(-0.12, 0.1))
    # beak (diamond)
    beak, o = c.poly([(300, 330), (344, 360), (300, 392), (256, 360)])
    c.place(beak, hex_rgb("#FF9F1C"), o, stitch_inset=7, dash=9, gap=7)
    c.stroke([(268, 360), (332, 360)], width=3, dash=30, gap=6)
    c.save(path)


def char_ollie_owl(path):
    c = FeltCanvas(W, H, seed=44)
    base = hex_rgb("#9B5DE5")
    belly = mix(base, CREAM, 0.55)
    # ear tufts
    for sx in (-1, 1):
        m, o = c.poly([(300 + sx * 150, 150), (300 + sx * 92, 218), (300 + sx * 196, 240)])
        c.place(m, base, o, shadow=(int(sx * 2 * SS), int(3 * SS), 6 * SS, 60), stitch_inset=9)
    # wings
    for sx in (-1, 1):
        m, o = c.ellipse(300 + sx * 196, 470, 60, 168, rot=-sx * 12)
        c.place(m, shade(base, 0.9), o, shadow=(int(sx * 3 * SS), int(4 * SS), 7 * SS, 70),
                stitch_inset=13)
    body, o = c.rrect(120, 360, 480, 700, 165)
    c.place(body, base, o, shadow=(0, int(6 * SS), 9 * SS, 80), stitch_inset=16)
    bel, o = c.ellipse(300, 520, 138, 165)
    c.place(bel, belly, o, stitch_inset=12, dash=12, gap=10)
    head, o = c.ellipse(300, 286, 205, 180)
    c.place(head, base, o, shadow=(0, int(5 * SS), 9 * SS, 70), stitch_inset=15)
    # big owl eye discs
    for sx in (-1, 1):
        m, o = c.ellipse(300 + sx * 86, 280, 86, 86)
        c.place(m, belly, o, stitch_inset=8, dash=10, gap=8)
    c.eye(214, 282, 52, look=(0.1, 0.06))
    c.eye(386, 282, 52, look=(-0.1, 0.06))
    # beak
    beak, o = c.poly([(300, 322), (330, 350), (300, 384), (270, 350)])
    c.place(beak, hex_rgb("#FF9F1C"), o, stitch_inset=6, dash=8, gap=6)
    c.save(path)


def char_milo_monkey(path):
    c = FeltCanvas(W, H, seed=55)
    base = hex_rgb("#3DDC97")
    face = mix(base, CREAM, 0.72)
    for sx in (-1, 1):
        m, o = c.ellipse(300 + sx * 168, 322, 58, 58)
        c.place(m, base, o, shadow=(int(sx * 2 * SS), int(3 * SS), 6 * SS, 70), stitch_inset=11)
        m, _ = c.ellipse(300 + sx * 168, 326, 30, 30)
        c.place(m, face, do_stitch=False)
    _shoulders(c, base, face)
    head, o = c.ellipse(300, 320, 188, 174)
    c.place(head, base, o, shadow=(0, int(5 * SS), 9 * SS, 70), stitch_inset=15)
    # monkey face patch (rounded heart-ish)
    patch, o = c.ellipse(300, 372, 132, 128)
    c.place(patch, face, o, stitch_inset=11, dash=12, gap=10)
    c.eye(248, 318, 33, look=(0.1, 0.12))
    c.eye(352, 318, 33, look=(-0.1, 0.12))
    for sx in (-1, 1):
        m, _ = c.ellipse(300 + sx * 20, 388, 9, 7)
        c.place(m, shade(base, 0.7), do_stitch=False)
    c.stroke([(300, 398), (300, 412)], width=4)
    c.stroke([(266, 420), (300, 432), (334, 420)], width=4)
    c.save(path)


CHARACTERS = {
    "reading_rabbit": char_reading_rabbit,
    "benny_bear": char_benny_bear,
    "penny_penguin": char_penny_penguin,
    "ollie_owl": char_ollie_owl,
    "milo_monkey": char_milo_monkey,
}


# --------------------------------------------------------------------------- #
# Tintable plush button / panel textures (neutral; the app multiplies by colour)
# --------------------------------------------------------------------------- #
def make_panel(path, size, seed, bulge=0.0, rim=0.20, dip=0.34, grain=0.04, round_bias=0.5):
    """Neutral felt shade map (values <=1.0) so Kivy's tint reads as plush felt."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = xx / (w - 1) * 2 - 1
    ny = yy / (h - 1) * 2 - 1
    r_sq = np.maximum(np.abs(nx), np.abs(ny))           # rounded-rect distance
    r_rad = np.clip(np.sqrt(nx ** 2 + ny ** 2), 0, 1)   # radial distance
    rr = round_bias * r_sq + (1 - round_bias) * r_rad
    shmap = 1.0 - dip * rr                               # bright centre, soft falloff
    edge = np.clip((rr - 0.80) / 0.20, 0, 1)
    shmap -= rim * edge                                 # darker sewn seam at the rim
    shmap += 0.05 * (-ny)                               # faint top light
    rng = np.random.default_rng(seed)
    shmap *= felt_grain(w, h, rng, fine=grain, soft=grain * 0.8)
    shmap = np.clip(shmap, 0.5, 1.0)
    val = (shmap * 255).astype(np.uint8)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(np.dstack([val, val, val]), "RGB").save(path)
    print(f"  OK  {os.path.relpath(path, ROOT)}")


# --------------------------------------------------------------------------- #
# Felt-craft land backgrounds (soft & pale so UI stays readable)
# --------------------------------------------------------------------------- #
def make_background(path, accent, seed):
    w, h = 1280, 900
    rng = np.random.default_rng(seed)
    top = np.array(mix(accent, (255, 255, 255), 0.62), np.float32)
    bot = np.array(mix(accent, (255, 255, 255), 0.30), np.float32)
    ty = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    grad = top[None, None, :] * (1 - ty) + bot[None, None, :] * ty
    grain = felt_grain(w, h, rng, fine=0.03, soft=0.05)[..., None]
    arr = np.clip(grad * grain, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGB").convert("RGBA")

    big = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)

    def felt_blob(cx, cy, rx, ry, col, a=255):
        layer = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col + (a,))
        big.alpha_composite(layer)

    # rolling felt hills
    hill = mix(accent, (255, 255, 255), 0.42)
    felt_blob(w, int(h * 2.05), int(w * 1.25), int(h * 0.72), hill, 235)
    hill2 = mix(accent, (90, 200, 130), 0.5)
    felt_blob(int(w * 0.4), int(h * 2.12), int(w * 0.8), int(h * 0.5), hill2, 220)
    # soft cream felt clouds
    for _ in range(5):
        cx = int(rng.uniform(0.1, 0.9) * w * 2)
        cy = int(rng.uniform(0.08, 0.4) * h * 2)
        rx = int(rng.uniform(0.10, 0.18) * w * 2)
        for ox in (-rx, 0, rx, int(rx * 0.5)):
            felt_blob(cx + ox, cy, int(rx * 0.7), int(rx * 0.5), (255, 252, 245), 210)
    # a warm felt sun
    felt_blob(int(w * 1.7), int(h * 0.5), 150, 150, hex_rgb("#FFD23F"), 220)

    big = big.filter(ImageFilter.GaussianBlur(3)).resize((w, h), Image.LANCZOS)
    img.alpha_composite(big)
    # subtle stitched horizon
    sd = ImageDraw.Draw(img, "RGBA")
    stitch(sd, [(0, int(h * 0.66)), (w, int(h * 0.66))],
           color=(255, 255, 255, 120), dash=10, gap=8, width=2, closed=False)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = img.convert("RGB")               # backgrounds never need alpha
    if path.lower().endswith((".jpg", ".jpeg")):
        img.save(path, quality=86, optimize=True)   # ~150 KB vs ~1.2 MB as PNG
    else:
        img.save(path)
    print(f"  OK  {os.path.relpath(path, ROOT)}")


STAGE_BG = {
    "visual": "#3DDC97", "alphabet": "#FF9F1C", "phonics": "#9B5DE5",
    "words": "#FF6B6B", "sentences": "#2E9BD6", "stories": "#FF8FB1",
}


# --------------------------------------------------------------------------- #
# Story-page scenes — soft felt settings; the page's emoji subject sits on top
# --------------------------------------------------------------------------- #
def make_story_scene(path, scene):
    W, H, S = 1000, 420, 2
    rng = np.random.default_rng(abs(hash(scene)) % 9999)
    night = scene == "moon"
    indoor = scene in ("rug", "mat", "nap", "hug")
    sunrise = scene == "sunrise"

    if night:
        top, bot = hex_rgb("#3C3F72"), hex_rgb("#605FA6")
    elif sunrise:
        top, bot = hex_rgb("#FFB877"), hex_rgb("#FFE7B6")
    elif indoor:
        top, bot = hex_rgb("#FBE3C2"), hex_rgb("#F6D3A6")
    else:
        top, bot = hex_rgb("#97D7F4"), hex_rgb("#D7F2FC")
    ty = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    grad = np.array(top, np.float32) * (1 - ty) + np.array(bot, np.float32) * ty
    base = Image.fromarray(np.clip(grad, 0, 255).astype("uint8"), "RGB").convert("RGBA")

    big = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))

    def blob(cx, cy, rx, ry, col, a=255):
        layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                                      fill=tuple(int(c) for c in col) + (a,))
        big.alpha_composite(layer)

    def band(x0, y0, x1, y1, r, col, a=255):
        layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
        ImageDraw.Draw(layer).rounded_rectangle([x0, y0, x1, y1], radius=r,
                                                fill=tuple(int(c) for c in col) + (a,))
        big.alpha_composite(layer)

    # ground
    if indoor:
        # a window on the wall (night view for the nap page), the floor, and a rug
        # whose colour differs per page so the four indoor pages read distinctly.
        band(int(W * 0.59) * S, int(H * 0.11) * S, int(W * 0.89) * S, int(H * 0.43) * S,
             16 * S, mix((255, 255, 255), (0, 0, 0), 0.12))
        win = hex_rgb("#34386A") if scene == "nap" else mix(hex_rgb("#9BD9F4"), (255, 255, 255), 0.2)
        band(int(W * 0.605) * S, int(H * 0.125) * S, int(W * 0.875) * S, int(H * 0.415) * S, 11 * S, win)
        if scene == "nap":
            blob(int(W * 0.8) * S, int(H * 0.22) * S, 17 * S, 17 * S, (255, 250, 225), 240)
        band(-40, int(H * 0.6) * S, (W + 40) * S, (H + 40) * S, 0, hex_rgb("#E7B585"))
        rug_hex = {"rug": "#FF6B6B", "mat": "#3DDC97", "nap": "#9B5DE5",
                   "hug": "#FF8FB1"}.get(scene, "#FF6B6B")
        rug = mix(hex_rgb(rug_hex), (255, 255, 255), 0.12)
        band(int(W * 0.16) * S, int(H * 0.66) * S, int(W * 0.84) * S, int(H * 0.96) * S, 46 * S, rug)
        for k in range(4):
            yy = int((0.71 + k * 0.06) * H) * S
            ImageDraw.Draw(big).line([(int(W * 0.19) * S, yy), (int(W * 0.81) * S, yy)],
                                     fill=mix(rug, (255, 255, 255), 0.45) + (255,), width=6 * S)
        if scene == "hug":
            for hx, hy, hr in [(0.28, 0.32, 24), (0.42, 0.2, 18), (0.18, 0.46, 16)]:
                blob(int(W * hx) * S, int(H * hy) * S, hr * S, hr * S, hex_rgb("#FF6B6B"), 215)
    elif not night:
        grass = mix(hex_rgb("#7AC74F"), (255, 255, 255), 0.14)
        blob(int(W * 0.5) * S, int(H * 1.52) * S, int(W * 0.95) * S, int(H * 0.82) * S, grass)

    # sky props
    if night:
        for _ in range(16):
            x = int(rng.uniform(0.05, 0.95) * W) * S
            y = int(rng.uniform(0.05, 0.55) * H) * S
            r = int(rng.uniform(3, 7)) * S
            blob(x, y, r, r, (255, 250, 230), 235)
    else:
        if scene not in ("sky",):
            sx, sy = int(W * 0.84) * S, int(H * 0.22) * S
            blob(sx, sy, 96 * S, 96 * S, hex_rgb("#FFD23F"), 75)
            blob(sx, sy, 70 * S, 70 * S, hex_rgb("#FFD23F"), 240)
        for _ in range(0 if indoor else 3):
            cx = int(rng.uniform(0.08, 0.7) * W) * S
            cy = int(rng.uniform(0.08, 0.34) * H) * S
            r = int(rng.uniform(52, 82)) * S
            for ox in (-r, 0, r, r // 2):
                blob(cx + ox, cy, int(r * 0.72), int(r * 0.5), (255, 252, 246), 230)

    if scene == "tree":
        tx = int(W * 0.28) * S
        band(tx - 20 * S, int(H * 0.42) * S, tx + 20 * S, int(H * 0.82) * S, 12 * S, hex_rgb("#A6713E"))
        blob(tx, int(H * 0.36) * S, 150 * S, 128 * S, hex_rgb("#5DBB63"))
    if scene == "meadow":
        palette = [hex_rgb(c) for c in ("#FF6B6B", "#FFD23F", "#FF8FB1", "#9B5DE5", "#5DC1F0")]
        for _ in range(11):
            x = int(rng.uniform(0.08, 0.92) * W) * S
            y = int(rng.uniform(0.72, 0.92) * H) * S
            blob(x, y, 13 * S, 13 * S, palette[int(rng.integers(len(palette)))])
        rdraw = ImageDraw.Draw(big)
        cx, cy = int(W * 0.5) * S, int(H * 0.95) * S
        for i, c in enumerate(palette[:5]):
            rr = int((0.46 - i * 0.05) * W) * S
            rdraw.arc([cx - rr, cy - rr, cx + rr, cy + rr], 180, 360,
                      fill=tuple(int(v) for v in c) + (170,), width=12 * S)

    big = big.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.LANCZOS)
    base.alpha_composite(big)

    arr = np.asarray(base.convert("RGB"), np.float32)
    g = felt_grain(W, H, rng, fine=0.03, soft=0.04)[..., None]
    if scene == "nap":
        arr = arr * 0.88                       # cozy, dimmed nap-time light
    out = Image.fromarray(np.clip(arr * g, 0, 255).astype("uint8"), "RGB")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # The cream RoundedCard frames the scene, so a flat JPEG (no alpha) is plenty
    # and keeps each page light (~100 KB vs ~900 KB as RGBA PNG).
    if path.lower().endswith((".jpg", ".jpeg")):
        out.save(path, quality=86, optimize=True)
    else:
        out.save(path)
    print(f"  OK  {os.path.relpath(path, ROOT)}")


# --------------------------------------------------------------------------- #
# App launcher icon — the felt rabbit on a stitched felt tile
# --------------------------------------------------------------------------- #
def make_app_icon(path, size=512):
    rabbit = os.path.join(IMG, "characters", "reading_rabbit", "portrait.png")
    if not os.path.exists(rabbit):
        char_reading_rabbit(rabbit)
    c = FeltCanvas(size, size, seed=3)
    m, o = c.rrect(28, 28, size - 28, size - 28, 108)
    c.place(m, hex_rgb("#5DC1F0"), o, shadow=(0, int(7 * SS), 11 * SS, 80),
            stitch_inset=20, dash=17, gap=12)
    icon = c.img.resize((size, size), Image.LANCZOS)
    head = Image.open(rabbit).convert("RGBA").crop((36, 24, 564, 470))  # head + ears
    scale = size * 0.82 / head.width
    head = head.resize((int(head.width * scale), int(head.height * scale)), Image.LANCZOS)
    icon.alpha_composite(head, ((size - head.width) // 2, int(size * 0.12)))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    icon.save(path)
    print(f"  OK  {os.path.relpath(path, ROOT)}")


# --------------------------------------------------------------------------- #
def gen_buttons():
    print("Plush button / panel textures + app icon:")
    make_panel(os.path.join(IMG, "ui", "felt_button.png"), (640, 320), seed=7,
               rim=0.20, dip=0.30, round_bias=0.62)
    make_panel(os.path.join(IMG, "ui", "felt_panel.png"), (512, 512), seed=8,
               rim=0.17, dip=0.26, round_bias=0.5)
    make_app_icon(os.path.join(IMG, "ui", "app_icon.png"))


def gen_characters():
    print("Felt mascot portraits:")
    for cid, fn in CHARACTERS.items():
        fn(os.path.join(IMG, "characters", cid, "portrait.png"))


def gen_backgrounds():
    print("Felt-craft land backgrounds:")
    for key, accent in STAGE_BG.items():
        make_background(os.path.join(IMG, "backgrounds", f"bg_{key}.jpg"), hex_rgb(accent), seed=hash(key) % 1000)
    make_background(os.path.join(IMG, "backgrounds", "bg_map.jpg"), hex_rgb("#5DC1F0"), seed=99)


def gen_stories():
    import json
    print("Felt story-page scenes:")
    with open(os.path.join(ROOT, "readingland", "content", "stories.json")) as fh:
        data = json.load(fh)
    for book in data.get("items", []):
        for i, page in enumerate(book.get("pages", [])):
            make_story_scene(os.path.join(IMG, "cards", f"{book['id']}_p{i}.jpg"),
                             page.get("scene", "day"))


def main():
    ap = argparse.ArgumentParser(description="Generate ReadingLand felt/plush art (offline).")
    ap.add_argument("--only", choices=["buttons", "characters", "backgrounds", "stories"],
                    help="generate just one group (default: all)")
    args = ap.parse_args()
    groups = [args.only] if args.only else ["buttons", "characters", "backgrounds", "stories"]
    table = {"buttons": gen_buttons, "characters": gen_characters,
             "backgrounds": gen_backgrounds, "stories": gen_stories}
    for g in groups:
        table[g]()
    print("\nDone. The app loads these automatically (assets/images/...).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
