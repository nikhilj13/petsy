// Terminal preview for visual iteration — no OpenCode needed.
// Usage: node scripts/preview.mjs [state]  (default: all states, both frames)
import { readFileSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const src = readFileSync(path.join(root, "src/avatar/frames.ts"), "utf8")

const RESET = "\x1b[0m"

function hexToAnsi(hex) {
  const m = hex.replace("#", "")
  const r = parseInt(m.slice(0, 2), 16)
  const g = parseInt(m.slice(2, 4), 16)
  const b = parseInt(m.slice(4, 6), 16)
  return `\x1b[38;2;${r};${g};${b}m`
}

function extractPalette() {
  const out = {}
  for (const m of src.matchAll(/^\s*([A-Za-z]):\s*"(#[0-9A-Fa-f]{6})"|^\s*([A-Za-z]):\s*[A-Z_]+/gm)) {
    // Handles `K: "#55506B"` entries; constant refs (P/R) resolved below.
    if (m[1] && m[2]) out[m[1]] = m[2]
  }
  const pastel = (src.match(/PASTEL_PURPLE\s*=\s*"(#[0-9A-Fa-f]{6})"/) ?? [])[1]
  const errRed = (src.match(/ERROR_RED\s*=\s*"(#[0-9A-Fa-f]{6})"/) ?? [])[1]
  if (pastel) out.P = pastel
  if (errRed) out.R = errRed
  return out
}

function extractFrames() {
  const states = ["idle", "thinking", "web-search", "reading", "writing", "done", "error"]
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
    // Pixel rows are exactly 13 chars of palette keys / dots.
    const rows = [...block.matchAll(/"([.A-Za-z]{13})"/g)].map((m) => m[1])
    out[state] = [rows.slice(0, 10), rows.slice(10, 20)]
  }
  return out
}

function renderRow(row, palette) {
  let out = ""
  let current = null
  let buf = ""
  const flush = () => {
    if (!buf) return
    out += current ? `${hexToAnsi(palette[current])}${"██".repeat(buf.length)}${RESET}` : "  ".repeat(buf.length)
    buf = ""
  }
  for (const ch of row) {
    const key = ch === "." ? null : ch
    if (key !== current) {
      flush()
      current = key
    }
    buf += ch
  }
  flush()
  return out
}

const only = process.argv[2]
const palette = extractPalette()
const frames = extractFrames()
for (const [state, pair] of Object.entries(frames)) {
  if (only && state !== only) continue
  pair.forEach((frame, i) => {
    console.log(`--- ${state} frame ${i + 1} ---`)
    for (const row of frame) console.log(renderRow(row, palette))
    console.log()
  })
}
