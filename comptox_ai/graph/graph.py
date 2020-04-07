"""
ComptoxAI graphs.

A typical graph workflow looks something like the following:

>>> from comptox_ai import Graph
>>> G = Graph.from_neo4j(config_file = "./CONFIG.cfg")
>>> G.convert_inplace(to='networkx')
>>> A = G.get_adjacency()
>>> GS = G.convert(to='graphsage')
"""

import numpy as np
import scipy.sparse
import networkx as nx
from networkx.readwrite import json_graph
from collections import defaultdict
from py2neo import Database

from abc import abstractmethod
from typing import List, Iterable, Union
import os
import json
from textwrap import dedent

import ipdb

from comptox_ai.cypher import queries
from comptox_ai.utils import execute_cypher_transaction
from comptox_ai.graph.metrics import vertex_count, ensure_nx_available
from ..utils import load_config

from .io import GraphDataMixin, Neo4jData, NetworkXData, GraphSAGEData

def _load_neo4j_config(config_file: str = None):
    config_dict = load_config(config_file)

    if not config_dict:
        raise RuntimeError("Could not load Neo4j configuration; aborting.")

    username = config_dict['NEO4J']['Username']
    password = config_dict['NEO4J']['Password']
    hostname = config_dict['NEO4J']['Hostname']
    protocol = config_dict['NEO4J']['Protocol']
    port = config_dict['NEO4J']['Port']

    uri = "{0}://{1}:{2}".format(protocol, hostname, port)

    return (uri, username, password)


def _convert(data: GraphDataMixin, from_fmt: str, to_fmt: str, safe: bool=True):
    # Initialize the new data structure
    if to_fmt == 'neo4j':
        # TODO: Only compatible with default config file for now
        uri, username, password = _load_neo4j_config()
        db = Database(uri, auth=(username, password))
        new_data = Neo4jData(db)
    elif to_fmt == 'networkx':
        new_data = NetworkXData()
    elif to_fmt == 'graphsage':
        raise NotImplementedError
    elif to_fmt == 'dgl':
        raise NotImplementedError

    # Populate nodes and edges
    nodes = data.nodes
    edges = data.edges
    #ipdb.set_trace()
    new_data.add_nodes(nodes)
    new_data.add_edges(edges)

    return new_data
    

