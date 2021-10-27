"""Input/output routines for ComptoxAI's graph database

io.py

Copyright (c) 2021 by Joseph D. Romano
"""

from comptox_ai.db import GraphDB

from yaml import load, Loader
from operator import itemgetter
from pathlib import Path
import pandas as pd
import uuid
import datetime as dt


# FOR DEBUGGING ONLY:
NODE_LABELS = [
  'Gene',
  'Pathway',
  'Assay'
]
OUTPUT_TYPE = 'tsv'

class DbExporter():
  """Base class for exporting subgraphs from ComptoxAI's graph database.

  Notes
  -----
  Users shouldn't usually try to interact with this class directly. They should
  instead call the appropriate `GraphDB` method (e.g., `db.export()`).
  """
  def __init__(self, db: GraphDB):
    self.db = db
    self.metagraph = db.get_metagraph()

class GraphExporter(DbExporter):
  """Exporter for serializing graphs to graph-like formats, meant for
  consumption by graph-based libraries (like DGL, PyTorch Geometric, networkx,
  etc.).

  Notes
  -----
  Users shouldn't usually try to interact with this class directly. They should
  instead call the appropriate `GraphDB` method (e.g., `db.export()`).
  """
  def __init__(self, db: GraphDB, verbose=True):
    super().__init__(db)
    self.verbose = verbose

  def _make_gds_graph(self, nodes, relationships='all'):
    self.uuid = uuid.uuid4()
    self.temp_graph_name = 'a'+self.uuid.hex  # Needs to start with alphabetic char

    self.db.build_graph_native_projection(self.temp_graph_name, nodes, relationships)

  def _make_temp_database(self):
    # Let's make sure we have a named GDS in-memory graph:
    graphs = self.db.list_existing_graphs()

    if not self.temp_graph_name in [x['graphName'] for x in graphs]:
      raise RuntimeError("Something went wrong - we couldn't successfully create the GDS in-memory graph")
    
    # Create a Neo4j DB from the in-memory GDS graph
    self.db.export_graph(graph_name=self.temp_graph_name, to='db')

  def _stream_temp_database(self):
    return self.db.run_cypher(f"CALL apoc.graph.fromDB('{self.temp_graph_name}', {{}});")
    
  def _cleanup(self):
    """Delete in-memory and on-disk objects produced during subgraph export."""
    graphs = self.db.list_existing_graphs()

    if self.uuid.hex in [x['graphName'] for x in graphs]:
      self.db.drop_existing_graph(self.temp_graph_name)

    
    
  def stream_subgraph(self, node_types, relationship_types='all'):
    """Extract a subgraph from the graph database and return it as a Python
    dictionary object.

    Parameters
    ----------
    node_types : list of str
      A list of node types to include in the subgraph. Node type names are
      case-sensitive.
    relationship_types : list or str
      A list of relationship labels (edge types) to include in the subgraph.
      Alternatively, the string `'all'` may be used to denote that all
      relationships in the induced subgraph should be included. Relationship
      type names are case-sensitive.

    Returns
    -------
    dict

    """
    if self.verbose:
      print("Creating subgraph for QSAR dataset...")
    self._make_gds_graph(node_types, relationship_types)
    
    if self.verbose:
      print("Converting subgraph to temporary graph database...")
    self._make_temp_database()
    
    if self.verbose:
      print("Retrieving subgraph (please be patient!)...")
    dataset = self._stream_temp_database()[0]['graph']

    if self.verbose:
      print("Deleting temporary data structures...")
    self._cleanup()

    return {k:dataset[k] for k in ('nodes', 'relationships') if k in dataset}

class TabularExporter(DbExporter):
  """Exporter for serializing graphs to tabular formats, meant for secondary
  processing by 'traditional' (i.e., non-graph-based) tools, such as
  scikit-learn. Such tabular datasets are mainly useful for establishing
  baseline comparisons to the GraphML algorithms that make up the main focus of
  ComptoxAI's models.

  Notes
  -----
  Users shouldn't usually try to interact with this class directly. They should
  instead call the appropriate `GraphDB` method (e.g., `db.export()`).
  """
  def __init__(self, db: GraphDB):
    super().__init__(db)