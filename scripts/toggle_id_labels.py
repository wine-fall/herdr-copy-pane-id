#!/usr/bin/env python3
"""Toggle pane id labels.

On: every pane is relabeled so its public id shows on the pane border.
Off: the labels captured when toggling on are restored.
"""

import json
import os
import subprocess

HERDR = os.environ.get("HERDR_BIN_PATH", "herdr")
STATE_DIR = os.environ.get("HERDR_PLUGIN_STATE_DIR", ".")
STATE_FILE = os.path.join(STATE_DIR, "id-labels.json")
LOCK_FILE = os.path.join(STATE_DIR, "toggle.lock")


def herdr(*args):
    result = subprocess.run(
        [HERDR, *args], capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def notify(title, body=""):
    subprocess.run(
        [HERDR, "notification", "show", title, "--body", body],
        capture_output=True,
        text=True,
    )


def restore(saved):
    restored = 0
    for pane_id, label in saved.items():
        try:
            if label:
                herdr("pane", "rename", pane_id, label)
            else:
                herdr("pane", "rename", pane_id, "--clear")
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            # The pane was closed while labels were on. Skip it so one dead
            # pane cannot strand every other pane with an id label.
            continue
        restored += 1
    os.remove(STATE_FILE)
    notify("pane id labels off", f"restored {restored} panes")


def apply_labels():
    saved = {}
    for pane in herdr("pane", "list")["result"]["panes"]:
        pane_id = pane["pane_id"]
        label = pane.get("label", "")
        saved[pane_id] = label
        herdr("pane", "rename", pane_id, f"{pane_id} · {label}" if label else pane_id)

    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as handle:
        json.dump(saved, handle)
    notify("pane id labels on", f"labeled {len(saved)} panes")


def main():
    os.makedirs(STATE_DIR, exist_ok=True)

    # Relabeling every pane takes a few seconds, one CLI call per pane. Without
    # this lock a second keypress mid-run interleaves with the first and leaves
    # the toggle state out of sync with the labels actually on screen.
    try:
        lock = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        notify("pane id labels busy", "a toggle is already running")
        return
    os.close(lock)

    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, encoding="utf-8") as handle:
                restore(json.load(handle))
        else:
            apply_labels()
    finally:
        os.unlink(LOCK_FILE)


if __name__ == "__main__":
    main()
