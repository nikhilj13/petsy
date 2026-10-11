# Petsy — pastel pixel buddy for OpenCode TUI

A cute, super-lightweight soot-sprite avatar that sits above the composer (top-right by default)
and shows what the agent is doing.

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
- `src/avatar/frames.ts` — 7 states × 2 pixel maps (20×24), 8-bit palette, pastel purple `#C8B6FF`
- `src/avatar/pixel.tsx` — pairs pixel rows into half-block (`▀`/`▄`) spans: 20×24 art in a 20×12 footprint
- `src/avatar/status.ts` — tool-name → state mapping

## Perf notes

- ~4KB of pixel-map strings + 15-color palette, zero image/rig deps
- ~50 half-block `<span>` segments per frame, re-rendered at most 5×/s while busy
- One `setInterval` per visible composer, cleared on unmount
- Idle blinks every ~3s; `done`/`error` are static then revert
- Respects `animations: false`

## V2 ideas

- `color` option for the body
- `position` full config + `size: compact | full`
- More props (branch, model badge)
