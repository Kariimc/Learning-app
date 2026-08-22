"""The sky world: a shader sky, drifting wool, and anything perched on it.

Kariim's direction, 2026-08-22: the app is one place, seen at golden hour, and
everything that needs to sit somewhere sits on a cloud made of felted wool.

Two rules came out of getting this wrong first:

1. NO FLAT SHAPES. The old background drew coloured rectangles and four ellipses
   and called them clouds. He rejected that method outright: "lazy... I would
   never use that method if I was doing it myself." The sky is a fragment shader
   on the graphics card, and the clouds are photographs of wool grown and lit in
   Blender (``assets/images/sky/wool_*.png``).

2. WOOL IS THE SURFACE. Anything that needs a place to be gets its own cloud.
   That is what replaced floating panels: a figure on the grown-up screen, a
   child's name on the picker, a land on the map. Nothing floats in empty space
   and no flat card is ever needed.

The wool files were rendered by ``tools/wool_clouds.py``. Re-render them there
rather than painting new ones by hand; four attempts at painting wool in 2D were
thrown away before Blender was used.
"""
from __future__ import annotations

import math
import os
import random

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RenderContext
from kivy.uix.image import Image as KImage
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget

from .. import config

SKY_DIR = os.path.join(config.ASSETS_DIR, "images", "sky")

# Warmth of the light. 0 is daytime, 1 is golden hour. Kariim picked golden.
WARM = 0.6

SKY_FS = """
$HEADER$
uniform vec2 resolution;
uniform float t;
uniform float warm;
void main(void) {
    // Clamped: before the window has laid out, resolution is stale, uv runs
    // past 1, the colour mix extrapolates, and the whole sky comes out
    // saturated blue with everything missing.
    vec2 uv = clamp(gl_FragCoord.xy / max(resolution, vec2(1.0)), 0.0, 1.0);
    vec3 hi = mix(vec3(0.15,0.52,0.86), vec3(0.26,0.50,0.86), warm);
    vec3 mid= mix(vec3(0.47,0.78,0.96), vec3(0.99,0.82,0.56), warm);
    vec3 lo = mix(vec3(0.86,0.95,1.00), vec3(1.00,0.90,0.66), warm);
    // y counts DOWN the screen here. Every stop was upside down until this.
    float y = 1.0 - uv.y;
    // the warm band is held high so gold never meets blue in the middle of the
    // screen, which turned the whole thing mauve
    float k = mix(0.55, 0.78, warm);
    vec3 col = y < k ? mix(lo, mid, y/k) : mix(mid, hi, (y-k)/(1.0-k));
    vec2 sun = vec2(0.76,0.84);
    float ar = resolution.x/resolution.y;
    float d = distance(vec2(uv.x*ar,uv.y), vec2(sun.x*ar,sun.y));
    col += vec3(1.0,0.92,0.70)*(0.30/(1.0+45.0*d*d));
    col = mix(col, vec3(1.0,0.98,0.93), smoothstep(0.26,0.0,1.0-uv.y)*0.40);
    gl_FragColor = vec4(col,1.0);
}
"""


def wool_path(n: int = 1) -> str:
    """Path to one of the rendered wool clouds, or "" if it has not been
    fetched yet. The files live in Git LFS, so a fresh clone that has not run
    ``git lfs pull`` holds pointer stubs, not pictures."""
    p = os.path.join(SKY_DIR, "wool_%d.png" % n)
    return p if os.path.exists(p) and os.path.getsize(p) > 2048 else ""


