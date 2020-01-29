from abc import abstractmethod
from typing import Iterable

class GraphMixin(object):
    """Mixin class defining operations common to all graph interfaces, inspired
    largely by the NetworkX API.
    
    Although each graph interface stores data in a different structure, both
    nodes and edges are created and accessed using the same minimal method
    calls.
    """
    def __init__(self, node_map: Iterable=None, edge_map: Iterable=None, node_features: Iterable=None, edge_features: Iterable=None):
        self._node_map = node_map
        self._edge_map = edge_map
        self._node_features = node_features
        self._edge_features = edge_features

    def get_nodes(self):
        return self._data.nodes

    def add_node(self, nodes):
        raise NotImplementedError

    def get_edges(self):
        return self._data.edges

    def add_edge(self, edges):
        raise NotImplementedError

    @property
    @abstractmethod
    def id_map(self):
        pass

    @abstractmethod
    def __getitem__(self, key):
        pass

    @abstractmethod
    def __setitem__(self, key, value):
        pass