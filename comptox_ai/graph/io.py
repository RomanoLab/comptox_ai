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

import ipdb

from ..cypher import queries
from ..utils import load_config

# def _infer_ontology_class_map(G: Graph):
#     # We only care about nodes that are a member of one of these ontology
#     # classes. If a node is a member than more than one of these, we have a
#     # problem.
#     valid_ontology_classes = set(
#         'Chemical',
#         'Disease',
#         'Gene',
#         'AdverseEffect',
#         'StructuralEntity',
#         'Phenotype',
#         'Database',
#         'AOP',
#         'MolecularInitiatingEvent',
#     )

#     nodes = G.run_query_in_session(FETCH_NODE_LABELS_BY_LABEL.format("owl__NamedIndividual"))    

#     class_map = {}
#     for n in nodes:

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

    """

    format = 'neo4j'

    def __init__(self, driver: neo4j.Driver):
        self._driver = driver

        node_idx_qry = queries.FETCH_NODE_IDS_BY_LABEL.format("owl__NamedIndividual")
        node_idx_res = self.run_query_in_session(node_idx_qry)
        self._node_ids = [x['ID(n)'] for x in node_idx_res]
    
    @property
    def nodes(self):
        """Get a list of all node IDs corresponding to a named individual in
        the ComptoxAI ontology.
        
        Returns
        -------
        list of int
            List of all Neo4j node IDs corresponding to a named individual.
        """
        return self._node_ids

    @property
    def edges(self):
        pass

    @property
    def is_heterogeneous(self):
        pass

    def add_node(self, node, **kwargs):
        """Adding a node to the Neo4j graph database requires several
        components that aren't needed for the other data types. These should be
        passed as a dictionary to **kwargs so it is compliant with the
        standardized method signature.
        
        Parameters
        ----------
        node : int
            [description]
        """
        pass
    
    def add_edge(self, edge):
        pass

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
        with self._driver.session() as session:
            query_response = session.read_transaction(_execute_cypher_transaction, query)
        return query_response

class NetworkX(GraphDataMixin):
    format = 'networkx'