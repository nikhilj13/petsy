import type { AgentStatus } from "./status.js"

// V1 palette. The body stays pastel purple (configurable color lands in V2).
export const PASTEL_PURPLE = "#C8B6FF"
export const ERROR_RED = "#E06C75"

// 8-bit palette: one char per pixel. "." is transparent (renders as spaces).
export const PALETTE: Record<string, string> = {
  K: "#55506B", // outline (dark muted purple-gray)
  P: PASTEL_PURPLE, // body
  p: "#9A86E8", // body shade
  h: "#E9E2FF", // highlight / sparkle
  W: "#FFFFFF", // eye white
  B: "#23232E", // pupil
  Y: "#FFD98A", // star / lens / pencil
  y: "#E8A94E", // star shade
  G: "#7EE2A8", // globe
  g: "#3FA46F", // globe shade
  R: ERROR_RED, // book / error marks / X eyes
  N: "#FFF6E3", // book pages
  n: "#D8C9A8", // book page shade
}

// Soot-sprite pixel maps: 13px wide x 10 rows per frame, 2 frames per state.
// Each pixel renders as two "██" blocks, so the sprite is ~26 cols wide.
// Fully static string data — no runtime cost beyond the span encoding.
export const SPRITE_WIDTH = 13
export const SPRITE_HEIGHT = 10

export const FRAMES: Record<AgentStatus, string[][]> = {
  idle: [
    [
      ".....YYY.....",
      "....YYYYY....",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPWWWPWWWPKK",
      "KPPWBWPWBWPPK",
      "KPPWWWPWWWPPK",
      ".KPPPPPPPPPK.",
      "...KKK.KKK...",
    ],
    [
      "....YYYY..h..",
      "....YYyYY....",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPPPPPPPPPKK",
      "KPPKKKPKKKPPK",
      "KPPPPPPPPPPPK",
      ".KPPPPPPPPPK.",
      "...KKK.KKK...",
    ],
  ],
  thinking: [
    [
      ".............",
      ".....WW......",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPWBWPWBWPKK",
      "KPPWWWPWWWPPK",
      "KPPWWWPWWWPPK",
      ".KPPPPPPPPPK.",
      "...KKK.KKK...",
    ],
    [
      "......W......",
      ".....WWW.....",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPWBWPWBWPKK",
      "KPPWWWPWWWPPK",
      "KPPWWWPWWWPPK",
      ".KPPPPPPPPPK.",
      "...KKK.KKK...",
    ],
  ],
  "web-search": [
    [
      "..GGGG...YY..",
      "..GgGG...YY..",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPWWWPWWWPKK",
      "KPPWWWPWWWPPK",
      "KPPWWBPWWBPPK",
      ".KPPPPPPPPPK.",
      "...KKK.KKK...",
    ],
    [
      "..GGGG....YY.",
      "..GgGG....YY.",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPWWWPWWWPKK",
      "KPPWWWPWWWPPK",
      "KPPWWBPWWBPPK",
      ".KPPPPPPPPPK.",
      "...KKK.KKK...",
    ],
  ],
  reading: [
    [
      "...RRRRR.....",
      "...RNNNR.....",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPWWWPWWWPKK",
      "KPPWBWPWBWPPK",
      "KPPWWWPWWWPPK",
      ".KPPPPPPPPPK.",
      "...KKK.KKK...",
    ],
    [
      "...RRRRR.....",
      "...RNnNR.....",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPWWWPWWWPKK",
      "KPPWBWPWBWPPK",
      "KPPWWWPWWWPPK",
      ".KPPPPPPPPPK.",
      "...KKK.KKK...",
    ],
  ],
  writing: [
    [
      "......YY.....",
      ".....YK......",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPWWWPWWWPKK",
      "KPPWBWPWBWPPK",
      "KPPWWWPWWWPPK",
      ".KPPPPPPPPPK.",
      "...KKK.KKK...",
    ],
    [
      ".....YY......",
      "....YK.......",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPWWWPWWWPKK",
      "KPPWBWPWBWPPK",
      "KPPWWWPWWWPPK",
      ".KPPPPPPPPPK.",
      "...KKK.KKK...",
    ],
  ],
  done: [
    [
      ".....YYY..h..",
      "....YYYYY....",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPWWWPWWWPKK",
      "KPPWWWPWWWPPK",
      "KPPWWWPWWWPPK",
      ".KPPPPPPPPPK.",
      "...KKK.KKK...",
    ],
    [
      ".h...YYY.....",
      "....YYyYY....",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPWWWPWWWPKK",
      "KPPWWWPWWWPPK",
      "KPPWWWPWWWPPK",
      ".KPPPPPPPPPK.",
      "....KK.KK....",
    ],
  ],
  error: [
    [
      ".....RR......",
      "......R......",
      "....KKKKK....",
      "..KKPPPPPKK..",
      ".KPhPPPPPpPK.",
      "KKPRWRPRWRPKK",
      "KPPWRWPWRWPPK",
      "KPPRWRPRWRPPK",
      ".KPPPPPPPPPK.",
      "...KKK.KKK...",
    ],
    [
      "......RR.....",
      ".......R.....",
      ".....KKKKK...",
      "...KKPPPPPKK.",
      "..KPhPPPPPpPK",
      ".KKPRWRPRWRPK",
      ".KPPWRWPWRWPP",
      ".KPPRWRPRWRPP",
      "..KPPPPPPPPPK",
      "....KKK.KKK..",
    ],
  ],
}
