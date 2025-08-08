# -- Project information -----------------------------------------------------

project = 'a2a-sdk'
copyright = '2025, Google LLC'
author = 'Google LLC'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',  # Automatically generate summaries
    'sphinx.ext.napoleon',  # Support for Google-style docstrings
    'myst_parser',  # For Markdown support
]

# Tell autosummary to generate stub files
autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'furo'

autodoc_member_order = 'alphabetical'
