"""Input/output routines for ComptoxAI's graph database

io.py

Copyright (c) 2021 by Joseph D. Romano
"""



from yaml import load, Loader
from operator import itemgetter
from pathlib import Path
import pandas as pd
import uuid
import datetime as dt
import numpy as np
import pandas as pd

import ipdb


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
  def __init__(self, db):
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
  from comptox_ai.db import GraphDB

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
  from comptox_ai.db import GraphDB
  
  def __init__(self, db: GraphDB):
    super().__init__(db)

  def stream_tabular_dataset(
    self,
    sample_node_type: str = 'Chemical',
    sample_filter_node_type: str = 'ChemicalList',
    sample_filter_node_value: str = 'EPAPCS',
    target_node_type: str = 'Assay',
    target_match_property: str = 'commonName',
    target_match_value: str = 'tox21-pxr-p1',
    target_pos_relationship_type: str = 'CHEMICALHASACTIVEASSAY',
    target_neg_relationship_type: str = 'CHEMICALHASINACTIVEASSAY',
    make_discovery_dataset: bool = False):
    """
    Example
    -------
    >>> g = GraphDB("comptox.ai")
    >>> exporter = TabularExporter(g)
    >>> exporter.stream_tabular_dataset(
    ...   sample_node_type = 'Chemical',
    ...   sample_filter_node_type = 'ChemicalList',
    ...   sample_filter_node_value = 'EPAPCS',
    ...   target_node_type = 'Assay',
    ...   target_match_property = 'commonName',
    ...   target_match_value = 'tox21-pxr-p1',
    ...   target_pos_relationship_type = 'CHEMICALHASACTIVEASSAY',
    ...   target_neg_relationship_type = 'CHEMICALHASINACTIVEASSAY'
    ... )
    """

    cypher_query_template = "MATCH {0} WHERE {1} RETURN {2};"

    if not make_discovery_dataset:
      match_clause = f"(sf:{sample_filter_node_type})-[r2]-(s:{sample_node_type})-[r1]-(t:{target_node_type})"

      where_clause = f"s.maccs IS NOT NULL AND sf.listAcronym = \"{sample_filter_node_value}\" AND t.{target_match_property} = \"{target_match_value}\""

      return_clause = f"s.commonName AS name, s.maccs AS maccs, type(r1) AS rel_type"

      cypher_query = cypher_query_template.format(match_clause, where_clause, return_clause)

      res = self.db.run_cypher(cypher_query)

      X = np.array([x['maccs'] for x in res])
      y = np.array([1 if x['rel_type'] == target_pos_relationship_type else 0 for x in res ], dtype=np.int32)

      names = [x['name'] for x in res]

      df = pd.DataFrame(X)
      df['y'] = y
      df.index = names

      return df

    else:
      # Generate a dataset without known links to the target
      match_clause = f"(sf:{sample_filter_node_type})-[r2]-(s:{sample_node_type})"

      where_clause = f"s.maccs IS NOT NULL AND sf.listAcronym = \"{sample_filter_node_value}\" AND NOT (s)-[]-(:{target_node_type} {{ {target_match_property}: \"{target_match_value}\" }})"

      return_clause = f"s.commonName AS name, s.maccs AS maccs"

      cypher_query = cypher_query_template.format(match_clause, where_clause, return_clause)

      res = self.db.run_cypher(cypher_query)
      
      X = np.array([x['maccs'] for x in res])

      names = [x['name'] for x in res]

      df = pd.DataFrame(X)
      df.index = names

      return df

def get_node_statistics(statistic, node_type: str = None):
  """
  Retrieve a specific statistic for nodes, optionally of a single node type.

  Parameters
  ----------
  statistic : {'degree'}
    The statistic to retrieve. See below for details.
  node_type : str
    Node type (label) to retrieve. E.g., `'Chemical'`.
  top_n : int or None, default 1000
    Number of nodes to retrieve statistics for, sorted by 'top' values. Top
    value ordering is semantically specific to the statistic. E.g., `'degree'`
    will sort in descending order.

  Returns
  -------
  pandas.DataFrame
    Data frame containing node identifiers, node name, and the desired
    statistic values.

  Notes
  -----
  `'degree'` is the total number of incident edges to the node in question.

  """
  if node_type == 'degree':
     query_res = _get_node_degrees(node_type)
  else:
    raise ValueError(f"Error - statistic {node_type} not currently recognized or supported.")

def _get_node_degrees(graph_db, node_type_label: str, extra_id: str, limit: int = 1000):
  safe_label = node_type_label.capitalize()
  if limit:
    limit_clause = f"LIMIT {limit}"
  else:
    limit_clause = ""
  
  degree_query = f"""
  CALL gds.degree.stream(
      {{
          nodeProjection: "*",
          relationshipProjection: "*",
          orientation: "UNDIRECTED"
      }}
  ) YIELD
  nodeId, score
  WITH
      gds.util.asNode(nodeId).commonName AS name,
      score AS degree,
      LABELS(gds.util.asNode(nodeId)) AS labels,
      gds.util.asNode(nodeId).{extra_id} AS {extra_id}
  WHERE '{safe_label}' IN labels AND {extra_id} IS NOT NULL
  RETURN name, nodeId, {extra_id}, degree
  ORDER BY degree DESC, name DESC
  {limit_clause};
  """

  return graph_db.run_cypher(degree_query)