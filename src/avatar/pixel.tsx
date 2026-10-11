import { For } from "solid-js"
import { FRAMES, PALETTE } from "./frames.js"
import type { AgentStatus } from "./status.js"

// Quadrant-block rendering: each terminal cell shows a 2x2 pixel group,
// so 24x24 art fits in 12 cols x 12 rows — 4 pixels per cell instead of 2.
// One cell carries at most two colors (fg + bg); extra colors at busy
// junctions are dropped by fixed priority (first-seen wins).
export interface CellRun {
  readonly fg: string | null
  readonly bg: string | null
  readonly text: string
}

// Bit order: TL=1, TR=2, BL=4, BR=8.
const QUAD = [" ", "▘", "▝", "▀", "▖", "▌", "▞", "▛", "▗", "▚", "▐", "▜", "▄", "▙", "▟", "█"]
const BIT = [1, 2, 4, 8]

function pixelAt(row: string, x: number): string | null {
  const ch = x < row.length ? row[x] : "."
  if (ch === ".") return null
  return PALETTE[ch] ?? null
}

/** Encode one pair of pixel rows into quadrant cells (2px per cell). */
export function encodeQuads(top: string, bottom: string): CellRun[] {
  const runs: CellRun[] = []
  let current: { fg: string | null; bg: string | null; ch: string } | null = null
  let text = ""
  const flush = () => {
    if (current && text) runs.push({ fg: current.fg, bg: current.bg, text })
    text = ""
  }
  const width = Math.max(top.length, bottom.length)
  for (let x = 0; x < width; x += 2) {
    const px = [pixelAt(top, x), pixelAt(top, x + 1), pixelAt(bottom, x), pixelAt(bottom, x + 1)]
    const colors: string[] = []
    for (const c of px) {
      if (c !== null && !colors.includes(c)) colors.push(c)
    }
    let cell: { fg: string | null; bg: string | null; ch: string }
    if (colors.length === 0) {
      cell = { fg: null, bg: null, ch: " " }
    } else {
      const fg = colors[0]
      const rest = px.filter((c) => c !== null && c !== fg)
      const hasTransparent = px.some((c) => c === null)
      // Terminal cells can't show transparency over a bg color, so a cell
      // touching transparency drops its bg (minority pixels follow).
      const bg = !hasTransparent && rest.length > 0 ? (rest[0] as string) : null
      let mask = 0
      for (let i = 0; i < 4; i++) {
        if (px[i] === fg) mask |= BIT[i]
      }
      cell = { fg, bg, ch: QUAD[mask] }
    }
    if (!current || current.fg !== cell.fg || current.bg !== cell.bg || current.ch !== cell.ch) {
      flush()
      current = cell
    }
    text += cell.ch
  }
  flush()
  return runs
}

export function PixelSprite(props: { status: AgentStatus; tick: number }) {
  const pairs = () => {
    const frame = FRAMES[props.status][props.tick % FRAMES[props.status].length]
    const out: Array<readonly [string, string]> = []
    for (let i = 0; i < frame.length; i += 2) out.push([frame[i], frame[i + 1] ?? ""])
    return out
  }
  return (
    <For each={pairs()}>
      {([top, bottom]) => (
        <text selectable={false}>
          <For each={encodeQuads(top, bottom)}>
            {(run) =>
              run.fg || run.bg ? (
                <PixelRun fg={run.fg} bg={run.bg} text={run.text} />
              ) : (
                run.text
              )
            }
          </For>
        </text>
      )}
    </For>
  )
}

// The Solid reconciler only applies `style` (not direct props) on text nodes
// like <span>, and the published SpanProps type omits it — so spread props to
// reach the runtime-supported `style.fg`/`style.bg` path without a type error.
function PixelRun(props: { fg: string | null; bg: string | null; text: string }) {
  const style: Record<string, string> = {}
  if (props.fg) style.fg = props.fg
  if (props.bg) style.bg = props.bg
  return <span {...{ style }}>{props.text}</span>
}
