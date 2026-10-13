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
const SKINS = ["cat", "claws"]
const WIDTH = 18
const HEIGHT = 22
const NF = 8

function skinBlock(skin) {
  const rowsBlock = framesSrc.slice(framesSrc.indexOf("FRAME_ROWS"))
  const s = rowsBlock.indexOf(`${skin}: {`)
  assert.ok(s !== -1, `missing skin ${skin} in FRAME_ROWS`)
  let end = rowsBlock.length
  for (const other of SKINS) {
    if (other === skin) continue
    const j = rowsBlock.indexOf(`\n  ${other}: {`, s + 1)
    if (j !== -1 && j < end) end = j
  }
  return rowsBlock.slice(s, end)
}

function framesFor(skin, state) {
  const block = skinBlock(skin)
  const start = block.indexOf(`${state}: [`)
  assert.ok(start !== -1, `missing state ${state} in skin ${skin}`)
  let end = block.length
  for (const other of STATES) {
    if (other === state) continue
    const j = block.indexOf(`\n    ${other}: [`, start + 1)
    if (j !== -1 && j < end) end = j
  }
  return [...block.slice(start, end).matchAll(/"([.0-9a-zA-Z]+)"/g)].map((m) => m[1])
}

function paletteFor(skin) {
  const palBlock = framesSrc.slice(framesSrc.indexOf("PALETTES"), framesSrc.indexOf("SPRITE_WIDTH"))
  const s = palBlock.indexOf(`${skin}: {`)
  assert.ok(s !== -1, `missing skin ${skin} in PALETTES`)
  const e = palBlock.indexOf("}", s)
  return new Map([...palBlock.slice(s, e).matchAll(/"(.)": "(#[0-9a-fA-F]{6})"/g)].map((m) => [m[1], m[2]]))
}

describe("frames", () => {
  it("declares cat|claws skins with cat as default", () => {
    assert.match(framesSrc, /export type Skin = "cat" \| "claws"/)
    assert.match(framesSrc, /export const DEFAULT_SKIN: Skin = "cat"/)
  })

  it("declares 18x22 sprites with 8 frames per state", () => {
    assert.match(framesSrc, /export const SPRITE_WIDTH = 18/)
    assert.match(framesSrc, /export const SPRITE_HEIGHT = 22/)
    assert.match(framesSrc, /export const FRAMES_PER_STATE = 8/)
  })

  it("defines all 9 states with 8 frames of 22 rows for every skin", () => {
    for (const skin of SKINS) {
      for (const state of STATES) {
        const rows = framesFor(skin, state)
        assert.equal(rows.length, NF * HEIGHT, `${skin}/${state}: expected ${NF * HEIGHT} rows, got ${rows.length}`)
      }
    }
  })

  it("keeps every row exactly 18 chars of palette chars", () => {
    for (const skin of SKINS) {
      const palette = paletteFor(skin)
      for (const state of STATES) {
        for (const [i, row] of framesFor(skin, state).entries()) {
          assert.equal(row.length, WIDTH, `${skin}/${state} row ${i}: width ${row.length}`)
          for (const ch of row) {
            // "." is transparent and intentionally absent from the palette map
            assert.ok(ch === "." || palette.has(ch), `${skin}/${state} row ${i}: unknown palette char ${JSON.stringify(ch)}`)
          }
        }
      }
    }
  })

  it("uses the cat orange + invader red-orange + error red palettes", () => {
    assert.equal(paletteFor("cat").get("3"), "#E89B3C")
    assert.equal(paletteFor("claws").get("3"), "#EF5D48")
    assert.ok(framesSrc.includes("#E06C75"), "missing error red")
  })

  it("expands palette rows to truecolor FRAMES per skin", () => {
    assert.match(framesSrc, /export const FRAMES: Record<Skin, Record<AgentStatus, PixelFrame\[\]>>/)
    assert.match(framesSrc, /PALETTES\[skin as Skin\]\[ch\] \?\? null/)
  })

  it("has no tabs in art", () => {
    assert.ok(!framesSrc.includes("\t"), "frames must not contain tabs")
  })
})
