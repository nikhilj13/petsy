import type { AgentStatus } from "./status.js"

// V1 palette: pastel purple body for everything, soft red for errors.
// V2 will make the body color configurable.
export const PASTEL_PURPLE = "#C8B6FF"
export const ERROR_RED = "#FF9D9D"

export const STATUS_COLOR: Record<AgentStatus, string> = {
  idle: PASTEL_PURPLE,
  thinking: PASTEL_PURPLE,
  "web-search": PASTEL_PURPLE,
  reading: PASTEL_PURPLE,
  writing: PASTEL_PURPLE,
  done: PASTEL_PURPLE,
  error: ERROR_RED,
}

// Soot-sprite inspired frames. Each state has 2 lightweight frames.
// Keep <= 10 rows x <= 15 cols so the composer layout never jumps much.
// Plain ASCII + a few widely-supported glyphs (★ ○ / [ ] ^ x) only.
export const FRAMES: Record<AgentStatus, string[][]> = {
  idle: [
    [
      "     ★      ",
      "    ★★★     ",
      "    | |     ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** O   O **",
      " ***********",
      "  _/     \\_ ",
    ],
    [
      "     ★      ",
      "    ★★★     ",
      "    | |     ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** -   - **",
      " ***********",
      "  _/     \\_ ",
    ],
  ],
  thinking: [
    [
      "   .        ",
      "   ...      ",
      "            ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** O   O **",
      " ***********",
      "  _/     \\_ ",
    ],
    [
      "            ",
      "   ....     ",
      "            ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** O   O **",
      " ***********",
      "  _/     \\_ ",
    ],
  ],
  "web-search": [
    [
      "   (o)  o/   ",
      "   (-)  /    ",
      "            ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** O   O **",
      " ***********",
      "  _/     \\_ ",
    ],
    [
      "   (o)  /o   ",
      "   (-)  /    ",
      "            ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** O   O **",
      " ***********",
      "  _/     \\_ ",
    ],
  ],
  reading: [
    [
      "   [_ _]     ",
      "   [___]     ",
      "    | |     ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** O   O **",
      " ***********",
      "  _/     \\_ ",
    ],
    [
      "   [_^_]     ",
      "   [___]     ",
      "    | |     ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** O   O **",
      " ***********",
      "  _/     \\_ ",
    ],
  ],
  writing: [
    [
      "     />  *   ",
      "     ||      ",
      "            ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** O   O **",
      " ***********",
      "  _/     \\_ ",
    ],
    [
      "     />      ",
      "     ||  .   ",
      "            ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** O   O **",
      " ***********",
      "  _/     \\_ ",
    ],
  ],
  done: [
    [
      "     ★      ",
      "    ★★★     ",
      "    | |     ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** ^   ^ **",
      " ***********",
      "   _/ \\_    ",
    ],
    [
      "    ★ ★     ",
      "    ★★★     ",
      "    | |     ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** ^   ^ **",
      " ***********",
      "   _/ \\_    ",
    ],
  ],
  error: [
    [
      "             ",
      "    ! !      ",
      "            ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      " ** x   x **",
      " ***********",
      "  _/     \\_ ",
    ],
    [
      "             ",
      "    ! !      ",
      "            ",
      "    . * .   ",
      "   * *** *  ",
      "  ********* ",
      "  ** x   x **",
      "  ***********",
      "   _/     \\_ ",
    ],
  ],
}

export function frameFor(status: AgentStatus, tick: number): string {
  const frames = FRAMES[status]
  return frames[tick % frames.length].join("\n")
}
