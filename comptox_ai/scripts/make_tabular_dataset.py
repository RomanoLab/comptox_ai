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

from yaml import load, Loader
from pathlib import Path
import pandas as pd
import ipdb
import os
import datetime as dt


def _get_default_config_file():
  root_dir = Path(__file__).resolve().parents[2]
  if os.path.exists(os.path.join(root_dir, 'CONFIG.yaml')):
    default_config_file = os.path.join(root_dir, 'CONFIG.yaml')
  else:
    default_config_file = os.path.join(root_dir, 'CONFIG-default.yaml')
  return default_config_file

def _make_timestamped_output_directory(parent_dir, prefixes=['subgraph', 'tsv'], suffixes=None):
  ts = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
  pre = f"{'-'.join(prefixes)}_" if prefixes else ""
  post = f"_{'-'.join(suffixes)}" if suffixes else ""

  dirname = f"{pre}{ts}{post}"
  full_path = os.path.join(parent_dir, dirname)

  os.makedirs(full_path)

  return full_path


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

OUTPUT_TYPE = 'tsv'

# Instead of what we described above, we will instead let Python do much of the
# heavy lifting. First we get the meta structure of the graph using APOC, we
# then determine the minimum spanning subtree over the metagraph, and then
# export all of the node types and relationship types contained in that tree.
metagraph = db.get_metagraph()

node_tables = dict()
rel_tables = dict()

# get node data
for nl in metagraph.node_labels:
  if nl in NODE_LABELS:
    # print(f"Loading {nl} nodes...")
    node_table = make_node_table(db, nl)
    print(f"    Adding node table: {nl}")
    node_tables[nl] = node_table

# get relationship data
for rt in metagraph.relationship_types:
  
  this_rel_table = pd.DataFrame(columns=['s', 'r', 'o'])

  for rt_s in metagraph.relationship_path_schema[rt]:
    from_label = rt_s['from']
    to_label = rt_s['to']
    
    # The induced subgraph only includes edges where both the subject and the
    # object of the relationship are members of NODE_LABELS
    if (from_label in NODE_LABELS) and (to_label in NODE_LABELS):
      print(f"    Loading relationships for rel type {rt}...")
      rel_table = make_relationship_table(db, rt, from_label, to_label)

      # Note that we need to make a copy of the data and then reassign. Pandas
      # doesn't have decent support for large-scale in-place operations. A
      # possible solution is to somehow use HDFStore tables during the process.
      this_rel_table = this_rel_table.append(rel_table, ignore_index=True)

  # Only hold onto the dataframe if it contains rows
  if this_rel_table.shape[0] > 0:
    print("Adding relationship table: {from_label}-[{rt}]->{to_label}")
    rel_tables[rt] = this_rel_table
  else:
    del(this_rel_table)


print()
print("Finished parsing nodes and relationships; now writing to disk...")

# export the results
config_file_path = _get_default_config_file()
with open(config_file_path, 'r') as fp:
  cnf = load(fp, Loader=Loader)

output_directory = cnf['data']['output_dir']

if OUTPUT_TYPE == 'tsv':
  output_dir = _make_timestamped_output_directory(output_directory)
  
  for k_node, v_node in node_tables.items():
    node_fname = os.path.join(output_dir, f"node_{k_node}.tsv")
    v_node.to_csv(node_fname, sep="\t", index=None)
    print(f"Wrote node file: {node_fname}")

  for k_rel, v_rel in rel_tables.items():
    rel_fname = os.path.join(output_dir, f"edge_{k_rel}.tsv")
    v_rel.to_csv(rel_fname, sep="\t", index=None)
    print(f"Wrote edge file: {rel_fname}")