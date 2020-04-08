#!/usr/bin/env python

__all__ = [
    'str_version'
]

import os
from pathlib import Path
import setuptools

with open("README.md", 'r') as fp:
    long_description = fp.read()

package_src_dir = Path(__file__).parent

# version_file = open(os.path.join(str(package_src_dir), 'VERSION'), 'r')
# str_version = version_file.read().strip()
str_version = "0.1.dev0"

setuptools.setup(
    name="comptox_ai",
    version=str_version,
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
