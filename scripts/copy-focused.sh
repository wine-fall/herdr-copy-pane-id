#!/usr/bin/env bash
# Copy the focused pane's public id (for example w1:p2) to the clipboard.
set -uo pipefail

herdr="${HERDR_BIN_PATH:-herdr}"

notify() {
  "$herdr" notification show "$1" --body "$2" >/dev/null 2>&1 || true
}

pane_id="${HERDR_PANE_ID:-}"

# Keybind and menu invocations set HERDR_PANE_ID. Fall back to the context JSON
# for invocation sources that only carry the focused pane there.
if [ -z "$pane_id" ] && [ -n "${HERDR_PLUGIN_CONTEXT_JSON:-}" ]; then
  pane_id=$(printf '%s' "$HERDR_PLUGIN_CONTEXT_JSON" |
    sed -n 's/.*"focused_pane_id":"\([^"]*\)".*/\1/p')
fi

if [ -z "$pane_id" ]; then
  notify "copy pane id failed" "no focused pane"
  exit 1
fi

if command -v pbcopy >/dev/null 2>&1; then
  printf '%s' "$pane_id" | pbcopy
elif command -v wl-copy >/dev/null 2>&1; then
  printf '%s' "$pane_id" | wl-copy
elif command -v xclip >/dev/null 2>&1; then
  printf '%s' "$pane_id" | xclip -selection clipboard
elif command -v xsel >/dev/null 2>&1; then
  printf '%s' "$pane_id" | xsel --clipboard --input
else
  # No clipboard tool, typically a headless server reached over SSH. Write an
  # OSC 52 sequence into the pane's own terminal: Herdr parses it as pane
  # output and forwards the clipboard write to the foreground client, which
  # is the machine you are sitting at. Nothing is drawn on screen.
  shell_pid=$("$herdr" pane process-info --pane "$pane_id" 2>/dev/null |
    sed -n 's/.*"shell_pid":\([0-9]*\).*/\1/p')
  tty=$([ -n "$shell_pid" ] && ps -o tty= -p "$shell_pid" 2>/dev/null | tr -d ' ')
  case "$tty" in
    "" | "?" | "??")
      notify "copy pane id failed" "no clipboard tool and no pane terminal for OSC 52"
      exit 1
      ;;
  esac
  printf '\033]52;c;%s\a' "$(printf '%s' "$pane_id" | base64 | tr -d '\n')" >"/dev/$tty" || {
    notify "copy pane id failed" "could not write OSC 52 to /dev/$tty"
    exit 1
  }
fi

notify "copied pane id" "$pane_id"
