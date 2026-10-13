// Agent activity states shown by the Petsy avatar.
// Keep this union in sync with FRAMES keys in frames.ts.
export type AgentStatus =
  | "idle"
  | "thinking"
  | "idea"
  | "writing"
  | "researching"
  | "reading"
  | "complete"
  | "confused"
  | "error"

export type AvatarPosition = "top-right" | "top-left" | "hidden"

export interface PetsyOptions {
  /** Where to render above the composer. V1 supports top-right (default). */
  position?: AvatarPosition
  /** Frames per second for busy states. Kept low to stay lightweight. */
  fps?: number
  /** When false, render a static frame (also honors reduced motion). */
  animations?: boolean
  /** Ms to show done/error before returning to idle. Default 3000. */
  doneTimeoutMs?: number
  /** Render nothing at all. Useful for tests / minimal terminals. */
  enabled?: boolean
  /** Ms between idle blinks. Default 3000. */
  blinkEveryMs?: number
  /** How long the shut-eye frame shows per blink. Default 500. */
  blinkHoldMs?: number
}

const WEB_TOOLS = [
  "websearch",
  "webfetch",
  "web_search",
  "browser",
  "tavily",
  "fetch",
  "curl",
  "codesearch",
]

const READ_TOOLS = [
  "read",
  "glob",
  "grep",
  "list",
  "ls",
  "lsp",
  "diagnostics",
  "symbol",
  "codesearch",
]

const WRITE_TOOLS = [
  "edit",
  "write",
  "patch",
  "apply",
  "bash",
  "shell",
  "exec",
  "todo",
  "task",
]

function includesAny(name: string, needles: string[]): boolean {
  return needles.some((n) => name.includes(n))
}

/** Map an OpenCode tool name (e.g. "read", "webfetch") to an avatar state. */
export function toolNameToStatus(toolName: string | undefined | null): AgentStatus {
  if (!toolName) return "thinking"
  const name = toolName.toLowerCase()
  if (includesAny(name, WEB_TOOLS)) return "researching"
  if (includesAny(name, READ_TOOLS)) return "reading"
  if (includesAny(name, WRITE_TOOLS)) return "writing"
  return "thinking"
}

/** States that animate every frame vs. slow blink (idle only). */
export function isAnimatedStatus(status: AgentStatus): boolean {
  return status !== "idle"
}
