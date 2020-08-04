import numpy as np
import scipy.sparse
import pandas as pd
import networkx as nx

from ..cypher.queries import FETCH_NODES_BY_ID_LIST

from typing import List

from .graph import Graph

def _build_data_matrix(graph: Graph, id_list: List[int]):
    query = FETCH_NODES_BY_ID_LIST.format(id_list)
    res = graph.run_query_in_session(query)

    np.array((), dtype=np.float16)

def _build_metadata_df(graph: Graph, id_list: List[int]):
    raise NotImplementedError

class FeatureMatrix(object):
    def __init__(self, graph: Graph, node_ids: List[int] = []):
        self.parent_graph = graph
        self.node_ids = node_ids

        if len(node_ids) > 0:
            self.data = _build_data_matrix(self.parent_graph, self.node_ids)
            self.meta = _build_metadata_df(self.parent_graph, self.node_ids)

            self.is_empty = False
        else:
            self.data = np.array((0,0))
            self.meta = pd.DataFrame()
    