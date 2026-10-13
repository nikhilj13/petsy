// Terminal preview for visual iteration — no OpenCode needed.
// Usage: node scripts/preview.mjs [state] [skin]   (skin: cat | claws | both)
// Renders the truecolor frames the TUI uses (truecolor ANSI, half-blocks).
import { readFileSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const src = readFileSync(path.join(root, "src/avatar/frames.ts"), "utf8")

const RESET = "\x1b[0m"
const STATES = ["idle", "thinking", "idea", "writing", "researching", "reading", "complete", "confused", "error"]
const SKINS = ["cat", "claws"]

function hexToRgb(hex) {
  const m = hex.replace("#", "")
  return [parseInt(m.slice(0, 2), 16), parseInt(m.slice(2, 4), 16), parseInt(m.slice(4, 6), 16)]
}

const width = parseInt(src.match(/export const SPRITE_WIDTH = (\d+)/)[1], 10)
const height = parseInt(src.match(/export const SPRITE_HEIGHT = (\d+)/)[1], 10)

/** Per-skin palette maps from PALETTES. */
function palettes() {
  const block = src.slice(src.indexOf("PALETTES"), src.indexOf("SPRITE_WIDTH"))
  const out = {}
  for (const skin of SKINS) {
    const s = block.indexOf(`${skin}: {`)
    const e = block.indexOf("}", s)
    const map = {}
    for (const m of block.slice(s, e).matchAll(/"(.)": "(#[0-9a-fA-F]{6})"/g)) map[m[1]] = m[2]
    out[skin] = map
  }
  return out
}

/** All frames (as row-string arrays) for skin+state from FRAME_ROWS. */
function framesFor(skin, state) {
  const rowsBlock = src.slice(src.indexOf("FRAME_ROWS"))
  const skinStarts = SKINS.map((s) => rowsBlock.indexOf(`${s}: {`))
  const s = skinStarts[SKINS.indexOf(skin)]
  if (s === -1) return []
  let end = rowsBlock.length
  for (const other of SKINS) {
    if (other === skin) continue
    const j = rowsBlock.indexOf(`\n  ${other}: {`, s + 1)
    if (j !== -1 && j < end) end = j
  }
  const body = rowsBlock.slice(s, end)
  const start = body.indexOf(`${state}: [`)
  if (start === -1) return []
  let stop = body.length
  for (const other of STATES) {
    if (other === state) continue
    const j = body.indexOf(`\n    ${other}: [`, start + 1)
    if (j !== -1 && j < stop) stop = j
  }
  const rows = [...body.slice(start, stop).matchAll(/"([.0-9a-zA-Z]+)"/g)].map((m) => m[1])
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

function cell(pal, top, bottom) {
  const tc = top && top !== "." ? pal[top] : null
  const bc = bottom && bottom !== "." ? pal[bottom] : null
  const t = tc ? hexToRgb(tc) : null
  const b = bc ? hexToRgb(bc) : null
  if (t && b) return `\x1b[${fg(t)};${bg(b)}m▀${RESET}`
  if (t) return `\x1b[${fg(t)}m▀${RESET}`
  if (b) return `\x1b[${fg(b)}m▄${RESET}`
  return " "
}

const PALETTES = palettes()
const only = process.argv[2]
const skinArg = process.argv[3] ?? "both"
for (const skin of SKINS) {
  if (skinArg !== "both" && skin !== skinArg) continue
  for (const state of STATES) {
    if (only && state !== only) continue
    const frames = framesFor(skin, state)
    for (const [i, frame] of frames.entries()) {
      console.log(`--- ${skin} · ${state} frame ${i + 1}/${frames.length} ---`)
      for (let r = 0; r < height; r += 2) {
        let line = ""
        for (let c = 0; c < width; c++) line += cell(PALETTES[skin], frame[r]?.[c] ?? ".", frame[r + 1]?.[c] ?? ".")
        console.log(line)
      }
      console.log()
    }
  }
}
