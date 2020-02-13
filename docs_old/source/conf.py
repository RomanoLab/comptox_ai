#!/usr/bin/env python3

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import time
from pathlib import Path
import importlib.resources as pkg_resources
import glob
import comptox_ai  # Mostly so we can find the version string

# -- Project information -----------------------------------------------------

project = 'ComptoxAI'
copyright = time.strftime('%Y, Joseph D. Romano')
author = 'Joseph D. Romano, PhD'

str_version = comptox_ai.__version__

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    # 'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.ifconfig',
    'IPython.sphinxext.ipython_console_highlighting',
    'IPython.sphinxext.ipython_directive',
    'numpydoc',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
default_role = "autolink"

rst_prolog = """
.. |version| replace:: VERSION
""".replace('VERSION', str_version)

def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip

def setup(app):
    app.connect("autodoc-skip-member", skip)

html_additional_pages = {
    'index': 'indexcontent.html',
}

html_theme = 'alabaster'

html_title = "%s v%s Manual" % (project, str_version)
html_static_path = ['_static']
html_last_updated_fmt = '%b %d, %Y'
html_css_files = [
    'css/custom.css',
]
html_style = 'css/custom.css'
html_use_modindex = True
html_copy_source = False
html_domain_indices = False
html_file_suffix = '.html'
html_favicon = os.path.join('_static', 'img', 'favicon.ico')
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html'
    ]
}
html_theme_options = {
    'github_user': 'jdromano2',
    'github_repo': 'comptoxai',
    'github_button': 'true',
    'fixed_sidebar': 'fixed',
    'description': 'An AI research toolkit for computational toxicology.',
    'show_powered_by': 'false',
    'sidebar_header': '#226b07'
}
