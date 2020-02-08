"""
Common format for graph data structures in ComptoxAI.

Q: Why do we define so many internal representations of graphs? Shouldn't a
single format be sufficient?

A: The graphs used by ComptoxAI are sufficiently large that it is only
reasonable to store a single copy of the graph in memory at a given time,
unless the user explitly asks for otherwise. Some of the representations are
better for data storage, for information retrieval, for deep learning, etc., so
the best way to handle internal format is to provide a single interface to the
underlying data and a single function that handles conversion between those
types. In the future, we may modify this to a more complex architecture that is
more sustainable.
"""

from abc import abstractmethod
from typing import Iterable, List, Tuple, Union

import networkx as nx
import numpy as np
import pandas as pd
import neo4j
from py2neo import Database, Graph, Subgraph, Node, Relationship

import ipdb

from ..cypher import queries
from ..utils import load_config

def _execute_cypher_transaction(tx, query, **kwargs):
    if kwargs:
        verbose = kwargs['verbose']
    else:
        verbose = False

    records = []
    for record in tx.run(query):
        if verbose:
            print(record)
        records.append(record)
    return records


class GraphDataMixin(object):
    """
    Abstract base class specifying a common interface for all graph data 
    """
    
    @property
    @abstractmethod
    def nodes(self):
        pass

    @property
    @abstractmethod
    def edges(self):
        pass

    @property
    @abstractmethod
    def is_heterogeneous(self):
        pass

    @abstractmethod
    def add_node(self, node: tuple):
        pass
    
    @abstractmethod
    def add_edge(self, edge: tuple):
        pass

    @abstractmethod
    def add_nodes(self, nodes: List(tuple)):
        pass

    @abstractmethod
    def add_edges(self, edges: List(tuple)):
        pass


class GraphSAGE(GraphDataMixin):
    """
    Internal representation of a GraphSAGE formatted graph/dataset.

    This is essentially a NetworkX graph with a few extra data components
    needed to run the GraphSAGE algorithms. It also provides a more flexible
    way to work with node features, which are stored in a separate NumPy array
    (which, unfortunately, isn't natively compatible with heterogeneous
    graphs).

    Parameters
    ----------
    graph : nx.DiGraph
        A NetworkX directed graph containing the nodes and edges that define
        the topology of the ComptoxAI graph database. Nodes are identified by
        the ID assigned to them by Neo4j.
    node_map : Iterable, default=None
        An iterable where each element maps a Neo4j node id (int) to a
        consecutively numbered index, used to map nodes to columns of the
        (optional) matrix of node features. If None, a node map will be
        generated from scratch.
    edge_map : Iterable, default=None
        Currently not implemented (:TODO:)
    node_classes : list of str, default=None
        Membership for classes to be used in supervised learning tasks. NOTE:
        there is a semantic difference between the notion of 'node classes' in
        an ontology / graph database (which specifies the semantic type(s) of
        entities) versus in supervised learning (a target variable used to
        learn a decision function), although they may be equivalent in some
        settings.
    edge_classes : list of str, default=None
        Currently not implemented (:TODO:)
    node_features : array-like, default=None
        Array of node features.
    edge_features : array-like, default=None
        Array of edge features.
    """

    format = 'graphsage'
    
    def __init__(self, graph: nx.DiGraph, node_map: Iterable=None,
                 edge_map: Iterable=None, node_classes: List[str]=None,
                 edge_classes: List[str]=None, 
                 node_features: Union[np.ndarray, pd.DataFrame]=None,
                 edge_features: Union[np.ndarray, pd.DataFrame]=None):
        self._graph = graph

        self._node_map = node_map
        self._edge_map = edge_map

        self._node_classes = node_classes
        self._edge_classes = edge_classes
        
        self._node_features = node_features
        self._edge_features = edge_features

    @property
    def nodes(self):
        return list(self._graph.nodes())

    @property
    def edges(self):
        return self._graph.edges()

    @property
    def is_heterogeneous(self):
        """Return True if graph is heterogeneous, False otherwise.
        """
        # GraphSAGE is (CURRENTLY) only compatible with non-heterogeneous
        # graphs, so we always return False.
        # TODO: Revisit to potentially extend to heterogeneous case.
        return False

    def add_node(self, node: int, **kwargs):
        """
        Add a node to GraphSAGE.
        
        A node is simply an ID corresponding to a node in the Neo4j graph.
        Node features aren't tied to the NetworkX digraph under GraphSAGE,
        instead, they are stored in _node_features.

        Parameters
        ----------
        node : int
            A Neo4j node id
        kwargs : 
        """
        self._graph.add_node(node, **kwargs)

    def add_edge(self, edge: Tuple[int, str, int]):
        """
        Add an edge to GraphSAGE.

        Edge format:
        3-tuple with format:
        (
            {ID of u},
            {relationship label (str)},
            {ID of v}
        )

        If the edge does not have a label, you should use the empty string
        ('') as the second element of `edge`.

        Parameters
        ----------
        edge : Tuple[int, str, int]
            A tuple to add to the GraphSAGE dataset.
        """
        u, rel, v = edge

        if rel != '':
            self._graph.add_edge(u, v, rel=rel)
        else:
            self._graph.add_edge(u, v)

