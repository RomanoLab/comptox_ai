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
  def __init__(self, parent_db, name):
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

    self._db = parent_db
    self.name = name

class GraphDB(object):
  def __init__(self, config_file=None, verbose=True):
    """
    A Neo4j graph database containing ComptoxAI graph data.
    """
    self.is_connected = False

    if not config_file:
      self.config_file = _get_default_config_file()
    else:
      self.config_file = config_file

    self._connect()

  def _connect(self):
    assert self.config_file is not None

    cnf = configparser.ConfigParser()
    cnf.read(self.config_file)

    ipdb.set_trace()

    username = cnf["NEO4J"]["Username"]
    password = cnf["NEO4J"]["Password"]
    uri = "bolt://localhost:7687"

    self._driver = GraphDatabase.driver(uri, auth=(username, password))

  def _disconnect(self):
    self._driver.close()

  @staticmethod
  def _run_transaction(tx, query):
    result = tx.run(query)
    return result.values()

  def _run_cypher(self, qry_str):
    with self._driver.session() as session:
      res = session.write_transaction(self._run_transaction, query_str)
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
                                    relationship_proj, config_dict):
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
    
    Examples
    --------
    >>> g = GraphDB()
    >>> g.build_graph_native_projection(...)
    >>> 
    """

    create_graph_query_template = """
    CALL gds.graph.create(
      graphName: {0},
      nodeProjection: {1},
      relationshipProjection: {2},
      configuration: {3}
    )
    YIELD graphName, nodeCount, relationshipCount, createMillis;
    """[1:-1]

    graph_name_str = "'{0}'".format(graph_name)
    node_proj_str = "'{0}'".format(node_proj)
    relationship_proj_str = "'{0}'".format(relationship_proj)
    config_dict_str = str(config_dict)

    create_graph_query = create_graph_query_template.format(
      graph_name_str,
      node_proj_str,
      relationship_proj_str,
      config_dict_str
    )

    res = self._run_cypher(create_graph_query)

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

    res = self._run_cypher(create_graph_query)

    return res

  def fetch_nodes(self, nodes):
    pass

  def fetch_edges(self, edges):
    pass

  def get_features(self, graph):
    """
    Fetch arrays of features corresponding to entities in a graph from MongoDB.
    """
    pass