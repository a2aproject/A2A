# A2A Docs

<https://a2a-protocol.org>

## Developing A2A docs

1. Clone this repository and `cd` into the repository directory
2. Run `pip install -r requirements-docs.txt`
3. Run `mkdocs serve`, edit `.md` files, and live preview
4. Contribute docs changes as usual

## How it works

- The A2A docs use [mkdocs](https://www.mkdocs.org/) and the
  [mkdocs-material theme](https://squidfunk.github.io/mkdocs-material/)
- All of the source documentation / Markdown files related to the A2A docs are
  in the `docs/` directory in the A2A repository
- `mkdocs.yml` in the repository root contains all of the docs config, including
  the site navigation and organization
- Publishing is done by GitHub Actions, see [Publishing](#publishing) below.
- The A2A documentation is hosted on GitHub Pages (source: "GitHub Actions"),
  and the settings for this, including the `a2a-protocol.org` custom domain,
  are in the A2A repository settings in GitHub.

## Publishing

`.github/workflows/docs-publish.yml` builds the site and deploys it with
`actions/deploy-pages`. `.github/workflows/docs.yml` only checks that pull
requests build. Both share the toolchain setup in
`.github/actions/build-docs`.

| Trigger | Result |
| --- | --- |
| Push to `main` touching docs, specification or `.mkdocs/` | Rebuilds `dev` |
| Release published | Adds the release version; stable releases become `latest` (prereleases do not) |
| `repository_dispatch` `docs-update` from a mounted repo | Rebuilds `dev` |
| Weekly schedule | Rebuilds `dev` (safety net) |
| Manual run | Rebuilds `dev`, or adds a version (optionally as `latest`) |

Versions are managed by [mike](https://github.com/jimporter/mike). Built
versions are stored on the `docs-archive` branch, which is only a store and is
not served. Every run adds its version there, assembles the full site from the
branch, adds the root files (`scripts/assemble_site.sh`) and uploads it as the
Pages artifact. `latest` always points at the newest stable release.

Files published at the site root, outside any version:

- `404.html`, `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-reference.txt`, `llms-full.txt`
- everything in `docs/root-redirects/`: `extensions/`, `bindings/`, `.well-known/`,
  the Search Console verification file and `oauth/`. The OAuth Client ID Metadata
  Documents under `oauth/` are client identities at authorization servers, so
  their paths must never change.

## Mounting docs from other repositories

Other repositories can publish their docs as part of this site.

1. Add an entry to `.mkdocs/mounts.yml` (repo, ref, `source_dir`, `mount_path`,
   `nav_title`). See the comments in that file for all fields.
2. Put Markdown in the mounted repo's `docs/` directory. Optionally add
   `docs/.mount.yml` with a `nav:` list (paths relative to `docs/`) to control
   the navigation; otherwise it is generated from the directory layout.
3. To republish when the mounted repo's docs change, call the reusable workflow
   from that repo:

   ```yaml
   name: Notify A2A docs
   on:
     push:
       branches: [main]
       paths: ["docs/**"]
   jobs:
     notify:
       uses: a2aproject/A2A/.github/workflows/docs-notify.yml@main
       secrets:
         token: ${{ secrets.A2A_BOT_PAT }}
   ```

   Without this, the content is picked up at the next publish run.

At build time `scripts/mount_docs.py` copies the docs to `docs/mounted/<mount_path>/`
(ignored by git) and `.mkdocs/hooks.py` adds them to the nav. Mounted pages are
built with this site's theme and plugins and are included in `llms-full.txt`.
Entries are skipped with a warning if they cannot be cloned, unless
`required: true`. Pull request builds clone anonymously, so private repos are
only mounted when publishing.

To preview a mounted repo locally:

```bash
python scripts/mount_docs.py --local a2a-go=../a2a-go/docs
mkdocs serve
```

Run `python scripts/mount_docs.py --clean` to remove mounted docs again.

## One-time migration from `gh-pages`

1. Merge the change that adds `docs-publish.yml`.
2. Run `scripts/migrate_docs_archive.sh <latest-stable-version> --push`. It
   creates `docs-archive` from `gh-pages`, moves `latest` to that version and
   deletes stray preview versions. `gh-pages` is left alone, so the live site is
   unaffected so far.
3. In repository Settings, Pages, set Source to "GitHub Actions" and confirm the
   custom domain `a2a-protocol.org` and "Enforce HTTPS". The `CNAME` file is
   ignored for Actions deployments. Allow the `github-pages` environment to
   deploy from `main` and from release tags.
4. Add the `A2A_BOT_PAT` secret if mounting private repos.
5. Run the "Docs Publish" workflow manually with version `dev` and check:
   `/`, `/latest/`, `/versions.json`, `/404`, `/llms.txt`, `/llms-full.txt`,
   `/oauth/a2a-cli.json`, `/.well-known/security.txt`, `/extensions/`,
   `/bindings/`, the Search Console verification file and
   `/latest/sdk/python/api/`.
6. Once verified, delete the `gh-pages` branch.

## Docs for AI agents

AI agents are a first-class audience for these docs. Alongside the HTML site we
publish three plain-text files at the site root:

- [`llms.txt`](https://a2a-protocol.org/llms.txt) — a curated index following the
  [llms.txt convention](https://llmstxt.org/): a short summary plus one-line
  descriptions of the pages worth reading. Hand-maintained at `docs/llms.txt`;
  update it whenever a page is added, renamed, or removed.
- [`llms-reference.txt`](https://a2a-protocol.org/llms-reference.txt) — a condensed,
  non-normative protocol reference (core objects, RPC methods, task states).
  Hand-maintained at `docs/llms-reference.txt`; update it when the proto changes.
  Both files state the released protocol version in their opening lines, so they
  need a pass at each release.
- [`llms-full.txt`](https://a2a-protocol.org/llms-full.txt) — every doc page, the
  normative proto, and the Python SDK reference concatenated into one file, with
  layout-only markup stripped. Generated by `scripts/build_llms_full.sh` during
  the docs build and ignored by git, so don't edit or commit it by hand.

`scripts/assemble_site.sh` copies all three, plus `robots.txt`, to the root of
the published site. MkDocs also copies them into each versioned site, so
`/latest/llms.txt` works too.

When writing docs, keep them readable without a browser:

- Put content in Markdown. Styling wrappers such as `<div class="grid cards">` are
  fine, and `llms-full.txt` strips them — but no information should live *only*
  inside HTML or a JavaScript widget, because that is what gets dropped.
- Give every diagram a text equivalent: descriptive alt text for images, and a
  caption or surrounding paragraph that states what the diagram shows.
- Prefer real Markdown headings, lists, and tables over styled `<div>` blocks.

## Building the Python SDK Documentation

The Python SDK documentation is built using [Sphinx](https://www.sphinx-doc.org/).

### Prerequisites

Ensure you have installed the documentation dependencies:

```bash
pip install -r ../../requirements-docs.txt
```

### Building the Docs

1. Run the following command to build the HTML documentation:

   ```bash
   sphinx-build -b html docs/sdk/python docs/sdk/python/api
   ```

2. The generated HTML files will be in the `sdk/python/api` directory. You can open `sdk/python/api/index.html` in your browser to view the documentation.
