#!/bin/bash
set -euo pipefail

# Adds the root-level site files to an assembled GitHub Pages site directory.
# Replaces the old deploy_root_files.sh, which committed these to `gh-pages`.
#
# Usage: scripts/assemble_site.sh <site_dir>
#
# <site_dir> is the exported mike tree (versions/, versions.json, index.html).
# Everything below is copied to its root so URLs stay unchanged.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="$ROOT_DIR/docs"

# Individual files copied from docs/ to the site root.
FILES_TO_DEPLOY=("404.html" "robots.txt" "sitemap.xml" "llms.txt" "llms-reference.txt" "llms-full.txt")

# Everything in docs/root-redirects/ is copied to the site root, e.g.
#   root-redirects/extensions/ -> /extensions/
#   root-redirects/bindings/   -> /bindings/
#   root-redirects/.well-known -> /.well-known/
#   root-redirects/oauth/      -> /oauth/   (OAuth Client ID Metadata Documents:
#                                 each URL is a client's identity at authorization
#                                 servers, so its path must never change)
#   root-redirects/google*.html -> Search Console verification
REDIRECTS_DIR="$DOCS_DIR/root-redirects"

if [ $# -ne 1 ] || [ ! -d "$1" ]; then
  echo "Usage: $0 <site_dir>" >&2
  exit 1
fi
SITE_DIR="$(cd "$1" && pwd)"

echo "[assemble_site] Assembling root files into $SITE_DIR" >&2

for file in "${FILES_TO_DEPLOY[@]}"; do
  if [ -f "$DOCS_DIR/$file" ]; then
    cp "$DOCS_DIR/$file" "$SITE_DIR/$file"
    echo "[assemble_site] Copied $file" >&2
  else
    echo "[assemble_site] Warning: source file not found, skipping: $DOCS_DIR/$file" >&2
  fi
done

if [ -d "$REDIRECTS_DIR" ]; then
  cp -R "$REDIRECTS_DIR/." "$SITE_DIR/"
  echo "[assemble_site] Copied root-redirects/ to the site root" >&2
else
  echo "[assemble_site] Warning: $REDIRECTS_DIR not found" >&2
fi

# Pages serves the artifact as-is; keep Jekyll from touching dot-directories
# such as .well-known.
touch "$SITE_DIR/.nojekyll"

echo "[assemble_site] Done." >&2
