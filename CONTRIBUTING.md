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

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for our commit messages and Pull Request titles. This helps us automate our release process, generate changelogs, and maintain high standards.

To align with how our releases are automated, we enforce the following rules for PR titles and commit prefixes depending on which files are modified:

1. **Core Specification Edits (`docs(spec):`)**
   - **Target**: Modifications to the human-readable core specification document (`docs/specification.md`).
   - **Prefix**: Must use the `docs(spec):` prefix (e.g., `docs(spec): clarify handshake sequence`).
   - **Rationale**: Since these changes clarify or refine the specification text without modifying the machine-readable protocol definition, they should be clearly marked as specification changes but must not trigger a new release.

2. **General Documentation (`docs:`)**
   - **Target**: General docs files under the `docs/` directory other than the core specification (e.g., guides, definitions, FAQs).
   - **Prefix**: Must use the `docs:` prefix without the `spec` scope (e.g., `docs: update setup instructions`).
   - **Rationale**: Keeps documentation changes separate from specification and code updates, preventing unnecessary release bumps.

3. **Protocol updates (`feat:` / `fix:`)**
   - **Target**: Functional updates to the machine-readable protocol definition (`specification/a2a.proto`).
   - **Prefix**: Reserved exclusively for changes that include modifications to `specification/a2a.proto` (e.g., `feat: add encryption handshake fields` or `fix: correct typo in service error codes`).
   - **Rationale**: Commits starting with `feat:` or `fix:` trigger automated protocol releases and version bumps (via `release-please`). Pure documentation edits must not use these prefixes to avoid accidental protocol releases.

> [!NOTE]
> If a documentation edit defines a change in how the protocol is actually used, **it must be accompanied by a corresponding update in the protocol definition** (even if it's just updating comments/descriptions in `specification/a2a.proto`). This ensures that the machine-readable schema and human-readable documentation remain synchronized, and correctly triggers a new package release.

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
