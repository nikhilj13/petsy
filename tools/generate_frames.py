#!/usr/bin/env python3
"""Petsy sprite generator — deterministic, stdlib-only (Pillow only used by preview).

Two skins: "cat" (orange tabby) and "claws" (classic space invader).
Writes src/avatar/frames.ts: palette-indexed frames (OUT_W x OUT_H), 8 per state.
"""
import math
import random

W, H = 24, 30          # native design resolution
NF = 8  # frames per state

# Output scale: rasterize directly at OUT_W x OUT_H so the terminal
# footprint stays compact (18 cols x 11 rows via half-blocks).
OUT_SCALE = 0.75
OUT_W = int(W * OUT_SCALE)   # 18
OUT_H = int(H * OUT_SCALE)   # 22


class Canvas:
    """Design-space canvas (24x30) rasterized directly to OUT_W x OUT_H."""

    def __init__(self):
        self.px = [["."] * OUT_W for _ in range(OUT_H)]

    def put(self, x, y, ch):
        X = int(round(x * OUT_W / W))
        Y = int(round(y * OUT_H / H))
        if 0 <= X < OUT_W and 0 <= Y < OUT_H:
            self.px[Y][X] = ch

    def get(self, x, y):
        X = int(round(x * OUT_W / W))
        Y = int(round(y * OUT_H / H))
        if 0 <= X < OUT_W and 0 <= Y < OUT_H:
            return self.px[Y][X]
        return "."

    def put_px(self, X, Y, ch):
        """Write directly in output pixel coordinates."""
        if 0 <= X < OUT_W and 0 <= Y < OUT_H:
            self.px[Y][X] = ch

    def rows(self):
        return ["".join(r) for r in self.px]


# ---------------------------------------------------------------- palette ---
# Two skins: "cat" (orange tabby) and "claws" (classic space invader).
# Shared prop colors + per-skin body colors.

SHARED = {
    ".": None,
    "w": "#FFFFFF",  # white gloss / thought cloud
    "y": "#FFD98A",  # star / bulb / pencil
    "Y": "#E8A94E",  # yellow shade
    "L": "#FFF3C4",  # bulb glow
    "c": "#BFE3FF",  # glass tint / sweat
    "C": "#8FC4EE",  # glass rim shade
    "r": "#E06C75",  # error red / book cover
    "R": "#B34A55",  # red shade
    "n": "#FFF6E3",  # paper
    "N": "#D8C9A8",  # paper shade
    "k": "#55506B",  # dark handle / ink
    "a": "#7EE2A8",  # mint confetti
    "h": "#FFE9C8",  # sparkle warm
}

SKIN_PALETTES = {
    "cat": {
        "o": "#2A1808",  # outline (dark brown-near-black)
        "1": "#F8E0B0",  # cream highlight (muzzle/chest/paws)
        "2": "#F2B85C",  # fur light
        "3": "#E89B3C",  # fur base (orange tabby)
        "4": "#D07F28",  # fur shade
        "5": "#C46A1E",  # tabby stripes / deep shade
        "6": "#A8551A",  # fur deepest
        "e": "#14100C",  # eye (near-black)
        "g": "#8A7A66",  # soft shade detail
        "s": "#E890A0",  # pink: nose / inner ears / blush
    },
    "claws": {
        "o": "#3A1410",  # outline
        "1": "#FFC9B0",  # highlight
        "2": "#F08A6E",  # light
        "3": "#EF5D48",  # body (extracted from reference)
        "4": "#C84E36",  # shade
        "5": "#A83E2A",  # deep shade
        "6": "#8A3220",  # deepest
        "e": "#1A0E0C",  # eye
        "g": "#8A7A66",  # soft shade detail
        "s": "#E890A0",  # pink accent
    },
}

SKINS = ("cat", "claws")
ACTIVE_SKIN = "cat"


def palette():
    pal = dict(SHARED)
    pal.update(SKIN_PALETTES[ACTIVE_SKIN])
    return pal


# (PALETTE kept for the legacy single-map consumers)
PALETTE = palette()

STATES = ["idle", "thinking", "idea", "writing", "researching",
          "reading", "complete", "confused", "error"]

# ----------------------------------------------------------------- body -----
# Character layers per skin. Cat = rounded tabby drawn with primitives;
# claws = classic space-invader stamped from bitmaps.

def shade_char(dx, dy, rx, ry):
    """Interior shading: light from top-left."""
    lx, ly = dx / rx, dy / ry
    l = lx * -0.62 + ly * -0.70
    d = math.sqrt(lx * lx + ly * ly)
    v = 0.5 + 0.55 * l - 0.35 * d
    if v > 0.82:
        return "1"
    if v > 0.62:
        return "2"
    if v > 0.40:
        return "3"
    if v > 0.16:
        return "4"
    if v > -0.10:
        return "5"
    return "6"


