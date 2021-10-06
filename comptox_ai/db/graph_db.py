"""Neo4j graph database interface.

comptox_ai/db/graph_db.py

Copyright (c) 2020 by Joseph D. Romano
"""

from numpy.lib.arraysetops import ediff1d

import os
from pathlib import Path
from yaml import load, Loader
from dataclasses import dataclass
from typing import List, Dict

from neo4j import GraphDatabase
from neo4j.exceptions import ClientError

import pandas as pd
#from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import numpy as np


def _get_default_config_file():
  root_dir = Path(__file__).resolve().parents[2]
  if os.path.exists(os.path.join(root_dir, 'CONFIG.yaml')):
    default_config_file = os.path.join(root_dir, 'CONFIG.yaml')
  else:
    default_config_file = os.path.join(root_dir, 'CONFIG-default.yaml')
  return default_config_file

@dataclass
class Metagraph:
  """
  A metagraph showing the node types and relationship types (and their
  connectivity) in the overall graph database.

  Parameters
  ----------
  node_labels : list of str
    A list of node labels in the graph database.
  node_label_counts : dict of int
    A mapping from all node labels in `node_labels` to the corresponding number
    of nodes of that type in the graph database.
  relationship_types : list of str
    A list of relationship types in the graph database.
  relationship_path_schema : dict of list
    A mapping from each relationship type present in the graph database to a
    list describing valid (subject, object) pairs (in other words, all existing
    'from' node types and 'to' node types linked by the given relationship).
  """
  node_labels: List[str]
  node_label_counts: Dict[str, int]
  relationship_types: List[str]
  relationship_path_schema: Dict[str, Dict[str, int]]

class Graph(object):
  """
  A Neo4j graph, as defined by the Neo4j Graph Data Science Library. In
  general, users shouldn't instantiate this class directly - let a GraphDB
  instance handle that for you instead.

  See https://neo4j.com/docs/graph-data-science/current/management-ops/.

  Parameters
  ----------
  parent_db : comptox_ai.db.GraphDb
      A Neo4j graph database object, as defined in ComptoxAI.
  name : str
      A name that can be used to identify the graph.
  """

  def __init__(self, parent_db, name):
    self._db = parent_db
    self.name = name

