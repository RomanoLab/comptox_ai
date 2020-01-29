from typing import Iterable

import networkx as nx

from .graph_io import GraphMixin

class NetworkX(GraphMixin):
    def __init__(self, node_map: Iterable=None, edge_map: Iterable=None, node_features: Iterable=None, edge_features: Iterable=None):
        super().__init__()
        self._data = nx.DiGraph()

    @property
    def data(self):
        return self._data