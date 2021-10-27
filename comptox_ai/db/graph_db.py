"""ComptoxAI's main interface with Neo4j.

This class and its methods maintain a connection to either a local or remote
instance of the ComptoxAI graph database, and provide convenient access to the
database's contents.

"""

# Authors: Joseph D. Romano <joseph.romano@pennmedicine.upenn.edu>
#
# Copyright: (c) 2021 by Joseph D. Romano
#
# License: MIT License

from logging import warn
import os
import warnings
from pathlib import Path
from neo4j.api import Version
from yaml import load, Loader
from dataclasses import dataclass
from typing import List, Dict
from textwrap import dedent

import ipdb

from neo4j import GraphDatabase
from neo4j.exceptions import ClientError, AuthError, CypherSyntaxError, ServiceUnavailable


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
  A metagraph containing the node types and relationship types (and their
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


def _validate_config_file_contents(conf):
  """Validate the contents of a ComptoxAI config file.

  If anything doesn't pass the validations, a warning is displayed and this
  function returns False. Otherwise, no warning is given and the function
  returns True.
  """
  if 'neo4j' not in conf:
    warnings.warn("Warning: No `neo4j` block found in config file")
    return False

  for val in ['username', 'password', 'hostname', 'port']:
    if (val not in conf['neo4j']):
      warnings.warn("Warning: No value given for `{0}`".format(val))
      return False

  return True


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
  def __init__(self, config_file=None, verbose=False, username=None, password=None, hostname=None):
    self.is_connected = False
    self.verbose = verbose

    if not config_file:
      if hostname:
        self.config_file = None
        self.username = username
        self.password = password
        self.hostname = hostname
      else:
        self.config_file = _get_default_config_file()
    else:
      self.config_file = config_file

    self._connect()

  def __repr__(self):
    return(
      dedent(f"""\
        ------------------------
        ComptoxAI graph database
        ------------------------
        Hostname: {self.hostname}
        Username: {self.username}
        
        Statistics
        ----------
        Node count:       {self.graph_stats['nodeCount']}
        Edge count:       {self.graph_stats['relCount']}
        Node type count:  {self.graph_stats['labelCount']}
        Edge type count:  {self.graph_stats['relTypeCount']}""")
    )

  def _connect(self):
    if self.config_file is not None:
      try:
        with open(self.config_file, 'r') as fp:
          cnf = load(fp, Loader=Loader)
      except FileNotFoundError as e:
        raise RuntimeError("Config file not found at the specified location - using default configuration")

      if not _validate_config_file_contents(cnf):
        raise RuntimeError("Config file has an invalid format. Please see `CONFIG-default.yaml`.")
        
      username = cnf['neo4j']['username']
      password = cnf['neo4j']['password']
      hostname = cnf['neo4j']['password']
      
    else:
      username = self.username
      password = self.password
      hostname = self.hostname

    if hostname == 'localhost':
      uri = "bolt://localhost:7687"
    else:
      uri = f"neo4j://{hostname}"

    # Create the graph database driver
    try:
      if (username is None) and (password is None):
        self._driver = GraphDatabase.driver(uri)
      else:
        self._driver = GraphDatabase.driver(uri, auth=(username, password))
    except AuthError as e:
      raise RuntimeError("Could not find a database using the configuration provided.")

    # Test the connection to make sure we are connected to a database
    try:
      with warnings.catch_warnings():
        warnings.filterwarnings("ignore", "The configuration may change in the future.")
        conn_result = self._driver.verify_connectivity()
    except ServiceUnavailable:
      raise RuntimeError("Neo4j driver created but we couldn't connect to any routing servers. You might be using an invalid hostname.")
    except ValueError:
      raise RuntimeError("Neo4j driver created but the host address couldn't be resolved. Check your hostname, port, and/or protocol.")
    
    if (conn_result is None):
      raise RuntimeError("Neo4j driver created but a valid connection hasn't been established. You might be using an invalid hostname.")

    self.graph_stats = self.get_graph_statistics()

  def _disconnect(self):
    self._driver.close()

  @staticmethod
  def _run_transaction(tx, query):
    result = tx.run(query)
    return result.data()

  def run_cypher(self, qry_str, verbose=True):
    """
    Execute a Cypher query on the Neo4j graph database.

    The 

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
      if self.verbose or verbose:
        print(f"Writing Cypher transaction: \n  {qry_str}")
      try:
        res = session.write_transaction(self._run_transaction, qry_str)
      except CypherSyntaxError as e:
        warnings.warn("Neo4j returned a Cypher syntax error. Please check your query and try again.")
        print(f"\nThe original error returned by Neo4j is:\n\n {e}")
        return None
      return res

  def get_graph_statistics(self):
    """Fetch statistics for the connected graph database.

    This method essentially calls APOC.meta.stats(); and formats the output.

    Returns
    -------
    dict
      Dict of statistics describing the graph database.

    Raises
    ------
    RuntimeError
      If not currently connected to a graph database or the APOC.meta
      procedures are not installed/available.
    """
    qry = "CALL apoc.meta.stats();"
    response = self.run_cypher(qry)
    assert len(response) == 1

    response = response[0]

    stats = {k:response[k] for k in ('nodeCount', 'relCount', 'labelCount', 'relTypeCount') if k in response}
    
    return stats

  def fetch(self, field, operator, value, what='both', register_graph=True,
            negate=False, query_type='cypher', **kwargs):
    """
    Create and execute a query to retrieve nodes, edges, or both.

    Warnings
    --------
    This function is incomplete and should not be used until we can fix its
    behavior. Specifically, Neo4j's GDS library does not support non-numeric
    node or edge properties in any of its graph catalog-related subroutines.

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

    raise NotImplementedError("Error: GraphDB.fetch() not yet implemented - see documentation notes.")

    if query_type == 'cypher':
      new_graph = self.build_graph_cypher_projection()
    elif query_type == 'native':
      new_graph = self.build_graph_native_projection()
    else:
      raise ValueError("'query_type' must be either 'cypher' or 'native'")

    # consume results

    # (optionally) build Graph object

    # Return results to user

  def find_node(self, name=None, properties=None):
    """
    Find a single node either by name or by property filter(s).
    """
    if name:
      # search by name
      query = "MATCH (n {{ commonName: \"{0}\" }}) RETURN n LIMIT 1;".format(name)

    else:
      if not properties:
        raise ValueError("Error: Must provide a value for `name` or `properties`.")

      # search by properties
      # first, separate out properties with special meaning (e.g., `id`)

      # then, construct a MATCH clause suing the remaining properties
      # strings should be enclosed in 
      prop_string = ", ".join([f"{k}: '{v}'" if type(v) == str else f"{k}: {v}" for k, v in properties.items()])
      match_clause = f"MATCH (n {{ {prop_string} }})"
      # assemble the complete query

      query = f"{match_clause} RETURN n;"

    node_response = self.run_cypher(query)

    if len(node_response) < 1:
      warnings.warn("Warning: No node found matching the query you provided.")
      return False
    elif len(node_response) > 1:
      warnings.warn("Warning: Multiple nodes found for query - only returning one (see `find_nodes` if you want all results).")
    
    return node_response[0]['n']


  def find_nodes(self, properties={}, node_types=[]):
    """
    Find multiple nodes by node properties and/or labels.

    Parameters
    ----------
    properties : dict
      Dict of property values to match in the database query. Each key of
      `properties` should be a (case-sensitive) node property, and each value
      should be the value of that property (case- and type-sensitive).
    node_types : list of str
      Case sensitive list of strings representing node labels (node types) to
      include in the results. Two or more node types in a single query may
      significantly increase runtime. When multiple node labels are given, the
      results will be the union of all property queries when applied

    Returns
    -------
    generator of dict
      A generator containing dict representations of nodes matching the given
      query.

    Notes
    -----
    The value returned in the event of a successful query can be extremely
    large. To improve performance, the results are returned as a generator
    rather than a list.
    """
    if (not properties) and (len(node_types) == 0):
      raise ValueError("Error: Query must contain at least one node property or node type.")

    if not properties:
      warnings.warn("Warning: No property filters given - the query result may be very large!")

    prop_string = ", ".join([f"{k}: '{v}'" if type(v) == str else f"{k}: {v}" for k, v in properties.items()])

    # Use a WHERE clause when multiple node types are given
    if len(node_types) == 1:
      # Only 1 node label - include it in the MATCH clause
      match_clause = f"MATCH (n:{node_types[0]} {{ {prop_string} }})"
      where_clause = ""
    elif len(node_types) > 1:
      # Multiple node labels - include them in the WHERE clause
      match_clause = f"MATCH (n {{ {prop_string} }})"
      where_clause = " WHERE n:"+" OR n:".join(node_types)
    else:
      # No node labels - just use bare MATCH clause and no WHERE clause
      match_clause = f"MATCH (n {{ {prop_string} }})"
      where_clause = ""

    query = match_clause + where_clause + " RETURN n;"

    print(query)

    nodes_response = self.run_cypher(query)

    return (n['n'] for n in nodes_response)

  def find_relationships(self):
    """
    Find relationships by subject/object nodes and/or relationship type.
    """
    pass

  def build_graph_native_projection(self, graph_name, node_types,
                                    relationship_types="all", config_dict=None):
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

    node_proj_str = self._make_node_projection_str(node_types)

    # relationship_proj_str = "'{0}'".format(relationship_proj)
    relationship_proj_str = self._make_node_projection_str(relationship_types)

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
      # We need to wrap any string in double quotes
      if node_proj_arg == 'all':
        return '"*"'
      # e.g., 'Chemical'
      return f'"{node_proj_arg}"'
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

  def export_graph(self, graph_name, to='db'):
    """
    Export a graph stored in the GDS graph catalog to a set of CSV files.

    Parameters
    ----------
    graph_name : str
      A name of a graph, corresponding to the `'graphName'` field in the
      graph's entry within the GDS graph catalog.
    """
    if to == 'csv':
      res = self.run_cypher(f"CALL gds.beta.graph.export('{graph_name}', {{exportName: '{graph_name}'}})")
    elif to == 'db':
      res = self.run_cypher(f"CALL gds.graph.export('{graph_name}', {{dbName: '{graph_name}'}});")
    return res

  def stream_named_graph(self, graph_name):
    """
    Stream a named GDS graph into Python for further processing.

    Parameters
    ----------
    graph_name : str
      A name of a graph in the GDS catalog.
    """
    stream_graph_query = f"CALL gds.graph.streamNodeProperties('{graph_name}', "
    node_props = self.run_cypher(stream_graph_query)

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

    
