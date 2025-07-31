# Building the Python SDK Documentation

The Python SDK documentation is built using [Sphinx](https://www.sphinx-doc.org/).

## Prerequisites

Ensure you have installed the documentation dependencies:

```bash
pip install -r ../../requirements-docs.txt
```

## Building the Docs

1. Navigate to the `docs/sdk/python` directory.
2. Run the following command to build the HTML documentation:

   ```bash
   sphinx-build -b html docs/sdk/python docs/sdk/python/api
   ```

3. The generated HTML files will be in the `_build/html` directory. You can open `_build/html/index.html` in your browser to view the documentation.
