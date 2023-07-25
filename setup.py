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

MAJOR = 1
MINOR = 1
MICRO = 2
ISRELEASED = True
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


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
        'ablog==0.10.19',
        'numpy==1.24.4',
        'scipy==1.10.1',
        'pandas',
        'neo4j==4.3.4',
        'networkx==2.6.3',
        'py2neo==2021.1.5',
        'rdflib==5.0.0',
        'openpyxl==3.0.7',
        'owlready2==0.34',
        'PyYAML==5.3.1',
        'ipdb==0.13.9',
        'pytest==7.4',
    ],
    extras_require={
        "testing": ["pytest"],
        "coverage": ["pytest-cov", "codecov"],
        "docs": ["numpydoc", "sphinxext-opengraph"]
    },
    entry_points={
        'console_scripts': [
            'make_qsar=comptox_ai.scripts.make_qsar:main'
        ]
    }
)
