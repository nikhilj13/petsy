# Petsy — pastel pixel buddy for OpenCode TUI

A cute, super-lightweight soot-sprite avatar that stands on the input bar
(top-right by default) and shows what the agent is doing.
It renders in-flow directly above the composer, right-aligned.

States: `idle` `thinking` `idea` `writing` `researching` `reading` `complete` `confused` `error`.
`done` / `error` auto-revert to `idle` after 3s.

## Install (local dev)

```jsonc // ~/.config/opencode/cli.json
{
  "plugins": [
    {
      "package": "/absolute/path/to/petsy",
      "options": {
        "position": "top-right", // top-right | top-left | hidden (V1)
        "fps": 5, // 1-12, default 5. Busy states only; idle blinks on its own timer.
        "animations": true, // false = static frame
        "doneTimeoutMs": 3000,
        "blinkEveryMs": 3000, // ms between idle blinks
        "blinkHoldMs": 500, // how long the shut-eye shows per blink
        "enabled": true
      }
    }
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
- `src/avatar/Avatar.tsx` — Solid component: event → state mapper, 5fps timer only while busy
- `src/avatar/frames.ts` — 9 states × 2 truecolor maps (16×20, exact-half downsample of 32×40 native sources with hand-tuned faces/props, `null` = transparent), 8-bit palette kept for hand-drawn props + brand reference
- `src/avatar/pixel.tsx` — pairs pixel rows into quadrant-block spans (2×2 px per cell): 24×24 art in a 12×12 footprint
- `src/avatar/status.ts` — tool-name → state mapping

## Perf notes

- ~53KB of truecolor pixel data (exact RGB, native sources + tuned compact set, zero image/rig deps)
- ~100 quadrant `<span>` segments per frame, re-rendered at most 5×/s while busy
- One `setInterval` per visible composer, cleared on unmount
- Idle blinks every ~3s; `done`/`error` are static then revert
- Respects `animations: false`

## V2 ideas

- `color` option for the body
- `position` full config + `size: compact | full`
- More props (branch, model badge)
