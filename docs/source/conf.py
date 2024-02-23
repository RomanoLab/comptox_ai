# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

import os
import re
import sys
from datetime import datetime

import ablog
from docutils.parsers.rst import directives
from sphinx.ext.autosummary import Autosummary, get_documenter
from sphinx.util.inspect import safe_getattr

# import comptox_ai

project = 'ComptoxAI'
copyright = f'(c) {datetime.now().year} by Joseph D. Romano (MIT License)'
author = 'Joseph D. Romano'

# The full version, including alpha/beta/rc tags
release = '0.1a'

# -- General configuration ---------------------------------------------------

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


#############################################
# Custom Autosummary that shows class members
#############################################

# see: https://stackoverflow.com/a/30783465/1730417

class AutoClassSummary(Autosummary):
    option_spec = {
        'methods': directives.unchanged,
        'attributes': directives.unchanged
    }

    required_arguments = 1

    @staticmethod
    def get_members(obj, typ, include_public=None):
        if not include_public:
            include_public = []
        items = []
        for name in dir(obj):
            try:
                documenter = get_documenter(safe_getattr(obj, name), obj)
            except AttributeError:
                continue
            if documenter.objtype == typ:
                items.append(name)
        public = [
            x for x in items if x in include_public or not x.startswith('_')]
        return public, items

    def run(self):
        clss = str(self.arguments[0])
        try:
            (module_name, class_name) = clss.rsplit('.', 1)
            m = __import__(module_name, globals(), locals(), [class_name])
            c = getattr(m, class_name)
            if 'methods' in self.options:
                _, methods = self.get_members(c, 'method', ['__init__'])
                self.content = ["~%s.%s" % (
                    clss, method) for method in methods if not method.startswith('_')]
            if 'attributes' in self.options:
                _, attribs = self.get_members(c, 'attribute')
                self.content = ["~%s.%s" % (
                    clss, attrib) for attrib in attribs if not attrib.startswith('_')]
        finally:
            return super(AutoClassSummary, self).run()


def setup(app):
    app.add_directive('autoclasssummary', AutoClassSummary)

########################
# End custom autosummary
########################


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',  # note: automatically loaded by numpydoc
    'sphinx.ext.coverage',
    'numpydoc',
    'ablog',
    'sphinxext.opengraph',
]
# 'sphinxcontrib.bibtex'
# bibtex_bibfiles = ['refs.bib']
html_static_path = ['_static']

imgmath_image_format = 'svg'
img_font_size = 14

autodoc_default_options = {"members": True, "inherited-members": True}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['templates', ablog.get_html_templates_path()]

autosummary_generate = True

source_suffix = '.rst'

master_doc = 'contents'

blog_title = 'ComptoxAI\'s blog'

exclude_patterns = ["build", "templates", "themes"]

pygments_style = "sphinx"

numpydoc_class_members_toctree = False

# Configuration of sphinx.ext.coverage
coverage_show_missing_items = True

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
