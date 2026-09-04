"""MkDocs hooks for local preview.

Material's instant navigation swaps page HTML without a full reload, which
aborts MkDocs' livereload long-poll and prevents the browser tab from
refreshing. Disable that feature while serving, and inject a poller that
starts immediately (MkDocs' built-in script waits for window.load and a
visible tab, so IDE previews and background tabs never connect).
"""

from __future__ import annotations

_serving = False


def on_startup(command, dirty):
    global _serving
    _serving = command == "serve"


def on_config(config):
    if not _serving:
        return config

    theme = config["theme"]
    features = list(theme.get("features") or [])
    theme["features"] = [
        feature
        for feature in features
        if not str(feature).startswith("navigation.instant")
    ]
    config["extra"]["dev_livereload"] = True
    return config
