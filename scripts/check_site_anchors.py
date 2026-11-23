"""Verify that every same-page fragment link in the built site resolves.

The specification page renders its data-model tables from the proto definition
via the macros in ``.mkdocs/macros.py``. Each non-primitive field type becomes a
link such as ``[`Task`](#Task)``. Those links only work when the page defines a
matching anchor, and nothing checked that: MkDocs reports a missing anchor as an
informational message and still exits 0.

Run after ``mkdocs build``:

    python3 scripts/check_site_anchors.py site

Exits non-zero and lists the offenders when a fragment has no target.

Sphinx-generated SDK pages under ``sdk/python/`` are skipped: they emit repeated
``id1``/``id3``-style ids by design, which is unrelated to the anchors checked
here and would otherwise drown the report.
"""

from __future__ import annotations

import argparse
import sys

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote


class _Anchors(HTMLParser):
    """Collect element ids and same-page fragment links from one HTML file."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.fragments: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        for name, value in attrs:
            if value is None:
                continue
            if name == 'id':
                self.ids.add(value)
            elif name == 'name' and tag == 'a':
                # Legacy ``<a name="...">`` anchors are valid link targets.
                self.ids.add(value)
            elif name == 'href' and value.startswith('#'):
                fragment = unquote(value[1:])
                if fragment and not fragment.startswith('!'):
                    self.fragments.append(fragment)


def dead_fragments(html_path: Path) -> list[str]:
    """Return the fragments in ``html_path`` that point at no element id."""
    parser = _Anchors()
    parser.feed(html_path.read_text(encoding='utf-8'))
    return [
        fragment for fragment in parser.fragments if fragment not in parser.ids
    ]


def main(argv: list[str] | None = None) -> int:
    """Report every built page with an unresolvable fragment link."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'site_dir',
        nargs='?',
        default='site',
        help='Built site directory (default: site)',
    )
    args = parser.parse_args(argv)

    site_dir = Path(args.site_dir)
    if not site_dir.is_dir():
        parser.error(f'not a directory: {site_dir}')

    pages = 0
    failures = []
    for page in sorted(site_dir.rglob('*.html')):
        relative = page.relative_to(site_dir)
        # Sphinx writes the SDK reference; its repeated idN anchors are not
        # ours to police and the repo's lychee config excludes the same paths.
        if relative.parts[:3] in (
            ('sdk', 'python', 'api'),
            ('sdk', 'python', '_build'),
        ):
            continue
        dead = dead_fragments(page)
        if dead:
            pages += 1
            failures.extend(
                f'{relative.as_posix()}: #{fragment}' for fragment in dead
            )

    if not failures:
        print('OK: every same-page fragment resolves')
        return 0

    print(f'{len(failures)} dead fragment link(s) on {pages} page(s):')
    for failure in failures:
        print(f'  {failure}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
