#!/usr/bin/env python3
"""Petsy sprite generator — deterministic, stdlib-only (Pillow only used by preview).

Writes src/avatar/frames.ts: palette-indexed 24x30 frames, 8 frames per state.
Design: soot-sprite blob with animated fur, gradient shading, glossy eyes,
per-state props (bulb, magnifier, book, pencil) and particle systems.

Run:  python3 tools/generate_frames.py
"""
import math
import random

W, H = 24, 30
NF = 8  # frames per state

# ---------------------------------------------------------------- palette ---
PALETTE = {
    ".": None,
    "o": "#463258",  # outline
    "1": "#F6EBFF",  # body highlight
    "2": "#E4CDFF",  # body light
    "3": "#C8B6FF",  # body base (brand pastel purple)
    "4": "#AE8FE8",  # body shade
    "5": "#9271CC",  # body deep
    "6": "#7A57B0",  # body deepest
    "e": "#241F33",  # eye dark
    "w": "#FFFFFF",  # white gloss
    "g": "#9E96B8",  # eye gloss gray
    "s": "#F5A3C0",  # blush / pink
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
    "h": "#E9E2FF",  # sparkle lavender
}

STATES = ["idle", "thinking", "idea", "writing", "researching",
          "reading", "complete", "confused", "error"]

# ------------------------------------------------------------- primitives ---

class Canvas:
    def __init__(self):
        self.px = [["."] * W for _ in range(H)]

    def put(self, x, y, ch):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < W and 0 <= y < H:
            self.px[y][x] = ch

    def get(self, x, y):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < W and 0 <= y < H:
            return self.px[y][x]
        return "."

    def rows(self):
        return ["".join(r) for r in self.px]


def ellipse_fill(c, cx, cy, rx, ry, test):
    """Fill integer pixels whose center passes test(dx,dy)."""
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            dx, dy = x - cx, y - cy
            if test(dx, dy):
                c.put(x, y, test.ch)


# ------------------------------------------------------------- fur noise ----
FUR_SEED = 7
_r = random.Random(FUR_SEED)
FUR_BASE = [_r.uniform(-1.0, 1.0) for _ in range(48)]
FUR_SPIKE = [1 if _r.random() < 0.22 else 0 for _ in range(48)]


def fur_radius(theta, frame, amp=1.0):
    """Silhouette radius multiplier at angle theta for this frame."""
    b = int(((theta + math.pi) / (2 * math.pi)) * 48) % 48
    drift = frame  # fur shimmer drifts around the body
    i0 = (b + drift) % 48
    i1 = (b + drift + 1) % 48
    frac = ((b + drift) % 1)
    n = FUR_BASE[i0] * (1 - frac) + FUR_BASE[i1] * frac
    spike = max(FUR_SPIKE[i0], FUR_SPIKE[i1])
    return 1.0 + amp * (0.055 * n + 0.16 * spike)


# ----------------------------------------------------------------- body -----

def shade_char(dx, dy, rx, ry):
    """Interior shading: light from top-left."""
    # normalized position, light vector (-0.62, -0.70)
    lx, ly = dx / rx, dy / ry
    l = lx * -0.62 + ly * -0.70          # ~ +1 top-left, -1 bottom-right
    d = math.sqrt(lx * lx + ly * ly)      # 0 center .. 1 edge
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


def draw_body(c, cx, cy, rx, ry, frame, squash=0.0):
    """Furry blob with dark outline. squash>0 widens & flattens."""
    ry2 = ry * (1.0 - squash)
    rx2 = rx * (1.0 + squash * 0.6)
    for y in range(0, H):
        for x in range(0, W):
            dx, dy = x - cx, y - cy
            if abs(dx) > rx2 + 3 or abs(dy) > ry2 + 3:
                continue
            theta = math.atan2(dy / ry2, dx / rx2)
            fr = fur_radius(theta, frame)
            d = math.sqrt((dx / rx2) ** 2 + (dy / ry2) ** 2)
            if d <= fr - 0.16:
                c.put(x, y, shade_char(dx, dy, rx2, ry2))
            elif d <= fr + 0.12:
                c.put(x, y, "o")