class GraphDB(object):
  """
  A Neo4j graph database containing ComptoxAI graph data.

  Parameters
  ----------
  config_file : str, default None
    Relative path to a config file containing a "NEO4J" block, as described
    below. If None, ComptoxAI will look in the ComptoxAI root directory for
    either a "CONFIG.cfg" file or "CONFIG-default.cfg", in that order. If no
    config file can be found in any of those locations, an exception will be
    raised.
  verbose: bool, default True
    Sets verbosity to on or off. If True, status information will be returned
    to the user occasionally.
  """
  def __init__(self, config_file=None, verbose=True):
    self.is_connected = False
    self.verbose = verbose

    if not config_file:
      self.config_file = _get_default_config_file()
    else:
      self.config_file = config_file

    self._connect()

  def _connect(self):
    assert self.config_file is not None

    # cnf = configparser.ConfigParser()
    # cnf.read(self.config_file)
    with open(self.config_file, 'r') as fp:
      cnf = load(fp, Loader=Loader)

    username = cnf['neo4j']['username']
    password = cnf['neo4j']['password']
    
    uri = "bolt://localhost:7687"

    self._driver = GraphDatabase.driver(uri, auth=(username, password))

  def _disconnect(self):
    self._driver.close()

  @staticmethod
  def _run_transaction(tx, query):
    result = tx.run(query)
    return result.data()

  def run_cypher(self, qry_str, verbose=False):
    """
    Evaluate a Cypher query on the Neo4j graph database.

    Parameters
    ----------
    qry_str : str
      A string containing the Cypher query to run on the graph database server.

    Returns
    -------
    list
      The data returned in response to the Cypher query.

    Examples
    --------
    >>> from comptox_ai.db import GraphDB
    >>> g = GraphDB()
    >>> g.run_cypher("MATCH (c:Chemical) RETURN COUNT(c) AS num_chems;")
    [{'num_chems': 719599}]
    """
    with self._driver.session() as session:
      if self.verbose:
        print(f"Writing Cypher transaction: \n  {qry_str}")
      res = session.write_transaction(self._run_transaction, qry_str)
      return res

  def fetch(self, field, operator, value, what='both', register_graph=True,
            negate=False, query_type='cypher', **kwargs):
    """
    Create and execute a query to retrieve nodes, edges, or both.

    Parameters
    ----------
    field : str
        A property label.
    what : {'both', 'nodes', edges'}
        The type of objects to fetch from the graph database. Note that this
        functions independently from any subgraph registered in Neo4j during
        query execution - if `register_graph` is `True`, an induced subgraph
        will be registered in the database, but the components returned by this
        method call may be only the nodes or edges contained in that subgraph.
    filter : str
        'Cypher-like' filter statement, equivalent to a `WHERE` clause used in
        a Neo4j Cypher query (analogous to SQL `WHERE` clauses). 
    query_type : {'cypher', 'native'}
        Whether to create a graph using a Cypher projection or a native
        projection. The 'standard' approach is to use a Cypher projection, but
        native projections can be (a.) more highly performant and (b.) easier
        for creating very large subgraphs (e.g., all nodes of several or more
        types that exist in all of ComptoxAI). See "Notes", below, for more
        information, as well as https://neo4j.com/docs/graph-data-science/current/management-ops/graph-catalog-ops/#catalog-graph-create.
    """

    if query_type == 'cypher':
      new_graph = self.build_graph_cypher_projection()
    elif query_type == 'native':
      new_graph = self.build_graph_native_projection()
    else:
      raise ValueError("'query_type' must be either 'cypher' or 'native'")

    # consume results

    # (optionally) build Graph object

    # Return results to user

  def build_graph_native_projection(self, graph_name, node_proj,
                                    relationship_proj, config_dict={'nodeProperties': '*'}):
    """
    Create a new graph in the Neo4j Graph Catalog via a native projection.

    Parameters
    ----------
    graph_name : str
      A (string) name for identifying the new graph. If a graph already exists
      with this name, a ValueError will be raised.
    node_proj : str, list of str, or dict of 
      Node projection for the new graph. This can be either a single node
      label, a list of node labels, or a node projection

    Notes
    -----

    ComptoxAI is meant to hide the implementation and usage details of graph
    databases from the user, but some advanced features do expose the syntax
    used in the Neo4j and MongoDB internals. This is especially true when
    building graph projections in the graph catalog. The following components

    NODE PROJECTIONS:

    *(corresponding argument: `node_proj`)*

    Node projections take the following format::

      {
        <node-label-1>: {
            label: <neo4j-label>,
            properties: <node-property-mappings>
        },
        <node-label-2>: {
            label: <neo4j-label>,
            properties: <node-property-mappings>
        },
        // ...
        <node-label-n>: {
            label: <neo4j-label>,
            properties: <node-property-mappings>
        }
      }

    where ``node-label-i`` is a name for a node label in the projected graph 
    (it can be the same as or different from the label already in neo4j),
    ``neo4j-label`` is a node label to match against in the graph database, and
    ``node-property-mappings`` are filters against Neo4j node properties, as
    defined below.

    NODE PROPERTY MAPPINGS:

    RELATIONSHIP PROJECTIONS:
    
    Examples
    --------
    >>> g = GraphDB()
    >>> g.build_graph_native_projection(
      graph_name = "g1",
      node_proj = ['Gene', 'StructuralEntity'],
      relationship_proj = "*"
    )
    >>> 
    """

    create_graph_query_template = """
    CALL gds.graph.create({0},{1},{2}{3})
    YIELD graphName, nodeCount, relationshipCount, createMillis;
    """[1:-1]

    graph_name_str = "'{0}'".format(graph_name)

    node_proj_str = self._make_node_projection_str(node_proj)

    # relationship_proj_str = "'{0}'".format(relationship_proj)
    relationship_proj_str = self._make_node_projection_str(relationship_proj)

    #config_dict_str = str(config_dict)
    if config_dict is None:
      config_dict_str = ""
    else:
      config_dict_str = ", {0}".format(str(config_dict))

    create_graph_query = create_graph_query_template.format(
      graph_name_str,
      node_proj_str,
      relationship_proj_str,
      config_dict_str
    )

    if self.verbose:
      print(create_graph_query)

    res = self.run_cypher(create_graph_query)

    return res

  def build_graph_cypher_projection(self, graph_name, node_query,
                                    relationship_query, config_dict=None):
    """
    Create a new graph in the Neo4j Graph Catalog via a Cypher projection.

    Examples
    --------
    >>> g = GraphDB()
    >>> g.build_graph_cypher_projection(...)
    >>> 
    """
    
    create_graph_query_template = """
    CALL gds.graph.create.cypher({0},{1},{2}{3})
    YIELD graphName, nodeCount, relationshipCount, createMillis;
    """[1:-1]

    graph_name_str = "'{0}'".format(graph_name)
    node_query_str = "'{0}'".format(node_query)
    relationship_query_str = "'{0}'".format(relationship_query)

    if config_dict is None:
      config_dict_str = ""
    else:
      config_dict_str = ", configuration: {0}".format(str(config_dict))

    create_graph_query = create_graph_query_template.format(
      graph_name_str,
      node_query_str,
      relationship_query_str,
      config_dict_str
    )

    if self.verbose:
      print(create_graph_query)

    res = self.run_cypher(create_graph_query)

    return res

  def _make_node_projection_str(self, node_proj_arg):
    if isinstance(node_proj_arg, str):
      # e.g., 'Chemical'
      return node_proj_arg
    elif isinstance(node_proj_arg, list):
      # e.g., ['Chemical', 'Disease']
      return '{0}'.format(str(node_proj_arg))
    elif isinstance(node_proj_arg, dict):
      return

  def _make_rel_projection_str(self, rel_proj_arg):
    pass

  def fetch_nodes(self, node_label):
    """
    Fetch nodes from the Neo4j graph database.

    Returns
    -------
    generator of dict

    """
    
    res = self.run_cypher(f"MATCH (n:{node_label}) RETURN n;")

    return (r['n'] for r in res)


  def fetch_relationships(self, relationship_type, from_label, to_label):
    """
    Fetch edges (relationships) from the Neo4j graph database.
    """
    
    res = self.run_cypher(f"MATCH (s:{from_label})-[r:{relationship_type}]->(o:{to_label}) RETURN s, r, o;")

    return ((r['r'][0]['uri'], r['r'][1], r['r'][2]['uri']) for r in res)

  def get_metagraph(self):
    """
    Examine the graph and construct a metagraph, which describes all of the
    node types and relationship types in the overall graph database.

    Notes
    -----
    We currently don't run this upon GraphDB instantiation, but it may be
    prudent to start doing that at some point in the future. It's not an
    extremely quick operation, but it's also not prohibitively slow.
    """
  
    meta = self.run_cypher("CALL apoc.meta.graph();")[0]
    node_labels = [n['name'] for n in meta['nodes']]
    node_label_counts = dict([(n['name'], n['count']) for n in meta['nodes']])

    rel_types = []
    rel_path_schema = dict()
    for r in meta['relationships']:
      if r[1] not in rel_types:
        rel_types.append(r[1])
        rel_path_schema[r[1]] = []
      
      rel_path_schema[r[1]].append({
        'from': r[0]['name'],
        'to': r[2]['name']
      })

    metagraph = Metagraph(
      node_labels=node_labels,
      node_label_counts=node_label_counts,
      relationship_types=rel_types,
      relationship_path_schema=rel_path_schema
    )
    
    return metagraph

  def list_existing_graphs(self):
    """
    Fetch a list of projected subgraphs stored in the GDS graph catalog.

    Returns
    -------
    list
      A list of graphs in the GDS graph catalog. If no graphs exist, this will
      be the empty list ``[]``.
    """
    graphs = self.run_cypher("CALL gds.graph.list();")
    if self.verbose:
      if len(graphs) == 0:
        print("Graph catalog is currently empty.")
      else:
        print("Number of graphs currently in GDS graph catalog: {0}".format(len(graphs)))
    return graphs

  def drop_existing_graph(self, graph_name):
    """
    Delete a single graph from the GDS graph catalog by graph name.

    Parameters
    ----------
    graph_name : str
      A name of a graph, corresponding to the `'graphName'` field in the
      graph's entry within the GDS graph catalog.
    
    Returns
    -------
    dict
      A dict object describing the graph that was dropped as a result of
      calling this method. The dict follows the same format as one of the list
      elements returned by calling `list_current_graphs()`.
    """
    try:
      res = self.run_cypher(
        "CALL gds.graph.drop(\"{0}\")".format(graph_name)
      )
      return res[0]
    except ClientError:
      if self.verbose:
        print("Error: Graph {0} does not exist.".format(graph_name))
      return None

  def drop_all_existing_graphs(self):
    """
    Delete all graphs currently stored in the GDS graph catalog.

    Returns
    -------
    list
      A list of dicts describing the graphs that were dropped as a result of
      calling this method. The dicts  follow the same format as one of the list
      elements returned by calling `list_current_graphs()`.
    """
    current_graphs = self.list_existing_graphs()

    deleted_graphs = list()

    if current_graphs is None:
      if self.verbose:
        print("Warning - the graph catalog is already empty.")
    else:
      for cg in current_graphs:
        deleted_graph = self.drop_existing_graph(cg['graphName'])
        deleted_graphs.append(deleted_graph)

    return deleted_graphs

  def get_features(self, graph):
    """
    Fetch arrays of features corresponding to entities in a graph from MongoDB.
    """
    pass

  def export_graph(self, graph_name):
    """
    Export a graph stored in the GDS graph catalog to a set of CSV files.

    Parameters
    ----------
    graph_name : str
      A name of a graph, corresponding to the `'graphName'` field in the
      graph's entry within the GDS graph catalog.
    """
    res = self.run_cypher(f"CALL gds.beta.graph.export.csv('{graph_name}', {{exportName: '{graph_name}'}})")
    return res

  def stream_named_graph(self, graph_name):
    """
    Stream a named GDS graph into Python for further processing.

    Parameters
    ----------
    graph_name : str
      A name of a graph in the GDS catalog.
    """
    node_props = self.run_cypher(f"CALL gds.graph.streamNodeProperties('{graph_name}', ")

  # TODO: Recycle this code to send graphs to DGL instead of Pytorch Geometric
  # def to_pytorch(self, graph_name, node_list):
  #   """
  #   Construct dataset from exported graph to be used by PyTorch Geometric.

  #   Parameters
  #   ----------
  #   graph_name : str
  #     A name of a graph, corresponding to the `'graphName'` field in the
  #     graph's entry within the GDS graph catalog.
  #   """
  #   dir_abspath = os.path.join(os.getcwd(), 'comptox_ai/db/exports', f"{graph_name}")

  #   ## create dataframe containing all nodes
  #   node_df = pd.DataFrame()
  #   for node in node_list:
  #     node_files = glob.glob(f"{dir_abspath}/nodes_{node}_[0-9].csv")
  #     curr_df = pd.concat([pd.read_csv(fp, names=['id'], index_col=False) for fp in node_files])
  #     curr_df.insert(loc=1, column='type', value=f"{node}")
  #     node_df = pd.concat([node_df, curr_df])

  #   ## map node IDs to indices
  #   node_indices = dict(zip(node_df['id'].to_list(), range(len(node_df['id']))))
  #   node_df['index'] = node_df['id'].map(node_indices)

  #   ## convert node type to one hot encoded values
  #   node_df['type_encoded'] = LabelEncoder().fit_transform(node_df['type'])
  #   ohe = OneHotEncoder(sparse=False).fit_transform(node_df['type_encoded'].values.reshape(len(node_df), 1))
  #   x = torch.LongTensor(ohe)

  #   ## create dataframe containing all edges
  #   edge_files = glob.glob(f"{dir_abspath}/relationships_*_[0-9].csv")
  #   edge_df = pd.concat([pd.read_csv(fp, names=['start_id', 'end_id'], index_col=False) for fp in edge_files])

  #   ## map edges to indices
  #   edge_df['start_index'] = edge_df['start_id'].map(node_indices)
  #   edge_df['end_index'] = edge_df['end_id'].map(node_indices)
  #   edge_index = torch.tensor([edge_df['start_index'].to_numpy(), edge_df['end_index'].to_numpy()], dtype=torch.long)

  #   ## create torch_geometric data object
  #   data = Data(x=x, edge_index=edge_index)
  #   data.train_mask = data.val_mask = data.test_mask = data.y = None

  #   return data

    
