# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

from datetime import datetime

project = 'ComptoxAI'
copyright = f'(c) {datetime.now().year} by Joseph D. Romano (MIT License)'
author = 'Joseph D. Romano'

# The full version, including alpha/beta/rc tags
release = '0.1a'

# -- General configuration ---------------------------------------------------

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import comptox_ai

import ablog

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.imgmath',
    'sphinx.ext.autosummary',
    'numpydoc',
    'ablog',
    'sphinxext.opengraph'
]

imgmath_image_format = 'svg'

autodoc_default_options = {"members": True, "inherited-members": True}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['templates', ablog.get_html_templates_path()]

autosummary_generate = True

source_suffix = '.rst'

master_doc = 'contents'

blog_title = 'ComptoxAI\'s blog'

exclude_patterns = ["build", "templates", "themes"]

pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'comptox-ai'
html_theme_path = ['themes']

html_copy_source = True

html_context = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static', '_static/img']

html_additional_pages = {
    'index': 'index.html',
    'browse': 'browse.html',
    'data': 'data.html'
}

# html_extra_path = [
#     '../../_redirects'
# ]

html_domain_indices = False  # Don't automatically generate a module index
html_use_index = False  # Don't automatically generate an index

html_favicon = '_static/img/favicon.ico'

html_short_title = 'comptox-ai'

html_theme_options = {
    'google_analytics': True,
}

# pngmath_use_preview = True
# pngmath_dvipng_args = ['-gamma', '1.5', '-D', '96', '-bg', 'Transparent']

# For sphinxext.opengraph
ogp_site_url = "http://comptox.ai/"
ogp_image = "http://comptox.ai/_images/ComptoxAI_logo_type.png"
ogp_use_first_image = True
ogp_site_name = "comptox-ai"