class Graph(object):
    """
    A graph representation of ComptoxAI data.

    The internal data storage can be in several different formats, each of
    which has advantages in different scenarios.

    Read more in the :ref:`User Guide <graph>`.

    Parameters
    ----------
    data : comptox_ai.graph.io.GraphDataMixin
        A graph data structure that is of one of the formats compliant with
        ComptoxAI's standardized graph API.
    
    Attributes
    ----------
    format : {"graphsage", "networkx", "neo4j"}
        Internal format of the graph data. The format determines many aspects
        of how you interact with the graph, including the set of methods that
        can be called on it and the types of models that you can construct
        without first converting to another format.
    """

    def __init__(self, data: GraphDataMixin):
        self._data = data

    def __repr__(self):
        return dedent(
            """
            ComptoxAI Graph
            ---------------
            Format:     {0}
            Node count: {1}
            Edge count: {2}
            """
        ).format(
            self.format,
            len(self._data._nodes),
            len(self._data._edges)
        )

    @property
    def data(self):
        return self._data

    @property
    def format(self):
        return self._data.format

    def nodes(self):
        """
        Get all nodes in the graph and return as an iterable of tuples.
        
        Returns
        -------
        iterable
            Iterable over 2-tuples containing graph nodes. The first element is
            the node's integer ID and the second is the URI of that node (if
            available).
        """
        return self._data.nodes

    def edges(self):
        """
        Get all edges in the graph and return as an iterable of tuples.
        
        Returns
        -------
        iterable
            Iterable over tuples containing graph edge triples.
        """
        return self._data.edges

    def add_nodes(self, nodes: Union[List[tuple], tuple]):
        """
        Add one or more nodes to the graph.
        """
        if isinstance(nodes, tuple):
            self._data.add_node(nodes)
        elif isinstance(nodes, list):
            self._data.add_nodes(nodes)
        else:
            raise AttributeError("`nodes` must be a node tuple or list of node tuples - got {0}".format(type(nodes)))

    def add_edges(self, edges: Union[List[tuple], tuple]):
        """
        Add one or more edges to the graph.
        """
        if isinstance(edges, tuple):
            self._data.add_edge(edges)
        elif isinstance(edges, list):
            self._data.add_edges(edges)
        else:
            raise AttributeError("`edges` must be a node tuple or list of node tuples - got {0}".format(type(edges)))

    def node_id_map(self):
        return self._data._node_map

    def is_heterogeneous(self):
        return self._data._is_heterogeneous

    def classes(self):
        """
        Get a list of ontology classes present in the graph.
        """
        return self._data.node_labels

    def convert(self, to_fmt: str):
        """
        Convert the graph data structure into the specified format.

        The actual graph contained in a `comptox_ai.Graph` can be in a variety
        of different formats. When the user loads a graph 
        """
        if to_fmt not in [
            'neo4j',
            'networkx',
            'graphsage',
            'dgl'
        ]:
            raise AttributeError("Invalid format provided for graph conversion.")

        from_fmt = self._data.format

        if from_fmt == to_fmt:
            return True

        new_graph = _convert(data = self._data,
                             from_fmt=from_fmt,
                             to_fmt=to_fmt)

        # Free memory held for old graph
        #delattr(self, _data)

        self._data = new_graph

    @classmethod
    def from_neo4j(cls, config_file: str = None, verbose: bool = False):
        """Load a connection to a Neo4j graph database and use it to
        instantiate a comptox_ai.graph.io.Neo4j object.

        NOTE: All we do here is create a driver for the graph database; the
        Neo4j constructor handles building the node index and other important
        attributes. This is different from most of the other formats, where
        the attributes are provided by the constructor

        Parameters
        ----------
        config_file : str, default None
            Path to a ComptoxAI configuration file. If None, ComptoxAI will
            search for a configuration file in the default location. For more
            information, refer to http://comptox.ai/docs/guide/building.html.
        
        Raises
        ------
        RuntimeError
            If the data in the configuration file does not point to a valid
            Neo4j graph database.

        See Also
        --------
        comptox_ai.graph.Neo4jData
        """
        if verbose:
            print("Parsing Neo4j configuration...")
        uri, username, password = _load_neo4j_config(config_file)
        if verbose:
            print("  URI:", uri)

        if verbose:
            print("Creating database connection via py2neo...")
        database = Database(uri, auth=(username, password))
        if verbose:
            print("Connected to database, now reading contents")
        neo4j_data = Neo4jData(database = database)

        return cls(data = neo4j_data)

    @classmethod
    def from_networkx(cls):
        """
        Create a new ComptoxAI graph from a JSON node-link graph file, storing
        the data as a NetworkX graph.

        See Also
        --------
        comptox_ai.graph.NetworkXData
        """

        print("Reading NetworkX graph from file...")
        with open("./test_json.json", 'r') as fp:
            graph_text = json.load(fp)

        nx_g = nx.readwrite.json_graph.node_link_graph(graph_text)

        networkx_data = NetworkXData(graph = nx_g)

        return cls(data = networkx_data)

    @classmethod
    def from_graphsage(cls, prefix: str, directory: str=None):
        """
        Create a new GraphSAGE data structure from files formatted according to
        the examples given in https://github.com/williamleif/GraphSAGE.


        Parameters
        ----------
        prefix : str
            The prefix used at the beginning of each file name (see above for
            format specification).
        directory : str, default=None
            The directory (fully specified or relative) containing the data
            files to load.

        See Also
        --------
        comptox_ai.graph.GraphSAGEData

        Notes
        -----

        The parameters should point to files with the following structure:

        {prefix}-G.json
            JSON file containing a NetworkX 'node link' instance of the input
            graph. GraphSAGE usually expects there to be 'val' and 'test'
            attributes on each node indicating if they are part of the
            validation and test sets, but this isn't enforced by ComptoxAI (at
            least not currently).

        {prefix}-id_map.json
            A JSON object that maps graph node ids (integers) to consecutive
            integers (0-indexed).

        {prefix}-class_map.json (OPTIONAL)
            A JSON object that maps graph node ids (integers) to a one-hot list
            of binary class membership (e.g., {2: [0, 0, 1, 0, 1]} means that
            node 2 is a member of classes 3 and 5). NOTE: While this is shown
            as a mandatory component of a dataset in GraphSAGE's documentation,
            we don't enforce that. NOTE: The notion of a class in terms of
            GraphSAGE is different than the notion of a class in heterogeneous
            network theory. Here, a 'class' is a label to be used in a
            supervised learning setting (such as classifying chemicals as
            likely carcinogens versus likely non-carcinogens).

        {prefix}-feats.npy (OPTIONAL)
            A NumPy ndarray containing numerical node features. NOTE: This
            serialization is currently not compatible with heterogeneous
            graphs, as GraphSAGE was originally implemented for
            nonheterogeneous graphs only.

        {prefix}-walks.txt (OPTIONAL)
            A text file containing precomputed random walks along the graph.
            Each line is a pair of node integers (e.g., the second fields in
            the id_map file) indicating an edge included in random walks. The
            lines should be arranged in ascending order, starting with the 
            first item in each pair.
        """

        nx_json_file = os.path.join(directory, "".join([prefix, '-G.json']))
        id_map_file = os.path.join(directory, "".join([prefix, '-id_map.json']))
        class_map_file = os.path.join(directory, "".join([prefix, '-class_map.json']))
        feats_map_file = os.path.join(directory, "".join([prefix, '-feats.npy']))
        walks_file = os.path.join(directory, "".join([prefix, '-walks.txt']))

        G = json_graph.node_link_graph(json.load(open(nx_json_file, 'r')))
        id_map = json.load(open(id_map_file, 'r'))

        try:
            class_map = json.load(open(class_map_file, 'r'))
        except FileNotFoundError:
            class_map = None

        try:
            feats_map = np.load(feats_map_file)
        except FileNotFoundError:
            feats_map = None

        try:
            walks = []
            with open(walks_file, 'r') as fp:
                for l in fp:
                    walks.append(l)
        except FileNotFoundError:
            walks = None

        graph_data = GraphSAGEData(graph=G, node_map=id_map,
                               node_classes=class_map,
                               node_features=feats_map)

        return cls(data = graph_data)

    @classmethod
    def from_dgl(cls):
        """
        Create a ComptoxAI graph, populating the contents from a DGL graph (not
        yet implemented).

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