def draw_feet(c, cx, cy, frame, dy=0.0):
    # feet touch the body bottom (no background gap): body bottom ~ cy+8
    for sx in (-3.4, 3.4):
        fx, fy = cx + sx, cy + 9.4 + dy
        for yy in range(int(fy - 1.4), int(fy + 1.6)):
            for xx in range(int(fx - 1.8), int(fx + 1.9)):
                ddx, ddy = (xx - fx) / 1.9, (yy - fy) / 1.45
                dd = ddx * ddx + ddy * ddy
                if dd <= 1.0:
                    c.put(xx, yy, "5")
                elif dd <= 1.75 and c.get(xx, yy) == ".":
                    c.put(xx, yy, "o")


def draw_arms(c, cx, cy, frame, raise_amt=0.0):
    """Little nub arms at the sides; raise_amt lifts them up."""
    for sx in (-1, 1):
        ax = cx + sx * 8.6
        ay = cy + 2.6 - raise_amt * 3.2 + 0.25 * math.sin(frame * math.pi / 4 + sx)
        for yy in range(int(ay - 1.2), int(ay + 1.4)):
            for xx in range(int(ax - 1.4), int(ax + 1.5)):
                ddx, ddy = (xx - ax) / 1.5, (yy - ay) / 1.3
                dd = ddx * ddx + ddy * ddy
                if dd <= 1.0:
                    c.put(xx, yy, "4")
                elif dd <= 1.9:
                    c.put(xx, yy, "o")


# ----------------------------------------------------------------- eyes -----

def draw_eye(c, cx, cy, kind, pdx=0.0, pdy=0.0):
    """kind: open | closed | happy | sad | x | wide | half"""
    rx, ry = 2.5, 3.0
    if kind == "open" or kind == "wide" or kind == "half":
        ry_e = ry if kind != "half" else 1.9
        rx_e = rx if kind != "wide" else rx + 0.5
        for yy in range(int(cy - ry_e) - 1, int(cy + ry_e) + 2):
            for xx in range(int(cx - rx_e) - 1, int(cx + rx_e) + 2):
                dx, dy = (xx - cx) / rx_e, (yy - cy) / ry_e
                dd = dx * dx + dy * dy
                if dd <= 1.0:
                    c.put(xx, yy, "e")
        # gloss: big highlight top-left, small bottom-right
        hx, hy = cx - 1.0 + pdx, cy - 1.3 + pdy
        c.put(hx, hy, "w")
        c.put(hx + 1, hy, "w")
        c.put(hx, hy + 1, "w")
        c.put(cx + 1.2 - pdx * 0.5, cy + 1.5 - pdy * 0.4, "g")
    elif kind == "closed":
        for i, xx in enumerate(range(int(cx - 2.4), int(cx + 2.5))):
            yy = cy + (0 if i in (0, 4) else (1 if i in (1, 3) else 1))
            c.put(xx, yy, "e")
        c.put(cx - 2.4, cy - 1, "e")
        c.put(cx + 2.4, cy - 1, "e")
    elif kind == "happy":  # ^ arc
        pts = [(-2.4, 0.6), (-1.6, -0.4), (-0.8, -1.2), (0, -1.5),
               (0.8, -1.2), (1.6, -0.4), (2.4, 0.6)]
        for dx, dy in pts:
            c.put(cx + dx, cy + dy, "e")
    elif kind == "sad":
        pts = [(-2.2, -0.8), (-1.4, 0.2), (0, 0.8), (1.4, 0.2), (2.2, -0.8)]
        for dx, dy in pts:
            c.put(cx + dx, cy + dy, "e")
    elif kind == "x":
        for d in range(-2, 3):
            c.put(cx + d, cy + d, "r")
            c.put(cx + d, cy - d, "r")


