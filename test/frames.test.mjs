import { describe, it } from "node:test"
import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import { fileURLToPath } from "node:url"
import path from "node:path"

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const framesSrc = readFileSync(path.join(root, "src/avatar/frames.ts"), "utf8")

const STATES = [
  "idle",
  "thinking",
  "idea",
  "writing",
  "researching",
  "reading",
  "complete",
  "confused",
  "error",
]
const HEX_RE = /^#[0-9a-f]{6}$/
const WIDTH = 24
const HEIGHT = 30
const NF = 8

function framesFor(state) {
  const block = framesSrc.slice(framesSrc.indexOf("FRAME_ROWS"))
  const start = block.indexOf(`${state}: [`)
  assert.ok(start !== -1, `missing state ${state}`)
  let end = block.length
  for (const other of STATES) {
    if (other === state) continue
    const j = block.indexOf(`\n  ${other}: [`, start + 1)
    if (j !== -1 && j < end) end = j
  }
  return [...block.slice(start, end).matchAll(/"([.0-9a-zA-Z]+)"/g)].map((m) => m[1])
}

describe("frames", () => {
  it("declares 24x30 sprites with 8 frames per state", () => {
    assert.match(framesSrc, /export const SPRITE_WIDTH = 24/)
    assert.match(framesSrc, /export const SPRITE_HEIGHT = 30/)
    assert.match(framesSrc, /export const FRAMES_PER_STATE = 8/)
  })

  it("defines all 9 states with 8 frames of 30 rows", () => {
    for (const state of STATES) {
      const rows = framesFor(state)
      assert.equal(rows.length, NF * HEIGHT, `${state}: expected ${NF * HEIGHT} rows, got ${rows.length}`)
    }
  })

  it("keeps every row exactly 24 chars of palette chars", () => {
    const paletteChars = new Set([...framesSrc.matchAll(/"(.)": /g)].map((m) => m[1]))
    paletteChars.add(".") // transparent is implicit (absent from PALETTE map)
    for (const state of STATES) {
      for (const [i, row] of framesFor(state).entries()) {
        assert.equal(row.length, WIDTH, `${state} row ${i}: width ${row.length}`)
        for (const ch of row) {
          assert.ok(paletteChars.has(ch), `${state} row ${i}: unknown palette char ${JSON.stringify(ch)}`)
        }
      }
    }
  })

  it("uses the pastel purple + error red palette", () => {
    assert.ok(framesSrc.includes("#C8B6FF"), "missing pastel purple")
    assert.ok(framesSrc.includes("#E06C75"), "missing error red")
  })

  it("expands palette rows to truecolor FRAMES", () => {
    assert.match(framesSrc, /export const FRAMES: Record<AgentStatus, PixelFrame\[\]>/)
    assert.match(framesSrc, /PALETTE\[ch\] \?\? null/)
  })

  it("has no tabs in art", () => {
    assert.ok(!framesSrc.includes("\t"), "frames must not contain tabs")
  })
})
