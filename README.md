# Petsy — pixel buddy for OpenCode TUI

A cute, super-lightweight pixel avatar that stands on the input bar
(top-right by default) and shows what the agent is doing.
Two switchable skins via the `skin` option: `cat` (orange tabby) and
`claws` (classic space invader).
It renders in-flow directly above the composer, right-aligned.

States: `idle` `thinking` `idea` `writing` `researching` `reading` `complete` `confused` `error`.
`done` / `error` auto-revert to `idle` after 3s.

## Art pipeline

Sprite art is generated, not hand-maintained:

```sh
python3 tools/generate_frames.py    # regenerates src/avatar/frames.ts
python3 tools/render_preview.py     # preview sheets + GIFs, one per skin
```

`tools/generate_frames.py` draws each skin in layers (cat: rounded fur
silhouette, ears, striped tail, glossy eyes; claws: bitmap-stamped invader
with two-frame leg shuffle) plus shared per-state props and particles, and
emits compact palette-indexed frames per skin. Edit the generator, not
`frames.ts`.

## Install (local dev)

```jsonc // ~/.config/opencode/opencode.jsonc
{
  // OpenCode passes plugin options as the second tuple element.
  "plugin": [
    [
      "/absolute/path/to/petsy", // absolute path to your local clone
      {
        "skin": "cat", // cat | claws — the orange tabby or the classic space invader
        "position": "top-right", // top-right | top-left | hidden (V1)
        "fps": 8, // 1-12, default 8. Busy states only; idle blinks on its own timer.
        "animations": true, // false = static frame
        "doneTimeoutMs": 3000,
        "blinkEveryMs": 3000, // ms between idle blinks
        "blinkHoldMs": 500, // how long the shut-eye shows per blink
        "enabled": true
      }
    ]
  ]
}
```

Then run `opencode` from any project. The buddy appears above the input box.

## Preview without OpenCode

```sh
npm test
node scripts/preview.mjs
node scripts/preview.mjs researching
```

## Layout

- `src/index.ts` — server stub (no-op, required for plugin loading)
- `src/tui.tsx` — TUI entry: registers `session.composer.top` slot (right-aligned)
- `src/avatar/Avatar.tsx` — Solid component: event → state mapper, 8fps timer only while busy
- `src/avatar/frames.ts` — generated (see Art pipeline): 9 states × 8 truecolor frames, 24×30 native pixels, palette-indexed rows expanded once at load
- `src/avatar/pixel.tsx` — pairs pixel rows into half-block spans (2 px per cell): 24×30 art in a 24×15 footprint
- `src/avatar/status.ts` — tool-name → state mapping
- `tools/generate_frames.py` — sprite art source of truth (layered procedural drawing)
- `tools/render_preview.py` — PNG contact sheet + animated GIF previews

## Perf notes

- ~55KB of palette-indexed frame data (720 chars/frame × 72 frames), zero image/rig deps
- ~100 half-block `<span>` segments per frame, re-rendered at most 8×/s while busy
- One `setInterval` per visible composer, cleared on unmount
- Idle blinks every ~3s (last idle frame = shut eyes); `done` reverts after 3s
- Respects `animations: false`

## V2 ideas

- `color` option for the body
- `position` full config + `size: compact | full`
- More props (branch, model badge)
