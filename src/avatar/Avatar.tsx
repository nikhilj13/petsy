import { createSignal, onCleanup, onMount, Show } from "solid-js"
import { usePlugin } from "@opencode/plugin/tui"
import { DEFAULT_SKIN, FRAMES, type Skin } from "./frames.js"
import { PixelSprite } from "./pixel.js"
import { isAnimatedStatus, toolNameToStatus, type AgentStatus, type AvatarPosition } from "./status.js"

export interface AvatarProps {
  readonly sessionID: string
  readonly position: AvatarPosition
  readonly fps: number
  readonly animations: boolean
  /** Sprite skin: "cat" or "claws". */
  readonly skin: Skin
  readonly doneTimeoutMs: number
  readonly enabled: boolean
  /** Ms between idle blinks. Default 3000. */
  readonly blinkEveryMs: number
  /** How long the shut-eye frame shows per blink. Default 500. */
  readonly blinkHoldMs: number
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
  // Idle blink state machine: eyes stay open, then shut briefly.
  let idleTicks = 0
  let blinkLeft = 0
  // True once a tool has run in the current execution (for the idea moment).
  let toolsRanThisTurn = false
  let ideaTimer: ReturnType<typeof setTimeout> | undefined

  const clearIdeaTimer = () => {
    if (ideaTimer) {
      clearTimeout(ideaTimer)
      ideaTimer = undefined
    }
  }

  const show = (next: AgentStatus) => {
    if (revertTimer) {
      clearTimeout(revertTimer)
      revertTimer = undefined
    }
    if (next !== "idea") clearIdeaTimer()
    setStatus((prev) => {
      if (prev !== next) setTick(0)
      return next
    })
    if (next === "complete" || next === "error") {
      revertTimer = setTimeout(() => setStatus("idle"), props.doneTimeoutMs)
    }
    // Confused is sticky until the next event (it needs the user's attention).
  }

  /** Flash the lightbulb when text follows tool findings, then settle. */
  const showIdea = () => {
    show("idea")
    clearIdeaTimer()
    ideaTimer = setTimeout(() => {
      if (status() === "idea") show("thinking")
    }, 2500)
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
          toolsRanThisTurn = false
          show("thinking")
          break
        case "session.text.started":
        case "session.reasoning.started": {
          const current = status()
          if (
            toolsRanThisTurn &&
            (current === "researching" || current === "reading" || current === "writing")
          ) {
            // Findings just landed — flash the "new idea" bulb, then settle.
            showIdea()
          } else {
            show("thinking")
          }
          break
        }
        case "session.tool.called": {
          const toolCallID = (data as { id?: string } | undefined)?.id
          const name = toolCallID
            ? lookupToolName(
                () => context.data.session.message.list(props.sessionID) as never,
                toolCallID,
              )
            : undefined
          toolsRanThisTurn = true
          show(toolNameToStatus(name))
          break
        }
        case "session.message.content.updated": {
          const content = (data as { content?: unknown } | undefined)?.content
          const name = lastToolName(content)
          if (name) {
            toolsRanThisTurn = true
            show(toolNameToStatus(name))
          }
          break
        }
        case "session.execution.succeeded":
          show("complete")
          break
        case "session.execution.failed":
        case "session.step.failed":
          show("error")
          break
        case "permission.asked":
          show("confused")
          break
        case "permission.replied":
          show("thinking")
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
      const blinkEveryTicks = Math.max(1, Math.round(props.blinkEveryMs / ms))
      const blinkHoldTicks = Math.max(1, Math.round(props.blinkHoldMs / ms))
      const skinFrames = FRAMES[props.skin ?? DEFAULT_SKIN]
      const blinkFrame = skinFrames.idle.length - 1 // last idle frame = shut eyes
      interval = setInterval(() => {
        const current = status()
        if (isAnimatedStatus(current)) {
          setTick((t) => (t + 1) % skinFrames[current].length)
          idleTicks = 0
          blinkLeft = 0
        } else if (current === "idle") {
          if (blinkLeft > 0) {
            // Shut-eye hold: count down, then reopen.
            blinkLeft--
            if (blinkLeft === 0) setTick(0)
          } else {
            idleTicks++
            if (idleTicks >= blinkEveryTicks) {
              idleTicks = 0
              blinkLeft = blinkHoldTicks
              setTick(blinkFrame)
            }
          }
        }
      }, ms)
    }

    onCleanup(() => {
      stopListening()
      if (interval) clearInterval(interval)
      if (revertTimer) clearTimeout(revertTimer)
      clearIdeaTimer()
    })
  })

  return (
    <Show when={props.enabled && props.position !== "hidden"}>
      <box
        width="100%"
        flexDirection="column"
        alignItems={props.position === "top-left" ? "flex-start" : "flex-end"}
      >
        <PixelSprite status={status()} tick={tick()} skin={props.skin} />
      </box>
    </Show>
  )
}
