import { createSignal, onCleanup, onMount, Show } from "solid-js"
import { usePlugin } from "@opencode/plugin/tui"
import { FRAMES, STATUS_COLOR, frameFor } from "./frames.js"
import { isAnimatedStatus, toolNameToStatus, type AgentStatus, type AvatarPosition } from "./status.js"

export interface AvatarProps {
  readonly sessionID: string
  readonly position: AvatarPosition
  readonly fps: number
  readonly animations: boolean
  readonly doneTimeoutMs: number
  readonly enabled: boolean
}

type ToolContent = { readonly type: string; readonly name?: string; readonly id?: string }

function lastToolName(content: unknown): string | undefined {
  if (!Array.isArray(content)) return undefined
  for (let i = content.length - 1; i >= 0; i--) {
    const part = content[i] as ToolContent
    if (part && part.type === "tool" && typeof part.name === "string") return part.name
  }
  return undefined
}

function lookupToolName(
  getMessages: () => Array<{ type: string; content?: unknown }> | undefined,
  toolCallID: string,
): string | undefined {
  try {
    const messages = getMessages() ?? []
    for (let i = messages.length - 1; i >= 0; i--) {
      const msg = messages[i]
      if (msg.type !== "assistant" || !Array.isArray(msg.content)) continue
      for (const part of msg.content as ToolContent[]) {
        if (part?.type === "tool" && part.id === toolCallID && typeof part.name === "string") {
          return part.name
        }
      }
    }
    // Fallback: newest tool in newest assistant message.
    for (let i = messages.length - 1; i >= 0; i--) {
      const msg = messages[i]
      if (msg.type === "assistant") return lastToolName(msg.content)
    }
  } catch {
    // Message cache may not be synced yet — fall through to thinking.
  }
  return undefined
}

export function Avatar(props: AvatarProps) {
  const context = usePlugin()
  const [status, setStatus] = createSignal<AgentStatus>("idle")
  const [tick, setTick] = createSignal(0)

  let revertTimer: ReturnType<typeof setTimeout> | undefined
  let interval: ReturnType<typeof setInterval> | undefined
  let tickCount = 0

  const show = (next: AgentStatus) => {
    if (revertTimer) {
      clearTimeout(revertTimer)
      revertTimer = undefined
    }
    setStatus((prev) => {
      if (prev !== next) setTick(0)
      return next
    })
    if (next === "done" || next === "error") {
      revertTimer = setTimeout(() => setStatus("idle"), props.doneTimeoutMs)
    }
  }

  onMount(() => {
    try {
      const initial = context.data.session.status(props.sessionID)
      if (initial === "running") setStatus("thinking")
    } catch {
      // Session may not exist yet — stay idle.
    }

    const stopListening = context.data.listen(({ details }) => {
      const event = details as { type: string; data?: Record<string, unknown> }
      const data = event.data as { sessionID?: string } | undefined
      if (data && typeof data.sessionID === "string" && data.sessionID !== props.sessionID) return

      switch (event.type) {
        case "session.execution.started":
        case "session.text.started":
        case "session.reasoning.started":
          show("thinking")
          break
        case "session.tool.called": {
          const toolCallID = (data as { id?: string } | undefined)?.id
          const name = toolCallID
            ? lookupToolName(
                () => context.data.session.message.list(props.sessionID) as never,
                toolCallID,
              )
            : undefined
          show(toolNameToStatus(name))
          break
        }
        case "session.message.content.updated": {
          const content = (data as { content?: unknown } | undefined)?.content
          const name = lastToolName(content)
          if (name) show(toolNameToStatus(name))
          break
        }
        case "session.execution.succeeded":
          show("done")
          break
        case "session.execution.failed":
        case "session.step.failed":
        case "permission.asked":
          show("error")
          break
        case "session.execution.interrupted":
        case "session.idle":
          show("idle")
          break
        default:
          break
      }
    })

    if (props.animations && props.enabled) {
      const ms = Math.max(120, Math.floor(1000 / Math.max(1, props.fps)))
      interval = setInterval(() => {
        tickCount++
        const current = status()
        if (isAnimatedStatus(current)) {
          setTick((t) => (t + 1) % FRAMES[current].length)
        } else if (current === "idle" && tickCount % 15 === 0) {
          // Slow blink so idle stays calm and cheap.
          setTick((t) => (t + 1) % FRAMES.idle.length)
        }
      }, ms)
    }

    onCleanup(() => {
      stopListening()
      if (interval) clearInterval(interval)
      if (revertTimer) clearTimeout(revertTimer)
    })
  })

  return (
    <Show when={props.enabled && props.position !== "hidden"}>
      <box
        width="100%"
        flexDirection="column"
        alignItems={props.position === "top-left" ? "flex-start" : "flex-end"}
      >
        <text fg={STATUS_COLOR[status()]} selectable={false}>
          {frameFor(status(), tick())}
        </text>
      </box>
    </Show>
  )
}
