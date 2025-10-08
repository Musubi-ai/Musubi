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
copyright = '2025, Musubi team'
author = 'Musubi team'
release = '1.0.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',          
    'sphinx.ext.napoleon',         
    'sphinx.ext.viewcode',  
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

html_logo = '../assets/logo/favicon.png'
html_favicon = '../assets/logo/favicon.png'

# Furo 主題自訂顏色
html_theme_options = {
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#2E86AB",
        "color-brand-content": "#2E86AB",
    },
    "dark_css_variables": {
        "color-brand-primary": "#2E86AB",
        "color-brand-content": "#2E86AB",
    },
}

# 側邊欄顯示全部章節
html_sidebars = {
   "**": ["sidebar/scroll-start.html",
          "sidebar/brand.html",
          "sidebar/navigation.html",
          "sidebar/scroll-end.html"],
}