# Makefile for Sphinx documentation
#

PYVER:=(shell python -c 'from sys import version_info as v; print("{0}.{1}".format(v[0], v[1]))')

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
DISTDIR       = ../../comptox.ai/www/docs/

# Internal variables
PAPEROPT      = -D latex_paper_size=a4
ALLSPHINXOPTS = -WT --keep-going -d build/doctrees $(PAPEROPT) \
  #(SPHINXOPTS) source

.PHONY: help clean html html-build latex dist Makefile

#===============================================================================

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

dist:
	$(MAKE) html
	cp -r build/html/* $(DISTDIR)

html: html-build
html-build: generate
	mkdir -p build/html build/doctrees
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) build/html $(FILES)
	@echo
	@echo "Build finished. HTML pages are in build/html."


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
