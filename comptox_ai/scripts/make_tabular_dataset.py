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

import pandas as pd
import ipdb


def make_node_table(db, node_label, node_properties = None):
  if node_properties is None:
    # No filters on properties, so we will just fetch all of them
    res = db.fetch_nodes(node_label)
    res_df = pd.DataFrame(res)
    del(res)
    
  else:
    raise NotImplementedError

  return res_df


def make_relationship_table(db, relationship_type, from_label, to_label, relationship_properties = None):
  if relationship_properties is not None:
    # TODO: Figure out how/if to handle relationship properties if it ever
    # looks like it would be useful.
    raise NotImplementedError

  res = db.fetch_relationships(relationship_type, from_label, to_label)
  res_df = pd.DataFrame(res, columns=['s', 'r', 'o'])
  del(res)
  
  return res_df

# connect to running Neo4j instance
db = GraphDB()


# Ideally, we'd be able to tap into GDS' subgraph projection functionality, but
# it unfortunately isn't compatible with non-numeric node or relationship
# properties. E.g., we store MACCS bitstrings as a string, because Neo4j
# doesn't have a better datatype. Therefore, we couldn't export them using GDS
# alone. We'll be keeping an eye on this, because it should drastically speed
# up the subgraph dataset generation procedure if they can get this to work.
# # Build the graph using a native projection
# TEST_NODE_PROJ = ['Chemical', 'Gene', 'Assay']
# TEST_REL_PROJ = ['CHEMICALBINDSGENE', 'CHEMICALDECREASESEXPRESSION', 'CHEMICALHASACTIVEASSAY']
# db.build_graph_native_projection(
#   'testgraph',
#   TEST_NODE_PROJ,
#   TEST_REL_PROJ
# )

NODE_LABELS = [
  'Gene',
  'Pathway',
  'Assay'
]

# Instead of what we described above, we will instead let Python do much of the
# heavy lifting. First we get the meta structure of the graph using APOC, we
# then determine the minimum spanning subtree over the metagraph, and then
# export all of the node types and relationship types contained in that tree.
metagraph = db.get_metagraph()


# get node data
for nl in metagraph.node_labels:
  if nl in NODE_LABELS:
    print(f"Loading {nl} nodes...")
    node_table = make_node_table(db, nl)

# get relationship data
for rt in metagraph.relationship_types:
  for rt_s in metagraph.relationship_path_schema[rt]:
    from_label = rt_s['from']
    to_label = rt_s['to']
    
    if (from_label in NODE_LABELS) and (to_label in NODE_LABELS):
      print(f"Loading relationships for rel type {rt}...")
      rel_table = make_relationship_table(db, rt, from_label, to_label)


ipdb.set_trace()

