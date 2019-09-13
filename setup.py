#!/usr/bin/env python

import setuptools

with open("README.md", 'r') as fp:
    long_description = fp.read()

setuptools.setup(
    name="comptox_ai",
    version="0.0.1a",
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
        "Operating System :: Unix"
    ],
    python_requires='>=3.7',
)
