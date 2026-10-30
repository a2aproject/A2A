"""Custom MkDocs build hooks for A2A documentation."""

import shutil
from pathlib import Path


def on_post_build(config, **kwargs) -> None:
    """Put the hand-written 404 page back into the build output.

    MkDocs renders the theme's own `404.html` static template after copying
    static files from the docs directory, so `docs/404.html` is overwritten
    on every build. Copying it back here keeps the custom page visible on
    `mkdocs serve`, which serves `<site_dir>/404.html` for unknown paths.
    """
    source = Path(config['docs_dir']) / '404.html'
    if source.is_file():
        shutil.copyfile(source, Path(config['site_dir']) / '404.html')
