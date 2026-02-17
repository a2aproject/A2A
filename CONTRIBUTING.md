# How to contribute

We'd love to accept your patches and contributions to this project.

## Contribution process

### Code reviews

All submissions, including submissions by project members, require review. We
use GitHub pull requests for this purpose. Consult
[GitHub Help](https://help.github.com/articles/about-pull-requests/) for more
information on using pull requests.

### Contributor Guide

You may follow these steps to contribute:

1. **Fork the official repository.** This will create a copy of the official repository in your own account.
2. **Sync the branches.** This will ensure that your copy of the repository is up-to-date with the latest changes from the official repository.
3. **Work on your forked repository's feature branch.** This is where you will make your changes to the code.
4. **Commit your updates on your forked repository's feature branch.** This will save your changes to your copy of the repository.
5. **Submit a pull request to the official repository's main branch.** This will request that your changes be merged into the official repository.
6. **Resolve any linting errors.** This will ensure that your changes are formatted correctly.

Here are some additional things to keep in mind during the process:

- **Test your changes.** Before you submit a pull request, make sure that your changes work as expected.
- **Be patient.** It may take some time for your pull request to be reviewed and merged.

## Documentation Guidelines

### JSON Examples in Documentation

When writing JSON examples involving `Part` objects, follow the **current v1.0 convention**:

- **Do NOT** use a `kind` or `type` field as a Part discriminator.
- **Do NOT** reference the removed v0.3.x types `TextPart`, `FilePart`, or `DataPart`.
- **DO** use **member presence** to identify the Part content type:

  ```json
  // Text part
  { "text": "Hello, world!", "mediaType": "text/plain" }

  // File part (inline bytes)
  { "raw": "base64encodedcontent==", "filename": "image.png", "mediaType": "image/png" }

  // File part (URL reference)
  { "url": "https://example.com/doc.pdf", "filename": "doc.pdf", "mediaType": "application/pdf" }

  // Data part
  { "data": { "key": "value" }, "mediaType": "application/json" }
  ```

When documenting **legacy v0.3.x** behavior for migration guides, use the correct v0.3.x lowercase discriminators: `"kind": "text"`, `"kind": "file"`, `"kind": "data"` — not PascalCase variants.
