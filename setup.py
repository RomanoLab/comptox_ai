#!/usr/bin/env python

__all__ = [
    'VERSION'
]

import os
from pathlib import Path
import setuptools

with open("README.md", 'r') as fp:
    long_description = fp.read()

package_src_dir = Path(__file__).parent

MAJOR      = 0
MINOR      = 01
MICRO      = 0
ISRELEASED = False
VERSION    = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

def get_docs_url():
    return "https://comptox.ai/use/index.html"

setuptools.setup(
    name="comptox_ai",
    version=VERSION,
    author="Joseph D. Romano, PhD",
    author_email="joseph.romano@pennmedicine.upenn.edu",
    description="An ontology and knowledge base to support discovery in computational toxicology",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jdromano2/comptox_ai",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
        "Environment :: Console"
    ],
    python_requires='>=3.7',
    include_package_data=True,
    install_requires=[
        'py2neo',
        'owlready2',
        'numpy',
        'pandas',
        'scipy',
        'networkx',
        'ablog',
        'Sphinx',
        'blessed',
        'neo4j',
        'numpydoc',
        'docutils',
        'ipdb',
        'rdflib'
    ],
    extras_require={
        "testing": ["pytest"],
        "coverage": ["pytest-cov", "codecov"]
    }
)
