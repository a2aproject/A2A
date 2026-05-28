# -- Project information -----------------------------------------------------

project = 'a2a-sdk'
copyright = '2026, The Linux Foundation'
author = 'The Linux Foundation'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',  # Automatically generate summaries
    'sphinx.ext.napoleon',  # Support for Google-style docstrings
    'myst_parser',  # For Markdown support
]

# Tell autosummary to generate stub files
autosummary_generate = True

# Suppress warnings from external SDK package
suppress_warnings = [
    'ref.python',  # Suppress "more than one target found for cross-reference"
    'ref.ref',     # Suppress "undefined label"
    'toc.not_included', # Suppress "document isn't included in any toctree"
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'furo'

autodoc_member_order = 'alphabetical'
