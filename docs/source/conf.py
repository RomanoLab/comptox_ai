# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = 'ComptoxAI'
copyright = '2020, Joseph D. Romano'
author = 'Joseph D. Romano'

# The full version, including alpha/beta/rc tags
release = '0.1a'

# -- General configuration ---------------------------------------------------

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import ablog

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.imgmath',
    'numpydoc',
    'ablog'
]

imgmath_image_format = 'svg'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['templates', ablog.get_html_templates_path()]

source_suffix = '.rst'

master_doc = 'contents'

blog_title = 'ComptoxAI\'s blog'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'comptox-ai'
html_theme_path = ['themes']

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static', '_static/img']

html_additional_pages = {
    'index': 'index.html'
}

html_domain_indices = False  # Don't automatically generate a module index
html_use_index = False  # Don't automatically generate an index

html_favicon = '_static/img/favicon.ico'

html_short_title = 'comptox-ai'

html_theme_options = {
    'google_analytics': True,
}

# pngmath_use_preview = True
# pngmath_dvipng_args = ['-gamma', '1.5', '-D', '96', '-bg', 'Transparent']