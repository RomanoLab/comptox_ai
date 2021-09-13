#!/usr/bin/env python3

"""
make_tabular_dataset.py

Standalone Python job to generate a tabular dataset for predictive toxicology.
Briefly, the user specifies a node type and node features, as well as a target
feature or relationship.

This returns a file that is suitable for QSAR or similar analyses.

The algorithm for extracting a tabular dataset is roughly as follows: First,
the user creates a new 'in memory' graph in the Neo4j GDS library's graph
catalog. This is basically a subgraph of the complete graph database,
originally meant for providing an environment in which users can efficiently
run graph algorithms on relevant portions of the database. However, we co-opt
this functionality to allow rapid exporting of those same subgraphs for use in
external data analysis frameworks (like scikit-learn, networkx, DGL, etc.).
Specifically, we perform a *native projection*, where we supply the entire set
of node types and relationship types in the desired subgraph, along with either
specific node features or all defined node features for those node types. We
then call a routine to stream the graph into local Python data structures.
"""

from comptox_ai.db.graph_db import Graph, GraphDB

import ipdb

# connect to running Neo4j instance
db = GraphDB()

# Build the graph using a native projection
TEST_NODE_PROJ = ['Chemical', 'Gene', 'Assay']
TEST_REL_PROJ = ['CHEMICALBINDSGENE', 'CHEMICALDECREASESEXPRESSION', 'CHEMICALHASACTIVEASSAY']
db.build_graph_native_projection(
  'testgraph',
  TEST_NODE_PROJ,
  TEST_REL_PROJ
)

# Stream node properties back to Python
#db.stream_named_graph()

ipdb.set_trace()

