#!/usr/bin/env python3
"""Render preview PNG contact sheets + animated GIFs from the generated frames.

Parses src/avatar/frames.ts (per-skin PALETTES + FRAME_ROWS). Pillow only.
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
    width = int(re.search(r"SPRITE_WIDTH = (\d+)", src).group(1))
    height = int(re.search(r"SPRITE_HEIGHT = (\d+)", src).group(1))

    # per-skin palettes
    pal_block = src[src.index("PALETTES"):src.index("SPRITE_WIDTH")]
    palettes = {}
    for skin in ("cat", "claws"):
        s = pal_block.index(skin + ": {")
        e = pal_block.index("}", s)
        palettes[skin] = dict(re.findall(r'"(.)": "(#[0-9a-fA-F]{6})"',
                                          pal_block[s:e]))

    # per-skin frame rows
    block = src[src.index("FRAME_ROWS"):]
    rows_by_skin = {}
    for skin in ("cat", "claws"):
        s = block.index(skin + ": {")
        e = len(block)
        for other in ("cat", "claws"):
            if other == skin:
                continue
            j = block.find("\n  " + other + ": {", s + 1)
            if j != -1 and j < e:
                e = j
        body = block[s:e]
        states = re.findall(r"^    (\w+): \[", body, re.M)
        frames = {}
        for i, st in enumerate(states):
            start = body.index(f"{st}: [")
            stop = len(body)
            for other in states[i + 1:]:
                j = body.find(f"\n    {other}: [", start + 1)
                if j != -1 and j < stop:
                    stop = j
            rows = re.findall(r'"([.0-9a-zA-Z]+)"', body[start:stop])
            frames[st] = [rows[k:k + height] for k in range(0, len(rows), height)]
        rows_by_skin[skin] = frames
    return palettes, rows_by_skin, width, height


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
    palettes, skins_frames, width, height = parse()
    nf = 8
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
    except Exception:
        f = ImageFont.load_default()

    tw, th = width * SCALE, height * SCALE
    for skin, frames in skins_frames.items():
        states = list(frames.keys())
        # contact sheet
        sheet = Image.new("RGB", (PAD + (tw + PAD) * nf + PAD,
                                   PAD + (LABEL_H + th + PAD) * len(states)), BG)
        d = ImageDraw.Draw(sheet)
        for si, st in enumerate(states):
            y0 = PAD + si * (LABEL_H + th + PAD)
            d.text((PAD, y0), st, fill=(180, 170, 210), font=f)
            for fi in range(nf):
                sheet.paste(tile(palettes[skin], frames[st][fi]),
                           (PAD + fi * (tw + PAD), y0 + LABEL_H))
        out_png = os.path.join(outdir, f"petsy-frames-{skin}.png")
        sheet.save(out_png)
        print("sheet:", out_png, sheet.size)

        # gif: cycle all states, 2 loops each
        fps_ms = 125
        gif_frames = []
        for st in states:
            for _rep in range(2):
                for fi in range(nf):
                    g = Image.new("RGB", (tw + 2 * PAD, th + LABEL_H + 2 * PAD), BG)
                    gd = ImageDraw.Draw(g)
                    gd.text((PAD, PAD), f"{skin} · {st} {fi + 1}/{nf}",
                          fill=(180, 170, 210), font=f)
                    g.paste(tile(palettes[skin], frames[st][fi]),
                          (PAD, PAD + LABEL_H))
                    gif_frames.append(g.convert("P", palette=Image.Palette.ADAPTIVE,
                                               colors=256))
        out_gif = os.path.join(outdir, f"petsy-demo-{skin}.gif")
        gif_frames[0].save(out_gif, save_all=True,
                           append_images=gif_frames[1:],
                           duration=fps_ms, loop=0)
        print("gif:", out_gif)


if __name__ == "__main__":
    main()
