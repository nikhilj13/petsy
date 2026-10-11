// Terminal preview for visual iteration — no OpenCode needed.
// Usage: node scripts/preview.mjs [state]  (default: all states, both frames)
import { readFileSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const src = readFileSync(path.join(root, "src/avatar/frames.ts"), "utf8")

const PURPLE = "\x1b[38;2;200;182;255m"
const RED = "\x1b[38;2;255;157;157m"
const RESET = "\x1b[0m"

function extractFrames() {
  // Very small parser: find each `state: [` block and pull quoted rows in order.
  // Frames file format is stable (2 frames per state, 9 rows each).
  const states = ["idle", "thinking", "web-search", "reading", "writing", "done", "error"]
  const out = {}
  for (const state of states) {
    const start =
      src.indexOf(`${state}: [`) !== -1
        ? src.indexOf(`${state}: [`)
        : src.indexOf(`"${state}": [`)
    if (start === -1) continue
    // Find the next state block or end of FRAMES to bound the search.
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
    const rows = [...block.matchAll(/"((?:[^"\\]|\\.)*)"/g)]
      .map((m) => m[1].replace(/\\_/g, "_"))
      .filter((r) => r !== state)
    // First two quoted strings in block are not rows if short — filter to row-like.
    const frameRows = rows.filter((r) => r.length >= 9)
    out[state] = [frameRows.slice(0, 9), frameRows.slice(9, 18)]
  }
  return out
}

const only = process.argv[2]
const frames = extractFrames()
for (const [state, pair] of Object.entries(frames)) {
  if (only && state !== only) continue
  const color = state === "error" ? RED : PURPLE
  pair.forEach((frame, i) => {
    console.log(`${color}--- ${state} frame ${i + 1} ---${RESET}`)
    console.log(color + frame.join("\n") + RESET + "\n")
  })
}
