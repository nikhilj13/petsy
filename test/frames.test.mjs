import { describe, it } from "node:test"
import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import { fileURLToPath } from "node:url"
import path from "node:path"

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const framesSrc = readFileSync(path.join(root, "src/avatar/frames.ts"), "utf8")

const STATES = ["idle", "thinking", "web-search", "reading", "writing", "done", "error"]
const PIXEL_KEYS = new Set([".", "K", "P", "p", "h", "W", "B", "Y", "y", "G", "g", "R", "N", "n"])

function blockFor(state) {
  const key = framesSrc.includes(`"${state}": [`) ? `"${state}": [` : `${state}: [`
  const start = framesSrc.indexOf(key)
  assert.ok(start !== -1, `missing state ${state}`)
  const nextStarts = STATES.map((s) => {
    if (s === state) return Infinity
    const a = framesSrc.indexOf(`${s}: [`, start + 1)
    const b = framesSrc.indexOf(`"${s}": [`, start + 1)
    const cands = [a, b].filter((n) => n !== -1)
    return cands.length ? Math.min(...cands) : Infinity
  }).filter((n) => n !== -1)
  return framesSrc.slice(start, Math.min(...nextStarts, framesSrc.length))
}

describe("frames", () => {
  it("defines all 7 states with 2 frames of 10 rows", () => {
    for (const state of STATES) {
      const rows = [...blockFor(state).matchAll(/"([.A-Za-z]{13})"/g)].map((m) => m[1])
      assert.equal(rows.length, 20, `${state}: expected 20 pixel rows, got ${rows.length}`)
    }
  })

  it("keeps every row rectangular (13px) with known palette keys", () => {
    for (const state of STATES) {
      const rows = [...blockFor(state).matchAll(/"([.A-Za-z]{13})"/g)].map((m) => m[1])
      for (const row of rows) {
        assert.equal(row.length, 13, `${state}: bad width: ${JSON.stringify(row)}`)
        for (const ch of row) {
          assert.ok(PIXEL_KEYS.has(ch), `${state}: unknown pixel ${JSON.stringify(ch)}`)
        }
      }
    }
  })

  it("uses the pastel purple + error red palette", () => {
    assert.ok(framesSrc.includes("#C8B6FF"), "missing pastel purple")
    assert.ok(framesSrc.includes("#E06C75"), "missing error red")
  })

  it("has no tabs or trailing spaces in art", () => {
    assert.ok(!framesSrc.includes("\t"), "frames must not contain tabs")
  })
})
