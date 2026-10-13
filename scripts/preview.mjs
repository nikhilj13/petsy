// Terminal preview for visual iteration — no OpenCode needed.
// Usage: node scripts/preview.mjs [state]  (default: all states, all frames)
// Renders the truecolor frames the TUI uses (truecolor ANSI, half-blocks).
import { readFileSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const src = readFileSync(path.join(root, "src/avatar/frames.ts"), "utf8")

const RESET = "\x1b[0m"
const STATES = ["idle", "thinking", "idea", "writing", "researching", "reading", "complete", "confused", "error"]

function hexToRgb(hex) {
  const m = hex.replace("#", "")
  return [parseInt(m.slice(0, 2), 16), parseInt(m.slice(2, 4), 16), parseInt(m.slice(4, 6), 16)]
}

// Parse palette: "ch": "#rrggbb"
const PALETTE = {}
for (const m of src.matchAll(/"(.)": "(#[0-9a-fA-F]{6})"/g)) PALETTE[m[1]] = m[2]

const width = parseInt(src.match(/export const SPRITE_WIDTH = (\d+)/)[1], 10)
const height = parseInt(src.match(/export const SPRITE_HEIGHT = (\d+)/)[1], 10)

/** All frames (as row-string arrays) for a state from FRAME_ROWS. */
function framesFor(state) {
  const rowsBlock = src.slice(src.indexOf("FRAME_ROWS"))
  const start = rowsBlock.indexOf(`${state}: [`)
  if (start === -1) return []
  let end = rowsBlock.length
  for (const other of STATES) {
    if (other === state) continue
    const j = rowsBlock.indexOf(`\n  ${other}: [`, start + 1)
    if (j !== -1 && j < end) end = j
  }
  const body = rowsBlock.slice(start, end)
  const rows = [...body.matchAll(/"([.0-9a-zA-Z]+)"/g)].map((m) => m[1])
  const frames = []
  for (let i = 0; i + height <= rows.length; i += height) frames.push(rows.slice(i, i + height))
  return frames
}

function fg(rgb) {
  return `38;2;${rgb[0]};${rgb[1]};${rgb[2]}`
}

function bg(rgb) {
  return `48;2;${rgb[0]};${rgb[1]};${rgb[2]}`
}

function cell(top, bottom) {
  const tc = top && top !== "." ? PALETTE[top] : null
  const bc = bottom && bottom !== "." ? PALETTE[bottom] : null
  const t = tc ? hexToRgb(tc) : null
  const b = bc ? hexToRgb(bc) : null
  if (t && b) return `\x1b[${fg(t)};${bg(b)}m▀${RESET}`
  if (t) return `\x1b[${fg(t)}m▀${RESET}`
  if (b) return `\x1b[${fg(b)}m▄${RESET}`
  return " "
}

const only = process.argv[2]
for (const state of STATES) {
  if (only && state !== only) continue
  const frames = framesFor(state)
  for (const [i, frame] of frames.entries()) {
    console.log(`--- ${state} frame ${i + 1}/${frames.length} ---`)
    for (let r = 0; r < height; r += 2) {
      let line = ""
      for (let c = 0; c < width; c++) line += cell(frame[r]?.[c] ?? ".", frame[r + 1]?.[c] ?? ".")
      console.log(line)
    }
    console.log()
  }
}