def _blob(c, cx, cy, rx, ry, flare=0.0):
    """Filled ellipse with outline; flare widens the lower half (haunches)."""
    for y in range(int(cy - ry) - 2, int(cy + ry) + 3):
        for x in range(int(cx - rx) - 3, int(cx + rx) + 3):
            rxx = rx * (1.0 + flare * max(0.0, (y - cy) / ry))
            dd = ((x - cx) / rxx) ** 2 + ((y - cy) / ry) ** 2
            if dd <= 1.0:
                c.put(x, y, shade_char(x - cx, y - cy, rxx, ry))
            elif dd <= 1.35 and c.get(x, y) == ".":
                c.put(x, y, "o")


def _tri(c, apex_x, apex_y, half_base, height):
    """Pointed ear triangle with outline, apex up."""
    for i in range(height + 1):
        y = apex_y + i
        hw = max(0, int(round(half_base * i / max(1, height))))
        for x in range(apex_x - hw, apex_x + hw + 1):
            edge = abs(x - apex_x) >= hw or i == height
            c.put(x, y, "o" if edge else "3")


def draw_ears(c, cx, head_top, twitch=False):
    lh = 3 if twitch else 4
    _tri(c, int(cx - 4.5), int(head_top - 3), 2.6, 4)
    _tri(c, int(cx + 4.5), int(head_top - lh), 2.6, lh)
    c.put(cx - 4.5, int(head_top - 1), "s")
    c.put(cx - 5, int(head_top), "s")
    if not twitch:
        c.put(cx + 4.5, int(head_top - 1), "s")
        c.put(cx + 5, int(head_top), "s")


