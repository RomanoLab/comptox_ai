"""
ComptoxAI
=========

A modern toolkit for AI research in computational toxicology.
"""

import os
from pathlib import Path

#from .comptox_ai import ComptoxAI
#from . import graph
#from . import ontology
#from . import aop

#from . import cypher

### THIS BREAKS ON SOME BUILD SYSTEMS (e.g., TravisCI):
# package_src_dir = Path(__file__).parent.parent
# version_file = open(os.path.join(package_src_dir, 'VERSION'), 'r')
# str_version = version_file.read().strip()
##__version__ = str_version

### INSTEAD:
# PEP0440 compatible formatted version, see:
# https://www.python.org/dev/peps/pep-0440/
#
# Generic release markers:
#   X.Y
#   X.Y.Z   # For bugfix releases
#
# Admissible pre-release markers:
#   X.YaN   # Alpha release
#   X.YbN   # Beta release
#   X.YrcN  # Release Candidate
#   X.Y     # Final release
#
# Dev branch marker is: 'X.Y.dev' or 'X.Y.devN' where N is an integer.
# 'X.Y.dev0' is the canonical version of 'X.Y.dev'
#
__version__ = '0.1.dev0'
## ^^ Will be in dev on master branch until 0.1a is ready to go

from .graph import Graph
#from .db import GraphDB