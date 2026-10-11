import { describe, it } from "node:test"
import assert from "node:assert/strict"

// Mirrors src/avatar/status.ts mapping so `npm test` stays dependency-free.
// If you change the mapping, update both files.
function toolNameToStatus(toolName) {
  if (!toolName) return "thinking"
  const name = String(toolName).toLowerCase()
  const has = (...needles) => needles.some((n) => name.includes(n))
  if (has("websearch", "webfetch", "web_search", "browser", "tavily", "fetch", "curl", "codesearch"))
    return "researching"
  if (has("read", "glob", "grep", "list", "ls", "lsp", "diagnostics", "symbol", "codesearch"))
    return "reading"
  if (has("edit", "write", "patch", "apply", "bash", "shell", "exec", "todo", "task")) return "writing"
  return "thinking"
}

describe("toolNameToStatus", () => {
  it("maps web tools to researching", () => {
    assert.equal(toolNameToStatus("websearch"), "researching")
    assert.equal(toolNameToStatus("webfetch"), "researching")
  })
  it("maps read tools to reading", () => {
    assert.equal(toolNameToStatus("read"), "reading")
    assert.equal(toolNameToStatus("grep"), "reading")
    assert.equal(toolNameToStatus("glob"), "reading")
  })
  it("maps write tools to writing", () => {
    assert.equal(toolNameToStatus("edit"), "writing")
    assert.equal(toolNameToStatus("bash"), "writing")
    assert.equal(toolNameToStatus("write"), "writing")
  })
  it("falls back to thinking", () => {
    assert.equal(toolNameToStatus(undefined), "thinking")
    assert.equal(toolNameToStatus("some_future_tool"), "thinking")
  })
})