class Neo4j(GraphDataMixin):
    """Internal representation of a connection to a Neo4j graph database
    containing ComptoxAI data.

    Importantly, this data structure does not load the complete contents of the
    database into Python's memory space. This places significantly less demand
    on system resources when not executing large queries or performing complex
    data manipulations. This representation is also able to unload a fair deal
    of logic onto Neo4j's standard library in implementing various standardized
    operations.

    The recommended way to instantiate this class is by calling
    comptox_ai.Graph.from_neo4j(), which handles establishing a database driver
    connection.

    Parameters
    ----------
    driver : neo4j.Driver
        A driver connected to a Neo4j graph database containing ComptoxAI data.
    """

    format = 'neo4j'

    def __init__(self, database: Database):
        #ipdb.set_trace()
        self._graph = database.default_graph

        print("  Reading nodes (this may take a while)...")
        self._nodes = list(self._graph.nodes.match("owl__NamedIndividual"))
        print("  Reading edges (this may take a while)...")
        self._edges = list(self._graph.relationships.match())
        print("  Building index of node IDs...")
        self._node_ids = [n.identity for n in self._nodes]
        print()
        print("Done! The database connection is ready to use.")

    @staticmethod
    def standardize_node(n: Node):
        return ((
            n.identity,
            n.labels - {'Resource', 'owl__NamedIndividual'},
            dict(n)
        ))

    @staticmethod
    def standardize_edge(e: Relationship):
        return ((
            e.start_node.identity,
            list(e.types())[0],
            e.end_node.identity,
            dict(e)
        ))
    
    @property
    def nodes(self):
        """Get a list of all nodes corresponding to a named individual in the
        ComptoxAI ontology.
        
        Returns
        -------
        list of py2neo.Node
            List of all Neo4j nodes corresponding to a named individual.
        """
        return [self.standardize_node(n) for n in self._nodes]

    @property
    def edges(self):
        return [self.standardize_edge(e) for e in self._edges]

    @property
    def is_heterogeneous(self):
        pass

    def add_node(self, node: tuple):
        """
        Add a node to the graph and synchronize it to the remote database.
        
        Parameters
        ----------
        node : tuple of (int, label, **props)
            Node to add to the graph.
        """
        n_id, n_label, n_props = node
        n = Node(n_id, n_props)
        n.update_labels([
            'owl__NamedIndividual',
            n_label,
            'Resource'
        ])

        self._graph.create(n)

    def add_nodes(self, nodes: List[tuple]):
        """
        Add a list of nodes to the graph and synchronize them to the remote
        database.
        """

        ns = []
        # Since we have to synchronize changes as a single chunk, it's not as
        # simple as calling add_node() for every element of `nodes`.
        for n in nodes:
            n_id, n_label, n_props = n
            nn = Node(n_id, n_props)
            nn.update_labels([
                'owl__NamedIndividual',
                n_label,
                'Resource'
            ])
            ns.append(nn)
        
        self._graph.create(Subgraph(ns))
    
    def add_edge(self, edge: tuple):
        """
        Add an edge to the graph and synchronize it to the remote database.
        """
        u, rel_type, v, props = edge
        e = Relationship(u, rel_type, v, props)
        self._graph.create(e)

    def add_edges(self, edges: List[tuple]):
        """
        Add a list of edges to the graph and synchronize them to the remote
        database.
        """
        es = []
        # Since we have to synchronize changes as a single chunk, it's not as
        # simple as calling add_edge() for every element of `edges`.
        for e in edges:
            u, rel_type, v, props = e
            ee = Relationship(u, rel_type, v, props)
            es.append(ee)

        self._graph.create(Subgraph(es))


    def run_query_in_session(self, query: str):
        """Submit a cypher query transaction to the connected graph database
        driver and return the response to the calling function.

        Parameters
        ----------
        query : str
            String representation of the cypher query to be executed.

        Returns
        -------
        list of neo4j.Record
        """
        raise NotImplementedError
        # with self._driver.session() as session:
        #     query_response = session.read_transaction(_execute_cypher_transaction, query)
        # return query_response

class NetworkX(GraphDataMixin):
    format = 'networkx'

    def __init__(self):
        self._graph = nx.DiGraph()

    def add_node(self, node: tuple):
        n_id, n_label, n_props = node
        n_props['LABELS'] = {'owl__NamedIndividual', n_label, 'Resource'}
        # Use kwargs expansion to explode props
        self._graph.add_node(n_id, **n_props)

    def add_edge(self, edge: tuple):
        u, rel_type, v, e_props = edge
        e_props['TYPE'] = rel_type
        self._graph.add_edge(u, v, **e_props)

    def add_nodes(self, nodes: List(tuple)):
        for n in nodes:
            self.add_node(n)

    def add_edges(self, edges: List(tuple)):
        for e in edges:
            self.add_edge(e)
