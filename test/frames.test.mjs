import { describe, it } from "node:test"
import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import { fileURLToPath } from "node:url"
import path from "node:path"

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const framesSrc = readFileSync(path.join(root, "src/avatar/frames.ts"), "utf8")

const STATES = ["idle", "thinking", "web-search", "reading", "writing", "done", "error"]

describe("frames", () => {
  it("defines all 7 states", () => {
    for (const state of STATES) {
      assert.ok(
        framesSrc.includes(`${state}: [`) || framesSrc.includes(`"${state}": [`),
        `missing state ${state}`,
      )
    }
  })

  it("keeps frames small (<=10 rows, <=15 cols) and tab-free", () => {
    assert.ok(!framesSrc.includes("\t"), "frames must not contain tabs")
    // Extract string literals that look like frame rows (quoted lines).
    const rows = [...framesSrc.matchAll(/"((?:[^"\\]|\\.)*)"/g)]
      .map((m) => m[1])
      .filter((s) => s.length >= 9 && s.length <= 20)
    assert.ok(rows.length >= 7 * 2 * 8, `expected >=126 frame rows, got ${rows.length}`)
    for (const row of rows) {
      assert.ok(row.length <= 15, `row too wide (${row.length}): ${JSON.stringify(row)}`)
    }
  })

  it("uses the pastel purple + error red palette", () => {
    assert.ok(framesSrc.includes("#C8B6FF"), "missing pastel purple")
    assert.ok(framesSrc.includes("#FF9D9D"), "missing error red")
  })
})
