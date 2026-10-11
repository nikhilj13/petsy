// Terminal preview for visual iteration — no OpenCode needed.
// Usage: node scripts/preview.mjs [state]  (default: all states, both frames)
// Renders the same half-block encoding the TUI uses (truecolor ANSI).
import { readFileSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const src = readFileSync(path.join(root, "src/avatar/frames.ts"), "utf8")

const RESET = "\x1b[0m"

function hexToRgb(hex) {
  const m = hex.replace("#", "")
  return [parseInt(m.slice(0, 2), 16), parseInt(m.slice(2, 4), 16), parseInt(m.slice(4, 6), 16)]
}

function extractPalette() {
  const out = {}
  for (const m of src.matchAll(/^\s*([A-Za-z]):\s*"(#[0-9A-Fa-f]{6})"/gm)) {
    out[m[1]] = hexToRgb(m[2])
  }
  const pastel = (src.match(/PASTEL_PURPLE\s*=\s*"(#[0-9A-Fa-f]{6})"/) ?? [])[1]
  const errRed = (src.match(/ERROR_RED\s*=\s*"(#[0-9A-Fa-f]{6})"/) ?? [])[1]
  if (pastel) out.P = hexToRgb(pastel)
  if (errRed) out.R = hexToRgb(errRed)
  return out
}

function extractFrames() {
  const states = ["idle", "thinking", "idea", "writing", "researching", "reading", "complete", "confused", "error"]
  const out = {}
  for (const state of states) {
    const key = src.includes(`"${state}": [`) ? `"${state}": [` : `${state}: [`
    const start = src.indexOf(key)
    if (start === -1) continue
    const nextStarts = states
      .map((s) => {
        if (s === state) return Infinity
        const a = src.indexOf(`${s}: [`, start + 1)
        const b = src.indexOf(`"${s}": [`, start + 1)
        const cands = [a, b].filter((n) => n !== -1)
        return cands.length ? Math.min(...cands) : Infinity
      })
      .filter((n) => n !== -1)
    const end = Math.min(...nextStarts, src.length)
    const block = src.slice(start, end)
    const rows = [...block.matchAll(/"([.A-Za-z]{20})"/g)].map((m) => m[1])
    out[state] = [rows.slice(0, 24), rows.slice(24, 48)]
  }
  return out
}

function fg(rgb) {
  return `38;2;${rgb[0]};${rgb[1]};${rgb[2]}`
}

function bg(rgb) {
  return `48;2;${rgb[0]};${rgb[1]};${rgb[2]}`
}

function cell(top, bottom, palette) {
  const t = top === "." ? null : palette[top]
  const b = bottom === "." ? null : palette[bottom]
  if (t && b) return `\x1b[${fg(t)};${bg(b)}m▀${RESET}`
  if (t) return `\x1b[${fg(t)}m▀${RESET}`
  if (b) return `\x1b[${fg(b)}m▄${RESET}`
  return " "
}

const only = process.argv[2]
const palette = extractPalette()
const frames = extractFrames()
for (const [state, pair] of Object.entries(frames)) {
  if (only && state !== only) continue
  pair.forEach((frame, i) => {
    console.log(`--- ${state} frame ${i + 1} ---`)
    for (let r = 0; r < frame.length; r += 2) {
      let line = ""
      for (let c = 0; c < 20; c++) line += cell(frame[r][c], frame[r + 1][c], palette)
      console.log(line)
    }
    console.log()
  })
}
