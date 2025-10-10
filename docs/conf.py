# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'musubi-scrape'
copyright = '2025, Lung Chuan Chen'
author = 'Lung Chuan Chen'
release = '1.1.0'

master_doc = "index"

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',          
    'sphinx.ext.napoleon',         
    'sphinx.ext.viewcode',
    "sphinx.ext.autosummary",
    'myst_parser',
    "sphinx_design"
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

myst_enable_extensions = [
    "deflist",
    "html_admonition",
    "html_image",
    "colon_fence",
    "dollarmath",
    "amsmath",
    # "linkify",
    "replacements",
    "substitution",
    "tasklist"
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ['_static']

html_logo = '../assets/logo/FullLogo.png'
html_favicon = '../assets/logo/favicon.png'

html_theme_options = {
    "repository_url": "https://github.com/Musubi-ai/Musubi",
    "use_repository_button": True,
    "use_fullscreen_button": True,
    "use_source_button": True,
    "home_page_in_toc": True
}

html_css_files = [
    "https://unpkg.com/sphinx-design@0.6.0/dist/sphinx-design.min.css",
]