def draw_face(c, cx, cy, eyes, pdx=0.0, pdy=0.0, mouth="smile", blush=True):
    for sx, ex in ((-3.6, eyes[0]), (3.6, eyes[1])):
        draw_eye(c, cx + sx, cy, ex, pdx, pdy)
    if blush:
        c.put(cx - 6.2, cy + 2.6, "s")
        c.put(cx - 5.2, cy + 2.6, "s")
        c.put(cx + 5.2, cy + 2.6, "s")
        c.put(cx + 6.2, cy + 2.6, "s")
    mx, my = cx, cy + 4.6
    if mouth == "smile":
        c.put(mx - 1, my, "e")
        c.put(mx, my + 1, "e")
        c.put(mx + 1, my, "e")
    elif mouth == "open":
        for xx in range(int(mx - 1.5), int(mx + 2.5)):
            c.put(xx, my, "e")
            c.put(xx, my + 1, "e")
        c.put(mx - 2, my, "e")
        c.put(mx + 2, my, "e")
        c.put(mx, my + 2, "e")
        c.put(mx - 1, my + 2, "e")
        c.put(mx + 1, my + 2, "e")
    elif mouth == "o":
        for dx, dy in ((-1, 0), (1, 0), (0, 1), (-1, 1), (1, 1), (0, 2)):
            c.put(mx + dx, my + dy, "e")
    elif mouth == "wave":
        for i, dx in enumerate(range(-2, 3)):
            c.put(mx + dx, my + (0 if i % 2 == 0 else 1), "e")


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
    # twinkling star above head (min size 2 so it always reads as a star)
    star_size = [2, 2, 3, 3, 2, 2, 3, 2][f]
    draw_star(c, 12, 3.5 + BOB[f] * 0.5, star_size)
    draw_body(c, cx, cy, 8.4, 8.0, f, squash=sq)
    draw_feet(c, cx, cy, f, dy=BOB[f])
    draw_arms(c, cx, cy, f)
    eye = "closed" if blink else "open"
    draw_face(c, cx, cy - 1.2, (eye, eye), mouth="smile" if not blink else "none")
    # ambient sparkles
    if f % 2 == 0:
        draw_sparkle(c, 3 + (f % 3), 8 + (f % 2), "h")
        draw_sparkle(c, 20, 12 + (f % 3), "h")
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
    draw_face(c, cx, cy - 1.2, ("open", "open"), pdx=pdx, pdy=-0.9, mouth="o")
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
    draw_face(c, cx, cy - 1.2, ("happy", "happy"), mouth="open", blush=True)
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
    tipx = min(px0 + 1 + active_len, px1 - 5)
    tipy = active_y
    c.put(tipx, tipy, "k")                     # graphite tip
    for d in range(1, 4):                       # wood shaft
        c.put(tipx + d, tipy - d, "y")
        c.put(tipx + d + 1, tipy - d, "y")
    c.put(tipx + 4, tipy - 3, "Y")            # ferrule
    c.put(tipx + 5, tipy - 4, "s")            # eraser
    c.put(tipx + 4, tipy - 4, "s")
    # ink dot on the fresh line
    if f % 2 == 0:
        c.put(tipx - 1, tipy, "k")
    # eyes look down at page
    draw_face(c, cx, cy - 1.4, ("half", "half"), pdy=0.8, mouth="smile")
    return c


def frame_researching(f):
    c = Canvas()
    cx, cy = 12, 16.5 + BOB[f]
    draw_body(c, cx, cy, 8.4, 8.0, f)
    draw_feet(c, cx, cy, f, dy=BOB[f])
    # face first, so the magnifier overlaps it with the eye visible through glass
    pdx = 0.4 if f < 4 else -0.4
    draw_face(c, cx, cy - 1.2, ("open", "open"), pdx=pdx, pdy=0.2, mouth="smile")
    # magnifier sweeps across the face: big lens, thick rim, eye visible inside
    gx = [8.4, 10, 12, 14, 15.6, 14, 12, 10][f]
    gy = cy - 1.2
    r = 3.9
    # handle first (under the rim): always lower-left so the grip never flips
    hx0 = gx - 2.6
    hs = -1
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
    draw_eye(c, cx - 3.6, cy - 1.6, "half", pdy=1.0)
    draw_eye(c, cx + 3.6, cy - 1.6, "half", pdy=1.0)
    c.put(cx - 6.2, cy + 1.0, "s")
    c.put(cx + 6.2, cy + 1.0, "s")
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
    draw_body(c, cx, cy, 8.4, 8.0, f, squash=sq)
    draw_feet(c, cx, cy, f, dy=bounce * 0.6)
    draw_arms(c, cx, cy, f, raise_amt=1.2)
    draw_face(c, cx, cy - 1.2, ("happy", "happy"), mouth="open", blush=True)
    # big sparkles beside head
    if f % 2 == 0:
        draw_star(c, 2, 9, 1, "y")
        draw_star(c, 21, 11, 1, "y")
    return c


