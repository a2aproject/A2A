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

Mounted docs:
    Merge the nav entries written by `scripts/mount_docs.py` into the nav.
"""

from __future__ import annotations

import json
import shutil

from pathlib import Path


_serving = False


def on_startup(command, dirty):
    global _serving
    _serving = command == "serve"


def _merge_mounted_nav(config) -> None:
    """Append docs mounted from other repos (scripts/mount_docs.py) to the nav."""
    nav_file = Path(config["config_file_path"]).parent / ".mkdocs" / ".mounted-nav.json"
    if not nav_file.is_file():
        return
    nav = config["nav"] or []
    for mount in json.loads(nav_file.read_text(encoding="utf-8")):
        section = mount["section"]
        entry = {mount["title"]: mount["nav"]}
        for item in nav:
            if isinstance(item, dict) and section in item:
                item[section].append(entry)
                break
        else:
            nav.append({section: [entry]})
    config["nav"] = nav


def on_config(config):
    _merge_mounted_nav(config)

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

    # ADRs live outside docs/ but are linked from the specification page
    # (`../adrs/...`). Publish them inside every built version, since
    # `mike deploy` builds the site itself.
    adrs = Path(config["docs_dir"]).parent / "adrs"
    if adrs.is_dir():
        target = Path(config["site_dir"]) / "adrs"
        target.mkdir(parents=True, exist_ok=True)
        for adr in adrs.glob("*.md"):
            shutil.copyfile(adr, target / adr.name)
