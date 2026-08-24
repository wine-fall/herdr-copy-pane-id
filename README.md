# Copy pane id

A [Herdr](https://herdr.dev) plugin that puts the focused pane's id (`w1:p2`) on
your clipboard with one keypress, and can optionally show every pane's id on its
border.

Pane ids are the only unambiguous handle the Herdr CLI accepts. When you are
driving coding agents across panes, being able to say "read pane `w1:p2`" beats
describing which workspace, tab, and split you meant.

![copying a pane id](docs/copy-pane-id.png)

## Install

```bash
herdr plugin install wine-fall/herdr-copy-pane-id
```

Then bind a key in `~/.config/herdr/config.toml`:

```toml
[[keys.command]]
key = "prefix+y"
type = "plugin_action"
command = "wine-fall.copy-pane-id.copy-focused"
description = "copy focused pane id"
```

Add a second binding if you also want the id labels toggle:

```toml
[[keys.command]]
key = "prefix+i"
type = "plugin_action"
command = "wine-fall.copy-pane-id.toggle-id-labels"
description = "toggle pane id labels"
```

Reload with `herdr server reload-config`.

## Actions

| Action | What it does |
| --- | --- |
| `copy-focused` | Copies the focused pane's id to the clipboard and shows a toast. |
| `toggle-id-labels` | Relabels every pane so its id shows on the pane border. Run it again to restore the previous labels. |

![every pane showing its id](docs/id-labels.png)

`toggle-id-labels` saves the labels it replaces under
`HERDR_PLUGIN_STATE_DIR` and restores them when toggled off, so your own pane
names survive the round trip. A pane that already has a name shows as
`id · name`. Relabeling runs one CLI call per pane, so a toggle over many panes
takes a moment; a second toggle fired while one is still running is refused
rather than interleaved. Renaming a pane by hand while labels are on is undone
when you toggle them off.

## Requirements

- macOS or Linux.
- A clipboard tool: `pbcopy` (macOS), or `wl-copy`, `xclip`, or `xsel` (Linux).
- `python3`, for `toggle-id-labels` only. `copy-focused` needs nothing beyond a
  shell and a clipboard tool.

## Known limitation: remote sessions

The plugin copies to the clipboard of the machine Herdr runs on. That is what
you want for a local Herdr. If you SSH into a server and run Herdr there, the id
lands on that server's clipboard, which usually does not exist on a headless
box, so the copy will not reach the terminal you are sitting at.

Herdr itself handles this case for text selections by falling back to OSC 52,
which travels back over SSH to your local terminal emulator. Plugins cannot use
that path today: plugin stdout is captured for logs rather than connected to the
host terminal. If Herdr ever exposes a clipboard write through the CLI, this
plugin can use it and the limitation goes away.

## License

MIT