def draw_tail(c, cx, cy, frame):
    sway = round(math.sin(frame * 2 * math.pi / NF))
    pts = [(cx + 7, cy + 5), (cx + 8, cy + 4), (cx + 9, cy + 2),
           (cx + 9, cy), (cx + 9 + sway, cy - 2), (cx + 8 + sway, cy - 3)]
    body = set()
    for i, (x, y) in enumerate(pts):
        ch = "5" if (i // 2) % 2 == 0 else "3"
        for dx in (0, 1):
            body.add((x + dx, y))
            body.add((x + dx, y + 1))
            c.put(x + dx, y, ch)
            c.put(x + dx, y + 1, "4" if ch == "3" else ch)
    for (x, y) in list(body):
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            if (x + dx, y + dy) not in body and c.get(x + dx, y + dy) == ".":
                c.put(x + dx, y + dy, "o")


def draw_tabby(c, cx, head_cy):
    for dx, ln in ((-3, 2), (-1, 3), (1, 3), (3, 2)):
        for i in range(ln):
            c.put(cx + dx, head_cy - 4 + i, "5")


def _cat_body(c, cx, cy, rx, ry, frame, squash=0.0, twitch=False):
    ry2 = ry * (1.0 - squash)
    rx2 = rx * (1.0 + squash * 0.6)
    head_cy = cy - 3.0
    _blob(c, cx, head_cy, rx2 * 0.86, ry2 * 0.68)
    _blob(c, cx, cy + 3.2, rx2 * 0.88, ry2 * 0.62, flare=0.18)
    draw_ears(c, cx, head_cy - ry2 * 0.68 + 1, twitch=twitch)
    draw_tail(c, cx, cy, frame)
    draw_tabby(c, cx, head_cy)
    for yy in range(int(head_cy + 1), int(head_cy + 4)):
        for xx in range(int(cx - 2), int(cx + 3)):
            dd = ((xx - cx) / 2.6) ** 2 + ((yy - (head_cy + 2)) / 1.8) ** 2
            if dd <= 1.0 and c.get(xx, yy) in "1234":
                c.put(xx, yy, "1")
    for yy in range(int(cy + 1), int(cy + 5)):
        for xx in range(int(cx - 2), int(cx + 3)):
            dd = ((xx - cx) / 2.4) ** 2 + ((yy - (cy + 3)) / 2.6) ** 2
            if dd <= 1.0 and c.get(xx, yy) in "2345":
                c.put(xx, yy, "1")


# ---- claws: classic space invader, bitmap-stamped, 16x9 output px --------

# Extracted 1:1 from the reference image: classic crab invader, 12x8 grid.
# Head/body are 8 cells wide (cols 2-9); arms span the full 12.
INV_CORE = [
    "..XXXXXXXX..",
    "..XeXXXXeX..",
    "XXXXXXXXXXXX",
    "XXXXXXXXXXXX",
    "..XXXXXXXX..",
    "..XXXXXXXX..",
]
# legs are static (reference is a single pose); the bob provides the motion
INV_LEGS = [
    "..X.X..X.X..",
    "..X.X..X.X..",
]


def _stamp(c, ox, oy, row, ch):
    for rx, px in enumerate(row):
        if px == "X":
            c.put_px(ox + rx, oy, ch)
        elif px == "e":
            c.put_px(ox + rx, oy, "e")


def _claws_origin(cx, cy):
    # bitmap is 12 wide x 8 tall; center it in the OUT_W x OUT_H canvas
    return int(round(cx * OUT_W / W)) - 6, int(round(cy * OUT_H / H)) - 4


LAST_ORIGIN = (0, 0)


def _claws_body(c, cx, cy, frame):
    global LAST_ORIGIN
    ox, oy = _claws_origin(cx, cy)
    LAST_ORIGIN = (ox, oy)
    for i, row in enumerate(INV_CORE):
        for rx, px in enumerate(row):
            if px == "X":
                c.put_px(ox + rx, oy + i, "3")
            elif px == "e":
                c.put_px(ox + rx, oy + i, "e")
    for i, row in enumerate(INV_LEGS):
        for rx, px in enumerate(row):
            if px == "X":
                c.put_px(ox + rx, oy + 6 + i, "3")


def draw_body(c, cx, cy, rx, ry, frame, squash=0.0, twitch=False):
    if ACTIVE_SKIN == "claws":
        _claws_body(c, cx, cy, frame)
    else:
        _cat_body(c, cx, cy, rx, ry, frame, squash=squash, twitch=twitch)


def _cat_feet(c, cx, cy, frame, dy=0.0):
    for sx in (-3.2, 3.2):
        fx, fy = cx + sx, cy + 8.6 + dy
        for yy in range(int(fy - 1.2), int(fy + 1.4)):
            for xx in range(int(fx - 2.0), int(fx + 2.1)):
                ddx, ddy = (xx - fx) / 2.0, (yy - fy) / 1.3
                dd = ddx * ddx + ddy * ddy
                if dd <= 1.0:
                    c.put(xx, yy, "1")
                elif dd <= 1.8 and c.get(xx, yy) == ".":
                    c.put(xx, yy, "o")
        c.put(int(fx) - 1, int(fy), "o")
        c.put(int(fx) + 1, int(fy), "o")


def draw_feet(c, cx, cy, frame, dy=0.0):
    if ACTIVE_SKIN != "claws":
        _cat_feet(c, cx, cy, frame, dy=dy)


def _cat_arms(c, cx, cy, frame, raise_amt=0.0):
    for sx in (-1, 1):
        ax = cx + sx * 7.6
        ay = cy + 2.2 - raise_amt * 3.2 + 0.25 * math.sin(frame * math.pi / 4 + sx)
        for yy in range(int(ay - 1.2), int(ay + 1.4)):
            for xx in range(int(ax - 1.4), int(ax + 1.5)):
                ddx, ddy = (xx - ax) / 1.5, (yy - ay) / 1.3
                dd = ddx * ddx + ddy * ddy
                if dd <= 1.0:
                    c.put(xx, yy, "4")
                elif dd <= 1.9 and c.get(xx, yy) == ".":
                    c.put(xx, yy, "o")


def draw_arms(c, cx, cy, frame, raise_amt=0.0):
    if ACTIVE_SKIN != "claws":
        _cat_arms(c, cx, cy, frame, raise_amt=raise_amt)


# ----------------------------------------------------------------- eyes -----

def _cat_eye(c, cx, cy, kind, pdx=0.0, pdy=0.0):
    if kind in ("open", "wide", "half"):
        h = 1 if kind == "half" else (3 if kind == "wide" else 2)
        w = 3 if kind == "wide" else 2
        x0 = int(round(cx - w / 2 + pdx * 0.6))
        y0 = int(round(cy - h / 2 + pdy * 0.6))
        for yy in range(y0, y0 + h):
            for xx in range(x0, x0 + w):
                c.put(xx, yy, "e")
        c.put(x0, y0, "w")
    elif kind == "closed":
        x0 = int(round(cx - 1.5))
        for xx in range(x0, x0 + 3):
            c.put(xx, int(round(cy)), "e")
    elif kind == "happy":
        for dx, dy in ((-1.5, 0.5), (-0.5, -0.5), (0.5, -0.5), (1.5, 0.5)):
            c.put(cx + dx, cy + dy, "e")
    elif kind == "sad":
        for dx, dy in ((-1.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (1.5, -0.5)):
            c.put(cx + dx, cy + dy, "e")
    elif kind == "x":
        for d in (-1, 0, 1):
            c.put(cx + d, cy + d, "r")
            c.put(cx + d, cy - d, "r")


def _claws_eye(c, cx=None, cy=None, kind="open"):
    """Repaint the invader's 1px eye cells at the body's stamped origin."""
    ox, oy = LAST_ORIGIN
    for ex in (ox + 3, ox + 8):
        ey = oy + 1
        if kind in ("open", "wide"):
            c.put_px(ex, ey, "e")
            if kind == "wide":
                c.put_px(ex - 1, ey, "e")
                c.put_px(ex + 1, ey, "e")
                c.put_px(ex, ey - 1, "e")
                c.put_px(ex, ey + 1, "e")
        elif kind == "half":
            c.put_px(ex, ey, "e")          # 1px eye: keep at reference slot
        elif kind == "closed":
            c.put_px(ex, ey, "3")          # blink: eye vanishes into fur
        elif kind == "happy":
            c.put_px(ex, ey, "3")
            c.put_px(ex - 1, ey, "e")
            c.put_px(ex + 1, ey, "e")      # flat ^^ squint
        elif kind == "sad":
            c.put_px(ex, ey, "3")
            c.put_px(ex, ey + 1, "e")
        elif kind == "x":
            c.put_px(ex, ey, "r")


def draw_eye(c, cx, cy, kind, pdx=0.0, pdy=0.0):
    if ACTIVE_SKIN == "claws":
        _claws_eye(c, cx, cy, kind)
    else:
        _cat_eye(c, cx, cy, kind, pdx=pdx, pdy=pdy)


def draw_face(c, cx, cy, eyes, pdx=0.0, pdy=0.0, mouth="smile", blush=True):
    if ACTIVE_SKIN == "claws":
        # invader face = eyes only; props carry the state
        for ex in eyes:
            _claws_eye(c, cx, cy, ex)
        return
    for sx, ex in ((-3.4, eyes[0]), (3.4, eyes[1])):
        _cat_eye(c, cx + sx, cy, ex, pdx, pdy)
    ny = cy + 2.2
    c.put(cx, int(ny), "s")
    c.put(cx - 1, int(ny + 1), "s")
    c.put(cx, int(ny + 1), "s")
    c.put(cx + 1, int(ny + 1), "s")
    if blush:
        c.put(cx - 5.6, int(ny), "s")
        c.put(cx + 5.6, int(ny), "s")
    if mouth == "none":
        return
    mx, my = cx, ny + 2.0
    if mouth == "smile":
        for dx, dy in ((-2, -0.5), (-1, 0.5), (0, -0.5), (1, 0.5), (2, -0.5)):
            c.put(mx + dx, my + dy, "o")
    elif mouth == "open":
        for xx in range(int(mx - 1), int(mx + 2)):
            c.put(xx, int(my), "o")
            c.put(xx, int(my + 1), "R")
        c.put(int(mx), int(my + 2), "R")
    elif mouth == "o":
        for dx, dy in ((-1, 0), (1, 0), (0, 1)):
            c.put(mx + dx, int(my + dy), "o")
    elif mouth == "wave":
        for i, dx in enumerate(range(-2, 3)):
            c.put(mx + dx, int(my + (0 if i % 2 == 0 else 1)), "o")


# ----------------------------------------------------------------- bits -----

def draw_star(c, cx, cy, size, ch="y"):
    """4-point twinkle star."""
    c.put(cx, cy, ch)
    for d in range(1, size + 1):
        c.put(cx + d, cy, ch)
        c.put(cx - d, cy, ch)
        c.put(cx, cy + d, ch)
        c.put(cx, cy - d, ch)
    if size >= 2:
        for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            c.put(cx + sx, cy + sy, "L" if ch == "y" else "h")


def draw_qmark(c, cx, cy, ch="w", scale=1):
    """Question mark glyph 5x7, fully connected, dot same color."""
    pts = [(-1, -3), (0, -3), (1, -3),      # top bar
           (1, -2), (2, -2),                   # upper right
           (1, -1),
           (0, 0), (1, 0),
           (0, 1),
           (0, 3)]                            # dot
    for dx, dy in pts:
        c.put(cx + dx * scale, cy + dy * scale, ch)


def draw_sparkle(c, x, y, ch="h"):
    c.put(x, y, ch)
    c.put(x - 1, y, ch)
    c.put(x + 1, y, ch)
    c.put(x, y - 1, ch)
    c.put(x, y + 1, ch)


# ------------------------------------------------------------ state art ---

BOB = [0, 0, 1, 1, 0, 0, -1, -1][0:8]  # 2-frame dwell per level = smooth bob


def blink_frame(state_frames, idx):
    """Replace eyes on frame idx with closed (blink) version."""
    return state_frames


def frame_idle(f):
    c = Canvas()
    cx, cy = 12, 16.5 + BOB[f]
    blink = f == NF - 1
    sq = 0.05 if BOB[f] == 1 else (-0.04 if BOB[f] == -1 else 0)
    draw_body(c, cx, cy, 8.4, 8.0, f, squash=sq, twitch=(f in (2, 3)))
    draw_feet(c, cx, cy, f, dy=BOB[f])
    draw_arms(c, cx, cy, f)
    eye = "closed" if blink else "open"
    draw_face(c, cx, cy - 3.0, (eye, eye), mouth="smile" if not blink else "none")
    return c


def draw_cloud(c, cx, cy):
    """Big puffy thought cloud: union of blobs, flat-ish bottom, 1px outline."""
    blobs = [(cx - 4.5, cy + 0.6, 2.8), (cx, cy - 0.6, 3.4), (cx + 4.5, cy + 0.5, 2.9)]
    mask = set()
    for bx, by, br in blobs:
        for yy in range(int(by - br) - 1, int(by + br) + 2):
            for xx in range(int(bx - br) - 1, int(bx + br) + 2):
                if ((xx - bx) / br) ** 2 + ((yy - by) / br) ** 2 <= 1.0:
                    mask.add((xx, yy))
    # merge the bottoms into a solid belly
    for yy in range(int(cy), int(cy) + 2):
        for xx in range(int(cx - 6), int(cx + 7)):
            mask.add((xx, yy))
    for xx, yy in mask:
        c.put(xx, yy, "w")
    # outline: anything touching the cloud from outside
    for xx, yy in list(mask):
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = xx + dx, yy + dy
            if (nx, ny) not in mask and c.get(nx, ny) == ".":
                c.put(nx, ny, "o")


def frame_thinking(f):
    c = Canvas()
    cx, cy = 12, 16.5 + BOB[f]
    draw_body(c, cx, cy, 8.4, 8.0, f)
    draw_feet(c, cx, cy, f, dy=BOB[f])
    draw_arms(c, cx, cy, f)
    # eyes look up at the cloud, darting
    pdx = [-0.4, -0.4, 0.4, 0.4, 0, 0, -0.4, 0.4][f]
    draw_face(c, cx, cy - 3.0, ("open", "open"), pdx=pdx, pdy=-0.9, mouth="o")
    # thought trail rising from the head into the cloud
    trail = [(15.2, 8.6, 0.6), (16.4, 7.4, 0.9)]
    for i, (bx, by, br) in enumerate(trail):
        if f % 4 >= i:
            for yy in range(int(by - br) - 1, int(by + br) + 2):
                for xx in range(int(bx - br) - 1, int(bx + br) + 2):
                    if ((xx - bx) / (br + 0.4)) ** 2 + ((yy - by) / (br + 0.4)) ** 2 <= 1.0:
                        c.put(xx, yy, "w")
    # big cloud above the head, breathing gently
    lift = [0, 0, 0, 1, 1, 1, 0, 0][f]
    draw_cloud(c, 12, 3.5 - lift)
    # pulsing ? centered in the cloud
    wob = [0, 0, 1, 1, 0, -1, -1, 0][f]
    draw_qmark(c, 12 + wob, 3.2 - lift, ch="k")
    return c


def frame_idea(f):
    c = Canvas()
    cx, cy = 12, 16.5 + BOB[f]
    # bulb pops in f0-2, rays flash f2-5, steady glow f6-7
    scale = [0.4, 0.7, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0][f]
    bx, by = 12, 3.2
    if scale > 0.5:
        r = 2.6
        for yy in range(int(by - r) - 1, int(by + r) + 2):
            for xx in range(int(bx - r) - 1, int(bx + r) + 2):
                ddx, ddy = (xx - bx) / r, (yy - by) / r
                dd = ddx * ddx + ddy * ddy
                if dd <= 0.45:
                    c.put(xx, yy, "L")
                elif dd <= 1.0:
                    c.put(xx, yy, "y")
                elif dd <= 1.35 and c.get(xx, yy) == ".":
                    c.put(xx, yy, "o")
        # base
        c.put(bx - 1, by + 3, "k")
        c.put(bx, by + 3, "k")
        c.put(bx + 1, by + 3, "k")
        c.put(bx - 1, by + 4, "k")
        c.put(bx + 1, by + 4, "k")
    # rays appear progressively
    ray_order = [(-4, 0), (4, 0), (0, -4), (-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4)]
    n_rays = [0, 3, 8, 8, 5, 8, 3, 8][f]
    for i in range(n_rays):
        dx, dy = ray_order[i]
        ch = "y" if i % 2 == 0 else "L"
        c.put(bx + dx, by + dy, ch)
        if abs(dx) + abs(dy) > 4:
            c.put(bx + int(dx * 1.4), by + int(dy * 1.4), ch)
    draw_body(c, cx, cy, 8.4, 8.0, f)
    draw_feet(c, cx, cy, f, dy=BOB[f])
    draw_arms(c, cx, cy, f, raise_amt=1.0 if f % 4 < 2 else 0.4)
    draw_face(c, cx, cy - 3.0, ("happy", "happy"), mouth="open", blush=True)
    if f in (2, 3, 4, 5):
        draw_sparkle(c, 4, 6, "y")
        draw_sparkle(c, 20, 7, "y")
    return c


def frame_writing(f):
    c = Canvas()
    cx, cy = 12, 16.5 + BOB[f]
    draw_body(c, cx, cy, 8.4, 7.6, f)
    draw_feet(c, cx, cy, f, dy=BOB[f])
    # paper held in front — fixed size, always shows at least one line
    px0, px1, py0 = 5, 18, 22
    for yy in range(py0, py0 + 5):
        for xx in range(px0, px1 + 1):
            edge = yy == py0 or xx == px0 or xx == px1 or yy == py0 + 4
            c.put(xx, yy, "o" if edge else "n")
    # lines grow f0->f6 then reset f7 (new page)
    done_lines = [1, 1, 2, 2, 3, 3, 4, 0][f]
    active_len = [5, 9, 7, 11, 9, 13, 11, 0][f]
    for li in range(done_lines):
        yy = py0 + 1 + li
        ln = 13 if li < done_lines - 1 else active_len
        for xx in range(px0 + 2, min(px0 + 2 + ln, px1)):
            c.put(xx, yy, "N")
    # pencil: FIXED 5px shaft + tip, glides along the active line, stays on-canvas
    active_y = py0 + max(0, done_lines - 1) if done_lines else py0 + 1
    if ACTIVE_SKIN == "claws":
        # compact invader: vertical pencil just right of the paper
        tipx, tipy = px1 + 2, py0 + 1
        c.put(tipx, tipy, "k")
        for d in (1, 2, 3):
            c.put(tipx, tipy - d, "y")
            c.put(tipx + 1, tipy - d, "y")
        c.put(tipx, tipy - 4, "Y")
        c.put(tipx + 1, tipy - 4, "Y")
        c.put(tipx, tipy - 5, "s")
        c.put(tipx + 1, tipy - 5, "s")
    else:
        tipx = min(px0 + 1 + active_len, px1 - 5)
        tipy = active_y
        c.put(tipx, tipy, "k")                 # graphite tip
        for d in range(1, 4):                   # wood shaft
            c.put(tipx + d, tipy - d, "y")
            c.put(tipx + d + 1, tipy - d, "y")
        c.put(tipx + 4, tipy - 3, "Y")        # ferrule
        c.put(tipx + 5, tipy - 4, "s")        # eraser
        c.put(tipx + 4, tipy - 4, "s")
        # ink dot on the fresh line
        if f % 2 == 0:
            c.put(tipx - 1, tipy, "k")
    # eyes look down at page
    draw_face(c, cx, cy - 3.2, ("half", "half"), pdy=0.8, mouth="smile")
    return c


def frame_researching(f):
    c = Canvas()
    cx, cy = 12, 16.5 + BOB[f]
    draw_body(c, cx, cy, 8.4, 8.0, f)
    draw_feet(c, cx, cy, f, dy=BOB[f])
    # face first, so the magnifier overlaps it with the eye visible through glass
    pdx = 0.4 if f < 4 else -0.4
    draw_face(c, cx, cy - 3.0, ("open", "open"), pdx=pdx, pdy=0.2, mouth="smile")
    # magnifier sweeps across the face: big lens, thick rim, eye visible inside
    if ACTIVE_SKIN == "claws":
        # invader: keep the two-eye read intact — lens hovers above-right
        gx = cx + 4.0 + [0, 0.6, 1.0, 0.6, 0, -0.6, -1.0, -0.6][f]
        gy = cy - 8.0
    else:
        gx = [8.4, 10, 12, 14, 15.6, 14, 12, 10][f]
        gy = cy - 1.2
    r = 3.9
    # handle first (under the rim): always lower-left so the grip never flips
    hx0 = gx - 2.6
    hs = -1
    if ACTIVE_SKIN == "claws":
        hx0 = gx + 2.6
        hs = 1
    for d in range(1, 4):
        c.put(hx0 + d * hs, gy + 2.6 + d, "k")
        c.put(hx0 + d * hs + hs, gy + 2.6 + d, "k")
    for yy in range(int(gy - r) - 2, int(gy + r) + 3):
        for xx in range(int(gx - r) - 2, int(gx + r) + 3):
            ddx, ddy = (xx - gx) / r, (yy - gy) / r
            dd = ddx * ddx + ddy * ddy
            prev = c.get(xx, yy)
            if dd <= 1.0:
                if prev == "e":
                    c.put(xx, yy, "e")       # eye stays visible through glass
                elif prev == "w":
                    c.put(xx, yy, "w")       # face gloss shines through
                else:
                    c.put(xx, yy, "c")       # tinted glass over fur/background
            elif dd <= 1.75:
                c.put(xx, yy, "o")           # thick visible rim
    # glass shine streak
    c.put(gx - 1.4, gy - 1.8, "w")
    c.put(gx - 0.4, gy - 2.4, "w")
    # orbiting sparkle
    ang = f * 2 * math.pi / NF
    ox, oy = cx + math.cos(ang) * 10.5, cy - 4 + math.sin(ang) * 3.2
    draw_sparkle(c, ox, oy, "h")
    return c


def frame_reading(f):
    c = Canvas()
    cx, cy = 12, 16.5 + BOB[f]
    draw_body(c, cx, cy, 8.4, 8.0, f)
    # open book in front (covers lower face) — page flutters every frame
    lift = [0, 1, 2, 2, 1, 0, -1, 0][f]
    # left page
    for yy in range(21, 27):
        slant = 0 if yy < 23 else 0
        for xx in range(3, 12):
            edge = yy == 21 or yy == 26 or xx == 3
            c.put(xx, yy, "o" if edge else "n")
    # right page (flutter lifts its outer edge)
    for yy in range(21 - max(0, lift), 27):
        for xx in range(12, 21):
            edge = yy == (21 - max(0, lift)) or yy == 26 or xx == 20
            c.put(xx, yy, "o" if edge else ("w" if lift and xx > 17 else "n"))
    # spine
    for yy in range(21, 27):
        c.put(11, yy, "o")
        c.put(12, yy, "R")
    # red cover edges bottom
    for xx in range(3, 21):
        c.put(xx, 26, "r")
        c.put(xx, 27, "o")
    # text dashes
    for yy in (22, 23, 24):
        for xx in range(5, 10):
            if (xx + yy) % 2 == 0:
                c.put(xx, yy, "N")
        for xx in range(13, 18):
            if (xx + yy + lift) % 2 == 0:
                c.put(xx, yy, "N")
    # eyes peek over the top edge, looking down
    draw_eye(c, cx - 3.4, cy - 3.4, "half", pdy=1.0)
    draw_eye(c, cx + 3.4, cy - 3.4, "half", pdy=1.0)
    if ACTIVE_SKIN != "claws":
        c.put(cx - 5.6, cy - 1.2, "s")
        c.put(cx + 5.6, cy - 1.2, "s")
    # floating letters rising
    for i, (lx, phase) in enumerate(((2, 0), (21, 2))):
        ly = 18 - ((f + phase) % 4) * 2
        if 4 < ly < 19:
            c.put(lx, ly, "h")
            c.put(lx + 1, ly - 1, "h")
    return c


def frame_complete(f):
    c = Canvas()
    bounce = [0, 1, 2, 1, 0, -1, -2, -1][f]
    cx, cy = 12, 16.5 + bounce * 0.6
    sq = 0.06 if bounce == 2 else (-0.05 if bounce == -2 else 0)
    # confetti: clustered 2px bits on steady falling paths, present every frame
    rng = random.Random(99)
    parts = [(rng.randrange(1, W - 1), rng.randrange(0, 16),
              rng.choice(["y", "s", "a", "c", "3", "h"]),
              rng.choice([1, 2])) for _ in range(12)]
    for px, py0, pch, spd in parts:
        py = (py0 + f * spd * 2) % 20          # fall zone above/around body
        sway = round(math.sin((f + py0) * math.pi / 4))
        c.put(px + sway, py, pch)
        c.put(px + sway, py + 1, pch)          # 2px cluster, reads as confetti
        if spd == 2:
            c.put(px + sway + 1, py, pch)
    draw_body(c, cx, cy, 8.4, 8.0, f, squash=sq, twitch=(f in (2, 3)))
    draw_feet(c, cx, cy, f, dy=bounce * 0.6)
    draw_arms(c, cx, cy, f, raise_amt=1.2)
    draw_face(c, cx, cy - 3.0, ("happy", "happy"), mouth="open", blush=True)
    # big sparkles beside head
    if f % 2 == 0:
        draw_star(c, 2, 9, 1, "y")
        draw_star(c, 21, 11, 1, "y")
    return c


def frame_confused(f):
    c = Canvas()
    tilt = [0, 0, 1, 1, 0, -1, -1, 0][f]
    cx, cy = 12 + tilt * 0.6, 16.5 + BOB[f]
    # tilt the whole sprite slightly (props stay upright)
    draw_body(c, cx, cy, 8.4, 8.0, f)
    draw_feet(c, cx, cy, f, dy=BOB[f])
    draw_arms(c, cx, cy, f)
    # pupils dart side to side
    pdx = [1.2, 1.2, 1.2, 0, -1.2, -1.2, -1.2, 0][f]
    draw_face(c, cx + tilt, cy - 1.2, ("open", "open"), pdx=pdx, pdy=0.3, mouth="wave")
    # sweat drop sliding down
    sy = [7, 8, 9, 10, 11, 12, 13, 14][f]
    sx = cx + 7.6
    c.put(sx, sy, "c")
    c.put(sx, sy + 1, "c")
    c.put(sx - 1, sy + 1, "c")
    c.put(sx, sy + 2, "C")
    c.put(sx, sy - 1, "w")
    # wobbling ? above
    wob = [0, 1, 1, 0, -1, -1, 0, 1][f]
    draw_qmark(c, cx + 6 + wob, 4.0, ch="y")
    return c


def frame_error(f):
    c = Canvas()
    jitter = [0, -1, 1, 0, 1, -1, 0, 1][f]  # tight ±1px shake, no vertical teleport
    cx, cy = 12 + jitter, 16.5
    draw_body(c, cx, cy, 8.4, 8.0, f)
    draw_feet(c, cx, cy, f)
    draw_arms(c, cx, cy, f)
    draw_face(c, cx, cy - 3.0, ("x", "x"), mouth="sad", blush=False)
    # glitch static: fixed slots that shimmer (never fully vanish)
    if ACTIVE_SKIN == "claws":
        # invader: particles only around the silhouette, never on it
        slots = [(1, 6), (16, 5), (0, 14), (17, 13), (2, 22), (15, 23)]
    else:
        slots = [(3, 8), (20, 7), (2, 18), (21, 16), (5, 24), (18, 25), (1, 12), (22, 11)]
    for i, (sx, sy) in enumerate(slots):
        if (f + i) % 3 == 0:
            continue  # some slots blink off, at least 5 stay lit
        ch = ["r", "R", "h"][(f + i) % 3]
        c.put(sx + jitter, sy, ch)
        c.put(sx + jitter + 1, sy, ch)
    # red sparks falling on fixed columns, always visible
    for sx0, ph in ((5, 0), (12, 4), (18, 2)):
        sy = 2 + ((ph + f * 2) % 4) * 2       # cycles rows 2..8, above body
        c.put(sx0 + jitter, sy, "r")
        c.put(sx0 + jitter, sy + 1, "r")
    return c


FRAME_FUNCS = {
    "idle": frame_idle,
    "thinking": frame_thinking,
    "idea": frame_idea,
    "writing": frame_writing,
    "researching": frame_researching,
    "reading": frame_reading,
    "complete": frame_complete,
    "confused": frame_confused,
    "error": frame_error,
}


# ---------------------------------------------------------------- output ----

def build_skin(skin):
    global ACTIVE_SKIN
    ACTIVE_SKIN = skin
    out = {}
    for state in STATES:
        out[state] = [FRAME_FUNCS[state](f).rows() for f in range(NF)]
    ACTIVE_SKIN = "cat"
    return out


def emit_ts():
    lines = []
    lines.append('import type { AgentStatus } from "./status.js"')
    lines.append("")
    lines.append("// Generated by tools/generate_frames.py — do not hand-edit the frame data.")
    lines.append("// Regenerate with: python3 tools/generate_frames.py")
    lines.append("")
    lines.append('export type Skin = "cat" | "claws"')
    lines.append('export const DEFAULT_SKIN: Skin = "cat"')
    lines.append("")
    lines.append("export const CAT_ORANGE = \"#E89B3C\"")
    lines.append("export const ERROR_RED = \"#E06C75\"")
    lines.append("")
    lines.append("// Palette-indexed truecolor frames: %dx%d native pixels, 8 frames/state." % (OUT_W, OUT_H))
    lines.append("// Each frame is %d strings of %d chars; each char indexes the skin palette." % (OUT_H, OUT_W))
    lines.append("export const PALETTES: Record<Skin, Record<string, string>> = {")
    for skin in SKINS:
        pal = dict(SHARED)
        pal.update(SKIN_PALETTES[skin])
        lines.append("  %s: {" % skin)
        for ch, hexv in pal.items():
            if hexv is None:
                continue
            lines.append(f'    "{ch}": "{hexv}",')
        lines.append("  },")
    lines.append("}")
    lines.append("")
    lines.append("export const SPRITE_WIDTH = %d" % OUT_W)
    lines.append("export const SPRITE_HEIGHT = %d" % OUT_H)
    lines.append("export const FRAMES_PER_STATE = 8")
    lines.append("")
    lines.append("export type PixelCell = string | null")
    lines.append("export type PixelRow = PixelCell[]")
    lines.append("export type PixelFrame = PixelRow[]")
    lines.append("")
    lines.append("export const FRAME_ROWS: Record<Skin, Record<AgentStatus, string[][]>> = {")
    for skin in SKINS:
        data = build_skin(skin)
        lines.append("  %s: {" % skin)
        for state in STATES:
            lines.append(f"    {state}: [")
            for rows in data[state]:
                lines.append("      [")
                for r in rows:
                    lines.append(f'        "{r}",')
                lines.append("      ],")
            lines.append("    ],")
        lines.append("  },")
    lines.append("}")
    lines.append("")
    lines.append("// Expand palette rows to truecolor pixel maps once at module load.")
    lines.append("export const FRAMES: Record<Skin, Record<AgentStatus, PixelFrame[]>> =")
    lines.append("  Object.fromEntries(")
    lines.append("    Object.entries(FRAME_ROWS).map(([skin, states]) => [")
    lines.append("      skin,")
    lines.append("      Object.fromEntries(")
    lines.append("        Object.entries(states).map(([state, frames]) => [")
    lines.append("          state,")
    lines.append("          frames.map((rows) =>")
    lines.append("            rows.map((row) => [...row].map((ch) => PALETTES[skin as Skin][ch] ?? null)),")
    lines.append("          ),")
    lines.append("        ]),")
    lines.append("      ),")
    lines.append("    ]),")
    lines.append("  ) as Record<Skin, Record<AgentStatus, PixelFrame[]>>")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "src", "avatar", "frames.ts")
    with open(out, "w") as fh:
        fh.write(emit_ts())
    print(f"wrote {out}")