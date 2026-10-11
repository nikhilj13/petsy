import { Plugin } from "@opencode/plugin/tui"
import { Avatar } from "./avatar/Avatar.js"
import type { AvatarPosition } from "./avatar/status.js"

function asPosition(value: unknown): AvatarPosition {
  if (value === "top-left" || value === "hidden" || value === "top-right") return value
  return "top-right"
}

function asPositiveInt(value: unknown, fallback: number): number {
  if (typeof value === "number" && Number.isFinite(value) && value > 0) {
    return Math.min(12, Math.floor(value))
  }
  return fallback
}

export default Plugin.define({
  id: "petsy",
  setup(context) {
    const options = (context.options ?? {}) as Record<string, unknown>
    const position = asPosition(options.position)
    const fps = asPositiveInt(options.fps, 5)
    const animations = options.animations !== false
    const doneTimeoutMs = asPositiveInt(options.doneTimeoutMs, 3000)
    const enabled = options.enabled !== false

    const removeSlot = context.ui.slot({
      append: "session.composer.top",
      render: (input) => (
        <Avatar
          sessionID={input.sessionID}
          position={position}
          fps={fps}
          animations={animations}
          doneTimeoutMs={doneTimeoutMs}
          enabled={enabled}
        />
      ),
    })

    context.keymap.layer(() => ({
      mode: "global",
      commands: [
        {
          id: "petsy.toggle",
          title: "Toggle Petsy avatar",
          group: "Petsy",
          palette: true,
          run: () => {
            context.ui.toast.show({
              message: "Petsy toggle needs a TUI reload to apply (set plugins[].options.enabled).",
              variant: "info",
            })
          },
        },
      ],
    }))

    return () => {
      removeSlot()
    }
  },
})
