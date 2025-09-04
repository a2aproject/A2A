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
- There is a GitHub Action in `.github/workflows/docs.yml` that builds and
  publishes the docs and pushes the built assets to the `gh-pages` branch in
  this repository using `mkdocs gh-deploy --force`. This happens automatically for all
  commits / merges to `main`.
- The A2A documentation is hosted in GitHub pages, and the settings for this are
  in the A2A repository settings in GitHub.

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
