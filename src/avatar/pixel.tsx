import { For } from "solid-js"
import { FRAMES, PALETTE } from "./frames.js"
import type { AgentStatus } from "./status.js"

// One pixel renders as two full blocks, which reads as roughly square
// in most terminals and gives the chunky 8-bit look.
const PIXEL = "██"
const EMPTY = "  "

export interface PixelRun {
  readonly color: string | null
  readonly text: string
}

/** Run-length encode one pixel row. Transparent runs become plain spaces. */
export function encodeRow(row: string): PixelRun[] {
  const runs: PixelRun[] = []
  let current: string | null = null
  let count = 0
  const flush = () => {
    if (count === 0) return
    runs.push(
      current === null
        ? { color: null, text: EMPTY.repeat(count) }
        : { color: PALETTE[current], text: PIXEL.repeat(count) },
    )
    count = 0
  }
  for (const ch of row) {
    const key = ch === "." ? null : ch
    if (key !== current) {
      flush()
      current = key
    }
    count++
  }
  flush()
  return runs
}

export function PixelSprite(props: { status: AgentStatus; tick: number }) {
  const rows = () => FRAMES[props.status][props.tick % FRAMES[props.status].length]
  return (
    <For each={rows()}>
      {(row) => (
        <text selectable={false}>
          <For each={encodeRow(row)}>
            {(run) => (run.color ? <PixelRun color={run.color} text={run.text} /> : run.text)}
          </For>
        </text>
      )}
    </For>
  )
}

// The Solid reconciler only applies `style` (not direct props) on text nodes
// like <span>, and the published SpanProps type omits it — so spread props to
// reach the runtime-supported `style.fg` path without a type error.
function PixelRun(props: { color: string; text: string }) {
  return <span {...{ style: { fg: props.color } }}>{props.text}</span>
}
