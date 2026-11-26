#!/usr/bin/env python3
"""Mount documentation from other repositories into this site's docs dir.

Reads `.mkdocs/mounts.yml`, shallow-clones each repo, copies its docs into
`docs/mounted/<mount_path>/` and writes `.mkdocs/.mounted-nav.json`, which
`.mkdocs/hooks.py` merges into the MkDocs nav.

Usage:
    scripts/mount_docs.py                       # mount everything in the manifest
    scripts/mount_docs.py --local a2a-go=../a2a-go/docs   # use a local checkout
    scripts/mount_docs.py --clean               # remove mounted docs only

Environment:
    DOCS_MOUNT_TOKEN, A2A_BOT_PAT or GITHUB_TOKEN is used (first one set) to
    clone repositories over HTTPS.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / '.mkdocs' / 'mounts.yml'
DEST = ROOT / 'docs' / 'mounted'
NAV_FILE = ROOT / '.mkdocs' / '.mounted-nav.json'
DEFAULT_SECTION = 'Resources'
NAME_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*$')
REPO_RE = re.compile(r'^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$')
REF_RE = re.compile(r'^[A-Za-z0-9._/-]+$')


def log(msg: str) -> None:
    print(f'[mount_docs] {msg}', file=sys.stderr)


def safe_relpath(value: str, field: str) -> Path:
    """Validate a relative path that must stay inside its parent directory."""
    path = Path(value)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError(f'{field} must be a relative path without "..": {value!r}')
    return path


def load_manifest(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    entries = data.get('mounts') or []
    seen: set[str] = set()
    for entry in entries:
        name = entry.get('name', '')
        if not NAME_RE.match(name):
            raise ValueError(f'Invalid mount name: {name!r}')
        if name in seen:
            raise ValueError(f'Duplicate mount name: {name}')
        seen.add(name)
        if not REPO_RE.match(entry.get('repo', '')):
            raise ValueError(f'{name}: repo must be "owner/repo"')
        if not REF_RE.match(str(entry.get('ref', 'main'))):
            raise ValueError(f'{name}: invalid ref')
        safe_relpath(entry.get('mount_path', ''), f'{name}: mount_path')
        safe_relpath(entry.get('source_dir', 'docs'), f'{name}: source_dir')
        if not entry.get('nav_title'):
            raise ValueError(f'{name}: nav_title is required')
    return entries


def clone(repo: str, ref: str, target: Path) -> None:
    token = (
        os.environ.get('DOCS_MOUNT_TOKEN')
        or os.environ.get('A2A_BOT_PAT')
        or os.environ.get('GITHUB_TOKEN')
    )
    url = f'https://github.com/{repo}.git'
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0')
    cmd = ['git']
    if token:
        # Pass the token via -c so it never lands in .git/config.
        basic = base64.b64encode(f'x-access-token:{token}'.encode()).decode()
        cmd += ['-c', f'http.https://github.com/.extraheader=Authorization: Basic {basic}']
    # Shallow fetch of an arbitrary ref (branch, tag or SHA).
    target.mkdir(parents=True)
    subprocess.run([*cmd, 'init', '-q', str(target)], check=True, env=env)
    subprocess.run(
        [*cmd, '-C', str(target), 'remote', 'add', 'origin', url],
        check=True,
        env=env,
    )
    subprocess.run(
        [*cmd, '-C', str(target), 'fetch', '-q', '--depth=1', 'origin', ref],
        check=True,
        env=env,
    )
    subprocess.run(
        [*cmd, '-C', str(target), 'checkout', '-q', 'FETCH_HEAD'],
        check=True,
        env=env,
    )


def page_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.startswith('# '):
                return line[2:].strip()
    except OSError:
        pass
    return path.stem.replace('-', ' ').replace('_', ' ').title()


def auto_nav(base: Path, prefix: str) -> list:
    """Build a nav list from a directory of Markdown files."""
    items: list = []
    index = base / 'index.md'
    if index.is_file():
        items.append({page_title(index): f'{prefix}/index.md'})
    for child in sorted(base.iterdir()):
        if child.name.startswith('.') or child.name == 'index.md':
            continue
        if child.is_file() and child.suffix == '.md' and child.name != 'README.md':
            items.append({page_title(child): f'{prefix}/{child.name}'})
        elif child.is_dir():
            sub = auto_nav(child, f'{prefix}/{child.name}')
            if sub:
                items.append({child.name.replace('-', ' ').replace('_', ' ').title(): sub})
    return items


def prefix_nav(nav: object, prefix: str) -> object:
    """Prefix every page path in a nav tree (external URLs are untouched)."""
    if isinstance(nav, str):
        if re.match(r'^[a-z][a-z0-9+.-]*://', nav):
            return nav
        return f'{prefix}/{safe_relpath(nav, "nav path").as_posix()}'
    if isinstance(nav, list):
        return [prefix_nav(item, prefix) for item in nav]
    if isinstance(nav, dict):
        return {key: prefix_nav(value, prefix) for key, value in nav.items()}
    raise ValueError(f'Unsupported nav node: {nav!r}')


def copy_docs(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        src,
        dest,
        # Never copy symlinks' targets from untrusted repos.
        symlinks=True,
        ignore=shutil.ignore_patterns('.git', '.github'),
    )
    # Drop symlinks entirely; they could point outside the mounted tree.
    for path in list(dest.rglob('*')):
        if path.is_symlink():
            path.unlink()


def mount_entry(entry: dict, local: Path | None) -> dict:
    name = entry['name']
    mount_path = safe_relpath(entry['mount_path'], 'mount_path')
    source_dir = safe_relpath(entry.get('source_dir', 'docs'), 'source_dir')
    dest = DEST / mount_path

    with tempfile.TemporaryDirectory() as tmp:
        if local is not None:
            src = local
            log(f'{name}: using local docs at {src}')
        else:
            checkout = Path(tmp) / 'repo'
            ref = str(entry.get('ref', 'main'))
            log(f"{name}: fetching {entry['repo']}@{ref}")
            clone(entry['repo'], ref, checkout)
            src = checkout / source_dir
        if not src.is_dir():
            raise FileNotFoundError(f'{name}: source directory not found: {src}')
        copy_docs(src, dest)

    prefix = f'mounted/{mount_path.as_posix()}'
    mount_conf = dest / '.mount.yml'
    nav = None
    if mount_conf.is_file():
        conf = yaml.safe_load(mount_conf.read_text(encoding='utf-8')) or {}
        nav = conf.get('nav')
        mount_conf.unlink()
    nav = prefix_nav(nav, prefix) if nav else auto_nav(dest, prefix)
    if not nav:
        raise ValueError(f'{name}: no Markdown pages found')
    log(f'{name}: mounted at docs/{prefix}')
    return {
        'section': entry.get('nav_section', DEFAULT_SECTION),
        'title': entry['nav_title'],
        'nav': nav,
    }


def clean() -> None:
    shutil.rmtree(DEST, ignore_errors=True)
    NAV_FILE.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--manifest', type=Path, default=MANIFEST)
    parser.add_argument(
        '--local',
        action='append',
        default=[],
        metavar='NAME=PATH',
        help='Use a local docs directory instead of cloning (repeatable).',
    )
    parser.add_argument('--clean', action='store_true', help='Remove mounted docs and exit.')
    args = parser.parse_args()

    clean()
    if args.clean:
        return 0

    locals_: dict[str, Path] = {}
    for item in args.local:
        name, _, path = item.partition('=')
        locals_[name] = Path(path).expanduser().resolve()

    try:
        entries = load_manifest(args.manifest)
    except ValueError as err:
        log(f'ERROR invalid manifest {args.manifest}: {err}')
        return 2
    unknown = set(locals_) - {e['name'] for e in entries}
    if unknown:
        log(f'Unknown --local names: {", ".join(sorted(unknown))}')
        return 2

    nav_entries: list[dict] = []
    failed = False
    for entry in entries:
        try:
            nav_entries.append(mount_entry(entry, locals_.get(entry['name'])))
        except (subprocess.CalledProcessError, OSError, ValueError) as err:
            shutil.rmtree(DEST / entry['mount_path'], ignore_errors=True)
            if entry.get('required', False):
                log(f"ERROR {entry['name']}: {err}")
                failed = True
            else:
                log(f"WARNING {entry['name']}: skipped ({err})")
                print(f"::warning::docs mount '{entry['name']}' skipped: {err}")

    NAV_FILE.write_text(
        json.dumps(nav_entries, indent=2) + '\n', encoding='utf-8'
    )
    log(f'Mounted {len(nav_entries)} of {len(entries)} repositories.')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
