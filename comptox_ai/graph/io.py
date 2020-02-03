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

    @abstractmethod
    def add_node(self, node, **kwargs):
        pass
    
    @abstractmethod
    def add_edge(self, edge):
        pass

    def add_nodes(self, nodes):
        for n in nodes:
            self.add_node(n)

    @abstractmethod
    def add_edges(self, edges):
        for e in edges:
            self.add_edge(e)


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
    pass

class NetworkX(GraphDataMixin):
    pass