def frame_confused(f):
    c = Canvas()
    tilt = [0, 0, 1, 1, 0, -1, -1, 0][f]
    cx, cy = 12 + tilt * 0.6, 16.5 + BOB[f]
    # sheared body: rows above center shift with tilt
    for y in range(0, H):
        for x in range(0, W):
            dx, dy = x - cx, y - cy
            if abs(dx) > 11 or abs(dy) > 11:
                continue
            shear = tilt * (cy - y) * 0.10
            dxs = dx - shear
            theta = math.atan2(dy / 8.0, dxs / 8.4)
            fr = fur_radius(theta, f)
            d = math.sqrt((dxs / 8.4) ** 2 + (dy / 8.0) ** 2)
            if d <= fr - 0.16:
                c.put(x, y, shade_char(dxs, dy, 8.4, 8.0))
            elif d <= fr + 0.12:
                c.put(x, y, "o")
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
    draw_face(c, cx, cy - 1.2, ("x", "x"), mouth="sad", blush=False)
    # glitch static: fixed slots that shimmer (never fully vanish)
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

def emit_ts():
    lines = []
    lines.append('import type { AgentStatus } from "./status.js"')
    lines.append("")
    lines.append("// Generated by tools/generate_frames.py — do not hand-edit the frame data.")
    lines.append("// Regenerate with: python3 tools/generate_frames.py")
    lines.append("")
    lines.append("export const PASTEL_PURPLE = \"#C8B6FF\"")
    lines.append("export const ERROR_RED = \"#E06C75\"")
    lines.append("")
    lines.append("// Palette-indexed truecolor frames: 24x30 native pixels, 8 frames/state.")
    lines.append("// Each frame is 30 strings of 24 chars; each char indexes PALETTE.")
    lines.append("export const PALETTE: Record<string, string> = {")
    for ch, hexv in PALETTE.items():
        if hexv is None:
            continue
        lines.append(f"  \"{ch}\": \"{hexv}\",")
    lines.append("}")
    lines.append("")
    lines.append("export const SPRITE_WIDTH = 24")
    lines.append("export const SPRITE_HEIGHT = 30")
    lines.append("export const FRAMES_PER_STATE = 8")
    lines.append("")
    lines.append("export type PixelCell = string | null")
    lines.append("export type PixelRow = PixelCell[]")
    lines.append("export type PixelFrame = PixelRow[]")
    lines.append("")
    lines.append("export const FRAME_ROWS: Record<AgentStatus, string[][]> = {")
    for state in STATES:
        lines.append(f"  {state}: [")
        for f in range(NF):
            rows = FRAME_FUNCS[state](f).rows()
            lines.append("    [")
            for r in rows:
                lines.append(f"      \"{r}\",")
            lines.append("    ],")
        lines.append("  ],")
    lines.append("}")
    lines.append("")
    lines.append("// Expand palette rows to truecolor pixel maps once at module load.")
    lines.append("export const FRAMES: Record<AgentStatus, PixelFrame[]> = Object.fromEntries(")
    lines.append("  Object.entries(FRAME_ROWS).map(([state, frames]) => [")
    lines.append("    state,")
    lines.append("    frames.map((rows) =>")
    lines.append("      rows.map((row) => [...row].map((ch) => PALETTE[ch] ?? null)),")
    lines.append("    ),")
    lines.append("  ]),")
    lines.append(") as Record<AgentStatus, PixelFrame[]>")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "src", "avatar", "frames.ts")
    with open(out, "w") as fh:
        fh.write(emit_ts())
    print(f"wrote {out}")
