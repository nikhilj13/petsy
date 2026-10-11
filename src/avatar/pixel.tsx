import { For } from "solid-js"
import { FRAMES, PALETTE } from "./frames.js"
import type { AgentStatus } from "./status.js"

// 16x16 pixel maps render as 16 cols x 8 rows: each terminal cell shows two
// vertical pixels via half-blocks ("▀" = top pixel, "▄" = bottom pixel),
// which doubles detail while shrinking the sprite footprint.
export interface CellRun {
  readonly fg: string | null
  readonly bg: string | null
  readonly text: string
}

interface Cell {
  readonly fg: string | null
  readonly bg: string | null
  readonly ch: string
}

function paletteOf(ch: string): string | null {
  if (ch === ".") return null
  return PALETTE[ch] ?? null
}

function cellFor(top: string, bottom: string): Cell {
  const t = paletteOf(top)
  const b = paletteOf(bottom)
  if (t && b) return { fg: t, bg: b, ch: "▀" }
  if (t) return { fg: t, bg: null, ch: "▀" }
  if (b) return { fg: b, bg: null, ch: "▄" }
  return { fg: null, bg: null, ch: " " }
}

function sameCell(a: Cell, b: Cell): boolean {
  return a.fg === b.fg && a.bg === b.bg && a.ch === b.ch
}

/** Merge one row-pair into runs of identical cells to keep span count low. */
export function encodeHalves(top: string, bottom: string): CellRun[] {
  const runs: CellRun[] = []
  let current: Cell | null = null
  let text = ""
  const flush = () => {
    if (current && text) runs.push({ fg: current.fg, bg: current.bg, text })
    text = ""
  }
  const width = Math.max(top.length, bottom.length)
  for (let i = 0; i < width; i++) {
    const cell = cellFor(top[i] ?? ".", bottom[i] ?? ".")
    if (!current || !sameCell(current, cell)) {
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
          <For each={encodeHalves(top, bottom)}>
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
