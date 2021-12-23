#!/usr/bin/env python3

"""
make_qsar.py : Connect to ComptoxAI, extract a QSAR dataset with user-defined
endpoints, and return it in tabular format.
"""

import argparse
import asyncio

import ipdb

from comptox_ai.db import GraphDB


parser = argparse.ArgumentParser(description='Connect to ComptoxAI, extract a QSAR dataset with user-defined endpoints, and return it in tabular format.')
parser.add_argument('--endpoint', type=str, help='An entity type in the graph database corresponding to the endpoint for the QSAR analysis. Examples include Pathway, Gene, and Assay.')

args = parser.parse_args()

def print_dataset_statistics(subgraph):
  print()
  print(f"Number of nodes: {len(subgraph['nodes'])}")
  print(f"Number of edges (relationships): {len(subgraph['relationships'])}")
  print()

# async def get_subgraph(**kwargs)

async def main():
  
  db = GraphDB(hostname="165.123.13.192")

  print(f"Endpoint: {args.endpoint}")

  print("Extracting QSAR dataset from ComptoxAI; please be patient...")

  subgraph_args = {
    'node_types': ['Chemical', args.endpoint]
  }

  # TODO: Make async flashing cursor, or something along those lines
  # subgraph = 
  # subgraph = db.exporter.stream_subgraph(node_types = ['Chemical', args.endpoint])
  subgraph = db.exporter.stream_tabular_dataset(
    sample_node_type="Chemical",
    sample_filter_node_type="ChemicalList",
    sample_filter_node_value="EPAHFR"
    target_node_type="Assay",
    target_match_property="commonName",
    target_match_value="tox21-erb-bla-p1",
  )

  print_dataset_statistics(subgraph)

  ipdb.set_trace()