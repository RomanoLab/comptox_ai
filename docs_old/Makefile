# Makefile for Sphinx documentation
#

# See: tech.davis-hansson.com/p/make/
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# ifeq ($(origin .RECIPEPREFIX), undefined)
# 	$(error This Make does not support .RECIPEPREFIX. Please use GNU Make 4.0 or later)
# endif
# .RECIPEPREFIX = >


PYVER:=(shell python -c 'from sys import version_info as v; print("{0}.{1}".format(v[0], v[1]))')

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= LANG=C sphinx-build
PAPER         ?=
SOURCEDIR     = source
BUILDDIR      = build
DISTDIR       = ../../comptox.ai/www/docs/

FILES=

# Internal variables
PAPEROPT      =
ALLSPHINXOPTS = -WT --keep-going -d build/doctrees $(PAPEROPT) $(SPHINXOPTS) source

.PHONY: help clean html html-build latex dist Makefile dd

#===============================================================================

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	-rm -rf build/*
	find . -name generated -type d -prune -exec rm -rf "{}" ";"

dist:
	$(MAKE) html
	cp -r build/html/* $(DISTDIR)

html: html-build
html-build:
	mkdir -p build/html build/doctrees
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) build/html $(FILES)
	@echo
	@echo "Build finished. HTML pages are in build/html."


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