class ShaderSky(Widget):
    """The sky itself. Never static: the light drifts across the whole frame."""

    def __init__(self, warm: float = WARM, **kw):
        self.canvas = RenderContext(use_parent_projection=True)
        self.canvas.shader.fs = SKY_FS
        super().__init__(**kw)
        with self.canvas:
            Color(1, 1, 1, 1)
            self._rect = Rectangle()
        self._t = 0.0
        self._warm = warm
        self.bind(pos=self._sync, size=self._sync)
        self._ev = Clock.schedule_interval(self._tick, 1 / 60.0)

    def _sync(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _tick(self, dt):
        self._t += dt
        self.canvas["t"] = self._t
        self.canvas["warm"] = self._warm
        self.canvas["resolution"] = [float(max(1, self.width)),
                                     float(max(1, self.height))]
        self.canvas.ask_update()

    def stop(self):
        if getattr(self, "_ev", None):
            self._ev.cancel()
            self._ev = None


class WoolCloud(KImage):
    """One cloud drifting past. Depth comes from speed, not from a blur."""

    def __init__(self, speed: float, yfrac: float, width_px: float, which: int = 1, **kw):
        super().__init__(source=wool_path(which), allow_stretch=True,
                         keep_ratio=True, size_hint=(None, None), **kw)
        self.speed = speed
        self.yfrac = yfrac
        self.wpx = width_px
        self._x = None

    def step(self, dt, W, H):
        if not self.texture:
            return
        h = self.wpx * self.texture.height / self.texture.width
        self.size = (self.wpx, h)
        if self._x is None:
            self._x = random.uniform(-self.wpx, W)
        self._x += self.speed * dt
        if self._x > W:
            self._x = -self.wpx - 40      # start fully offscreen or it clips in
        self.pos = (self._x, H * self.yfrac)


def land_art(key: str) -> str:
    """The cut-out plush land for a stage key, or "" if it is not fetched."""
    p = os.path.join(config.ASSETS_DIR, "images", "lands", "land_%s.png" % key)
    return p if os.path.exists(p) and os.path.getsize(p) > 2048 else ""


class Perched(ButtonBehavior, Widget):
    """Something standing on its own wool, with its name underneath.

    Use this for a land on the map, a child on the picker, a character anywhere.
    Pass ``art`` as an image path, or leave it None to perch text alone.
    The whole thing, wool and all, is the tap target.
    """

    def __init__(self, art=None, cxf=0.5, cyf=0.5, wpx=200, label="",
                 phase=0.0, which=1, label_color=None, on_tap=None, dim=False, **kw):
        super().__init__(size_hint=(None, None), **kw)
        self._on_tap = on_tap
        self._dim = dim
        from ..ui import theme  # local import keeps this module import-light
        self.wool = KImage(source=wool_path(which), allow_stretch=True,
                           keep_ratio=True, size_hint=(None, None))
        self.add_widget(self.wool)
        self.img = None
        if art:
            self.img = KImage(source=str(art), allow_stretch=True,
                              keep_ratio=True, size_hint=(None, None))
            self.add_widget(self.img)
        self.lbl = Label(text=label, bold=True, font_size=theme.FONT_HEADING,
                         color=label_color or config.PALETTE["ink"],
                         size_hint=(None, None), halign="center", valign="middle")
        self.add_widget(self.lbl)
        self.cxf, self.cyf, self.wpx, self.phase = cxf, cyf, wpx, phase
        if dim:
            for w in (self.wool, self.lbl):
                w.opacity = 0.55
            if self.img is not None:
                self.img.opacity = 0.42

    def on_release(self):
        if self._on_tap:
            self._on_tap(self)

    def step(self, t, W, H):
        if not self.wool.texture:
            return
        bob = math.sin(t * 0.7 + self.phase) * H * 0.008
        sway = math.cos(t * 0.33 + self.phase) * W * 0.004
        cx = W * self.cxf + sway
        cy = H * self.cyf + bob
        h = self.wpx
        if self.img is not None and self.img.texture:
            h = self.wpx * self.img.texture.height / self.img.texture.width
            self.img.size = (self.wpx, h)
            self.img.pos = (cx - self.wpx / 2, cy - h / 2)
        ww = self.wpx * 2.05
        wh = ww * self.wool.texture.height / self.wool.texture.width
        self.wool.size = (ww, wh)
        self.wool.center = (cx, cy - h * 0.42)
        self.lbl.size = (ww, 44)
        self.lbl.text_size = (ww, None)
        if self.img is not None:
            # measured off the wool, not off the picture: a tall portrait sinks
            # its cloud lower, and a fixed drop let the name touch the wool
            # the wool PNG carries transparent padding under the puff, so the
            # name sits just inside the box rather than a fixed drop below it
            self.lbl.center = (cx, self.wool.y + 10)
        else:
            # nothing standing on it, so the name stands on the wool itself
            # rather than floating under a bare cloud
            self.lbl.center = (cx, cy - h * 0.42 + wh * 0.04)
        # the tap target is the whole thing: art, wool and name together
        self.size = (ww, h + wh)
        self.center = (cx, cy - h * 0.18)


class Standing(ButtonBehavior, Widget):
    """Something standing on its own wool, inside a box a layout gives it.

    ``Perched`` floats free in the sky and bobs; ``Standing`` takes its place
    from a parent layout, so it can go in a scrolling column or a grid and
    still obey the one rule: wool is the surface, and nothing sits on a flat
    panel. Pass ``art`` for a picture standing on the cloud, or leave it out
    and ``label`` sits on the wool itself. That is how a number gets a place
    to be without a card being drawn behind it.
    """

    def __init__(self, art=None, label="", caption="", which=1, dim=False,
                 on_tap=None, label_color=None, caption_color=None,
                 label_size=None, **kw):
        super().__init__(**kw)
        from ..ui import theme
        self._on_tap = on_tap
        self.wool = KImage(source=wool_path(which), allow_stretch=True,
                           keep_ratio=True, size_hint=(None, None))
        self.add_widget(self.wool)
        self.img = None
        if art:
            self.img = KImage(source=str(art), allow_stretch=True,
                              keep_ratio=True, size_hint=(None, None))
            self.add_widget(self.img)
        ink = config.PALETTE["ink"]
        self.lbl = Label(text=label, bold=True,
                         font_size=label_size or theme.FONT_BODY,
                         color=label_color or ink, size_hint=(None, None),
                         halign="center", valign="middle")
        self.add_widget(self.lbl)
        self.cap = Label(text=caption, font_size=theme.FONT_LABEL,
                         color=caption_color or ink, size_hint=(None, None),
                         halign="center", valign="middle")
        self.add_widget(self.cap)
        if dim:
            self.wool.opacity = 0.55
            self.lbl.opacity = 0.70
            if self.img is not None:
                self.img.opacity = 0.42
        # Laid out on the frame AFTER the change, never during it. Binding
        # straight to pos ran this while the grid was still moving the box, so
        # every cloud kept the position it had mid-layout and the whole row sat
        # half a column to the left of its own labels.
        self._relay = Clock.create_trigger(self._lay, -1)
        self.bind(pos=self._relay, size=self._relay)
        self.wool.bind(texture=self._relay)
        if self.img is not None:
            self.img.bind(texture=self._relay)
        self._relay()

    def on_release(self):
        if self._on_tap:
            self._on_tap(self)

    def _lay(self, *_):
        if not self.wool.texture:
            return
        w, h = self.size
        cx = self.center_x
        has_cap = bool(self.cap.text)
        has_art = self.img is not None and self.img.texture
        # The box is read from the bottom up: caption, then name, then the
        # wool, then whatever stands on it. Getting this order wrong once put
        # the name underneath its own figures.
        # one cloud height for both kinds, so a row of them lines up whether or
        # not each box happens to have a picture standing on it
        ww = w * 0.72
        wh = ww * self.wool.texture.height / self.wool.texture.width
        wool_cy = self.y + h * (0.48 if has_art else 0.50)
        self.wool.size = (ww, wh)
        self.wool.center = (cx, wool_cy)
        if has_art:
            ah = h * 0.46
            aw = ah * self.img.texture.width / self.img.texture.height
            if aw > w * 0.72:                     # keep it inside its own box
                aw = w * 0.72
                ah = aw * self.img.texture.height / self.img.texture.width
            self.img.size = (aw, ah)
            self.img.center = (cx, wool_cy + ah * 0.40)
            self.lbl.size = (w, h * 0.14)
            self.lbl.text_size = self.lbl.size
            self.lbl.center = (cx, self.y + h * (0.20 if has_cap else 0.10))
        else:
            # no picture: the words stand on the wool instead
            self.lbl.size = (ww * 0.92, wh * 0.72)
            self.lbl.text_size = self.lbl.size
            self.lbl.center = (cx, wool_cy + wh * 0.05)
        if has_cap:
            self.cap.size = (w, h * 0.13)
            self.cap.text_size = self.cap.size
            self.cap.center = (cx, self.y + h * 0.07)
