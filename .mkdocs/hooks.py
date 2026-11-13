"""Custom MkDocs build hooks for A2A documentation.

Local preview:
    Material's instant navigation swaps page HTML without a full reload, which
    aborts MkDocs' livereload long-poll and prevents the browser tab from
    refreshing. Disable that feature while serving, and inject a poller that
    starts immediately (MkDocs' built-in script waits for window.load and a
    visible tab, so IDE previews and background tabs never connect).

Custom 404 page:
    Restore the hand-written `404.html` into the build output after the theme
    overwrites it.
"""

from __future__ import annotations

import shutil

from pathlib import Path


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


def on_post_build(config, **kwargs) -> None:
    """Put the hand-written 404 page back into the build output.

    MkDocs renders the theme's own `404.html` static template after copying
    static files from the docs directory, so `docs/404.html` is overwritten
    on every build. Copying it back here keeps the custom page visible on
    `mkdocs serve`, which serves `<site_dir>/404.html` for unknown paths.
    """
    source = Path(config["docs_dir"]) / "404.html"
    if source.is_file():
        shutil.copyfile(source, Path(config["site_dir"]) / "404.html")
