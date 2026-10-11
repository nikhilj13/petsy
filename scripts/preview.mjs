// Terminal preview for visual iteration — no OpenCode needed.
// Usage: node scripts/preview.mjs [state]  (default: all states, both frames)
// Renders the truecolor frames the TUI uses (truecolor ANSI).
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

function blockFor(state) {
  const key = src.includes(`"${state}": [`) ? `"${state}": [` : `${state}: [`
  const start = src.indexOf(key)
  if (start === -1) return ""
  let end = src.length
  for (const s of STATES) {
    if (s === state) continue
    for (const k of [`${s}: [`, `"${s}": [`]) {
      const i = src.indexOf(k, start + 1)
      if (i !== -1 && i < end) end = i
    }
  }
  return src.slice(start, end)
}

function framesFor(state, width, height) {
  const tokens = [...blockFor(state).matchAll(/"(#[0-9a-fA-F]{6})"|null/g)].map((m) =>
    m[1] ? m[1].toLowerCase() : null,
  )
  const rows = []
  for (let i = 0; i + width <= tokens.length; i += width) rows.push(tokens.slice(i, i + width))
  return [rows.slice(0, height), rows.slice(height, height * 2)]
}

function fg(rgb) {
  return `38;2;${rgb[0]};${rgb[1]};${rgb[2]}`
}

function bg(rgb) {
  return `48;2;${rgb[0]};${rgb[1]};${rgb[2]}`
}

function cell(top, bottom) {
  const t = top ? hexToRgb(top) : null
  const b = bottom ? hexToRgb(bottom) : null
  if (t && b) return `\x1b[${fg(t)};${bg(b)}m▀${RESET}`
  if (t) return `\x1b[${fg(t)}m▀${RESET}`
  if (b) return `\x1b[${fg(b)}m▄${RESET}`
  return " "
}

const only = process.argv[2]
const widthMatch = src.match(/export const SPRITE_WIDTH = (\d+)/)
const heightMatch = src.match(/export const SPRITE_HEIGHT = (\d+)/)
const width = widthMatch ? parseInt(widthMatch[1], 10) : 20
const height = heightMatch ? parseInt(heightMatch[1], 10) : 24
for (const state of STATES) {
  if (only && state !== only) continue
  for (const [i, frame] of framesFor(state, width, height).entries()) {
    console.log(`--- ${state} frame ${i + 1} ---`)
    for (let r = 0; r < frame.length; r += 2) {
      let line = ""
      for (let c = 0; c < width; c++) line += cell(frame[r][c], (frame[r + 1] ?? [])[c])
      console.log(line)
    }
    console.log()
  }
}
