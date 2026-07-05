# How to contribute

We'd love to accept your patches and contributions to this project.

## Development Setup

### Prerequisites

To contribute to this project, you will need the following tools installed:

- [Python 3.10+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) - Fast Python package installer and resolver.
- [Node.js & npm](https://nodejs.org/en/download/) - For markdown formatting tools.
- [Docker](https://www.docker.com/get-started) - Required for running the local linter.

## Working with Documentation

The A2A documentation is built using [MkDocs](https://www.mkdocs.org/) with the [Material theme](https://squidfunk.github.io/mkdocs-material/).

### Local Setup

1. **Create a virtual environment:**

    ```bash
    uv venv .doc-venv
    ```

2. **Activate the virtual environment:**

    ```bash
    source .doc-venv/bin/activate  # Unix/macOS
    # .doc-venv\Scripts\activate  # Windows
    ```

3. **Install dependencies:**

    ```bash
    uv pip install -r requirements-docs.txt
    ```

### Build and Serve

1. **Build the documentation:**
    This script regenerates the JSON schema from the protocol definition, builds the SDK documentation, and then builds the MkDocs site.

    ```bash
    ./scripts/build_docs.sh
    ```

2. **Serve the documentation locally:**
    Run the following command to start a local server with live reloading:

    ```bash
    mkdocs serve
    ```

3. **View the documentation:**
    Open [http://localhost:8000](http://localhost:8000) in your browser.

## Code Standards

### Linting

We use [Super Linter](https://github.com/super-linter/super-linter) to ensure code quality across the repository. You can run the linter locally using Docker:

```bash
./scripts/lint.sh
```

### Formatting

We use [markdownlint](https://github.com/igorshubovych/markdownlint-cli) for formatting markdown files. You can fix most formatting issues automatically by running:

```bash
./scripts/format.sh
```

### Conventional Commits

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for our commit messages and PR titles to automate releases. We enforce the following rules depending on which files are changed:

- **Core Specification (`docs(spec):`)**: Use for changes to the core specification (`docs/specification.md`).
- **General Documentation (`docs:`)**: Use for other files under `docs/` (without the `spec` scope).
- **Protocol Updates (`feat:` / `fix:`)**: Reserved exclusively for changes to the protocol definition (`specification/a2a.proto`).

> [!TIP]
> If a documentation change alters how the protocol should be used, update the `.proto` file as well (even just its comments) so that a new protocol release is triggered.

## Contribution Process

### Code reviews

All submissions, including submissions by project members, require review. We
use GitHub pull requests for this purpose. Consult
[GitHub Help](https://help.github.com/articles/about-pull-requests/) for more
information on using pull requests.

### Workflow

You may follow these steps to contribute:

1. **Fork the official repository.** This will create a copy of the official repository in your own account.
2. **Sync the branches.** This will ensure that your copy of the repository is up-to-date with the latest changes from the official repository.
3. **Work on your forked repository's feature branch.** This is where you will make your changes to the code.
4. **Test your changes.** Build and preview the documentation locally to ensure everything looks correct.
5. Format and lint your code. Run ./scripts/format.sh and ./scripts/lint.sh to ensure your changes meet our standards.
6. **Commit your updates.** Use conventional commit messages on your feature branch.
7. **Submit a pull request.** Submit a PR from your fork's feature branch to the official repository's `main` branch.
8. **Resolve any feedback.** Work with reviewers to address any comments or requested changes.

Be patient! It may take some time for your pull request to be reviewed and merged.

## Conformance fixture contributions (recommended pattern)

When proposing interoperability or conformance fixtures, include enough detail for
maintainers and implementers to validate behavior consistently.

Suggested minimum metadata per fixture proposal:

- Protocol area covered (for example: discovery, lifecycle, errors, streaming)
- Expected request/response shape or event sequence
- Pass/fail criteria that can be checked across SDKs
- Edge case rationale (why this fixture matters for interoperability)

For protocol-affecting fixture changes, link the related issue and document any
specification assumptions directly in the PR description.
