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

const TOKEN_RE = /"(#[0-9a-fA-F]{6})"|null/g

function cellsFor(state) {
  const tokens = [...blockFor(state).matchAll(TOKEN_RE)].map((m) =>
    m[1] ? m[1].toLowerCase() : null,
  )
  return tokens
}

describe("frames", () => {
  it("defines all 9 states with 2 frames of 20 rows (16px wide)", () => {
    for (const state of STATES) {
      const tokens = cellsFor(state)
      assert.equal(tokens.length, 2 * 20 * 16, `${state}: expected 640 cells, got ${tokens.length}`)
    }
  })

  it("keeps every row rectangular (16px) with hex colors or transparency", () => {
    for (const state of STATES) {
      const tokens = cellsFor(state)
      for (let r = 0; r < tokens.length; r += 16) {
        const row = tokens.slice(r, r + 16)
        assert.equal(row.length, 16, `${state}: bad width at row ${r / 16}`)
        for (const cell of row) {
          assert.ok(
            cell === null || HEX_RE.test(cell),
            `${state}: bad cell ${JSON.stringify(cell)}`,
          )
        }
      }
    }
  })

  it("uses the pastel purple + error red palette", () => {
    assert.ok(framesSrc.includes("#C8B6FF"), "missing pastel purple")
    assert.ok(framesSrc.includes("#E06C75"), "missing error red")
  })

  it("has no tabs in art", () => {
    assert.ok(!framesSrc.includes("\t"), "frames must not contain tabs")
  })
})
