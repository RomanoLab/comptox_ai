"""
comptox_ai/db/graph_db.py

Copyright (c) 2020 by Joseph D. Romano
"""

import ipdb

import os
import glob
import configparser
from pathlib import Path
from neo4j import GraphDatabase

def _get_default_config_file():
  root_dir = Path(__file__).resolve().parents[2]
  if os.path.exists(os.path.join(root_dir, 'CONFIG.cfg')):
    default_config_file = os.path.join(root_dir, 'CONFIG.cfg')
  else:
    default_config_file = os.path.join(root_dir, 'CONFIG-default.cfg')
  return default_config_file

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

    cnf = configparser.ConfigParser()
    cnf.read(self.config_file)

    username = cnf["NEO4J"]["Username"]
    password = cnf["NEO4J"]["Password"]
    uri = "bolt://localhost:7687"

    self._driver = GraphDatabase.driver(uri, auth=(username, password))

  def _disconnect(self):
    self._driver.close()

  @staticmethod
  def _run_transaction(tx, query):
    result = tx.run(query)
    return result.data()

  def run_cypher(self, qry_str):
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
      res = session.write_transaction(self._run_transaction, qry_str)
      return res

  def fetch(self, field, operator, value, what='both', register_graph=True,
            negate=False, query_type='cypher', **kwargs):
    """
    Create and execute a query to retrieve nodes, edges, or both.

    Parameters
    ----------
    field : str
        A property label 
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
                                    relationship_proj, config_dict=None):
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

    relationship_proj_str = "'{0}'".format(relationship_proj)
    #relationship_proj_str = self._make_rel_projection_str(relationship_proj)

    #config_dict_str = str(config_dict)
    if config_dict is None:
      config_dict_str = ""
    else:
      config_dict_str = ", configuration: {0}".format(str(config_dict))

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
                                    relationship_query, config_dict):
    """
    Create a new graph in the Neo4j Graph Catalog via a Cypher projection.

    Examples
    --------
    >>> g = GraphDB()
    >>> g.build_graph_cypher_projection(...)
    >>> 
    """
    
    create_graph_query_template = """
    CALL gds.graph.create.cypher(
      graphName: {0},
      nodeQuery: {1},
      relationshipQuery: {2},
      configuration: {3}
    )
    YIELD graphName, nodeCount, relationshipCount, createMillis;
    """[1:-1]
    
    graph_name_str = "'{0}'".format(graph_name)
    node_query_str = "'{0}'".format(node_query)
    relationship_query_str = "'{0}'".format(relationship_query)
    config_dict_str = str(config_dict)

    create_graph_query = create_graph_query_template.format(
      graph_name_str,
      node_query_str,
      relationship_query_str,
      config_dict_str
    )

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

  def fetch_nodes(self, nodes):
    """
    Fetch nodes from the Neo4j graph database.
    """
    pass

  def fetch_edges(self, edges):
    """
    Fetch edges (relationships) from the Neo4j graph database.
    """
    pass

  def get_features(self, graph):
    """
    Fetch arrays of features corresponding to entities in a graph from MongoDB.
    """
    pass