#!/usr/bin/env python3
"""Render preview PNG contact sheet + animated GIF from the generated frames.

Parses src/avatar/frames.ts (palette + FRAME_ROWS). No dependencies beyond Pillow.
Usage: python3 tools/render_preview.py [outdir]
"""
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES_TS = os.path.join(HERE, "src", "avatar", "frames.ts")

SCALE = 8
PAD = 10
LABEL_H = 22
BG = (24, 22, 32)


def parse():
    src = open(FRAMES_TS).read()
    pal = dict(re.findall(r'"(.)": "(#[0-9a-fA-F]{6})"', src))
    block = src[src.index("FRAME_ROWS"):]
    states = re.findall(r"(\w+): \[", block)
    frames = {}
    for i, st in enumerate(states):
        start = block.index(f"{st}: [")
        end = len(block)
        for other in states:
            if other == st:
                continue
            j = block.find(f"\n  {other}: [", start + 1)
            if j != -1 and j < end:
                end = j
        body = block[start:end]
        rows = re.findall(r'"([.0-9a-zA-Z]+)"', body)
        frames[st] = [rows[k:k + 30] for k in range(0, len(rows), 30)]
    return pal, frames


def tile(pal, frame):
    h = len(frame)
    w = len(frame[0])
    img = Image.new("RGB", (w * SCALE, h * SCALE), BG)
    d = ImageDraw.Draw(img)
    for y, row in enumerate(frame):
        for x, ch in enumerate(row):
            hexv = pal.get(ch)
            if hexv:
                d.rectangle([x * SCALE, y * SCALE,
                            (x + 1) * SCALE - 1, (y + 1) * SCALE - 1],
                           fill=hexv)
    return img


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "preview")
    os.makedirs(outdir, exist_ok=True)
    pal, frames = parse()
    states = list(frames.keys())
    nf = 8
    label_img = None
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
    except Exception:
        f = ImageFont.load_default()

    tw, th = 24 * SCALE, 30 * SCALE
    # contact sheet
    sheet = Image.new("RGB", (PAD + (tw + PAD) * nf + PAD,
                              PAD + (LABEL_H + th + PAD) * len(states)), BG)
    d = ImageDraw.Draw(sheet)
    for si, st in enumerate(states):
        y0 = PAD + si * (LABEL_H + th + PAD)
        d.text((PAD, y0), st, fill=(180, 170, 210), font=f)
        for fi in range(nf):
            t = tile(pal, frames[st][fi])
            sheet.paste(t, (PAD + fi * (tw + PAD), y0 + LABEL_H))
    sheet.save(os.path.join(outdir, "petsy-frames.png"))
    print("sheet:", os.path.join(outdir, "petsy-frames.png"), sheet.size)

    # gif: cycle all states, 2 loops each
    fps_ms = 125
    seq = []
    for st in states:
        for rep in range(2):
            for fi in range(nf):
                seq.append((st, fi))
    gw, gh = tw + 2 * PAD, th + LABEL_H + 2 * PAD
    gif_frames = []
    for st, fi in seq:
        g = Image.new("RGB", (gw, gh), BG)
        gd = ImageDraw.Draw(g)
        gd.text((PAD, PAD), f"{st} {fi + 1}/{nf}", fill=(180, 170, 210), font=f)
        g.paste(tile(pal, frames[st][fi]), (PAD, PAD + LABEL_H))
        gif_frames.append(g.convert("P", palette=Image.Palette.ADAPTIVE, colors=256))
    gif_frames[0].save(os.path.join(outdir, "petsy-demo.gif"),
                      save_all=True, append_images=gif_frames[1:],
                      duration=fps_ms, loop=0)
    print("gif:", os.path.join(outdir, "petsy-demo.gif"))


if __name__ == "__main__":
    main()
