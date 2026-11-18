#!/bin/bash
set -euo pipefail

# One-time migration from the old `gh-pages` deployment to the Actions-based one.
#
# 1. Creates `docs-archive` from `gh-pages` (the version store used by mike).
# 2. Moves the `latest` alias from `dev` to the newest stable release.
# 3. Removes stray preview versions (pr-*, bare commit SHAs).
#
# It only pushes `docs-archive`. `gh-pages` is left untouched so the live site
# keeps working until GitHub Pages is switched to the "GitHub Actions" source.
#
# Usage: scripts/migrate_docs_archive.sh <latest-version> [--push]
#   e.g. scripts/migrate_docs_archive.sh v1.0.1 --push

LATEST="${1:?Usage: $0 <latest-version> [--push]}"
PUSH="${2:-}"

git fetch origin gh-pages
git branch -f --no-track docs-archive origin/gh-pages

echo "Versions before:" >&2
mike list --branch docs-archive >&2

# Move `latest` off `dev` (--update-aliases moves an alias that exists elsewhere).
mike alias --branch docs-archive --update-aliases "$LATEST" latest

# Drop stray previews: pr-<n> and bare commit SHAs.
for version in $(mike list --branch docs-archive | awk '{print $1}'); do
  if [[ "$version" =~ ^pr-[0-9]+$ ]] || [[ "$version" =~ ^[0-9a-f]{7,40}$ ]]; then
    echo "Deleting stray version $version" >&2
    mike delete --branch docs-archive "$version"
  fi
done

echo "Versions after:" >&2
mike list --branch docs-archive >&2

if [ "$PUSH" = "--push" ]; then
  git push origin docs-archive
  echo "Pushed docs-archive." >&2
else
  echo "Dry run: review with 'git log docs-archive', then re-run with --push." >&2
fi
