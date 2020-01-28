from ..graph import Graph, Subgraph
from ..cypher import FETCH_NODE_LABELS_BY_LABEL

import networkx as nx
import numpy as np

def _generate_walks(G: Graph, num_walks):
    raise NotImplementedError

def _infer_ontology_class_map(G: Graph):
    # We only care about nodes that are a member of one of these ontology
    # classes. If a node is a member than more than one of these, we have a
    # problem.
    valid_ontology_classes = set(
        'Chemical',
        'Disease',
        'Gene',
        'AdverseEffect',
        'StructuralEntity',
        'Phenotype',
        'Database',
        'AOP',
        'MolecularInitiatingEvent',
        ''
    )

    nodes = G.run_query_in_session(FETCH_NODE_LABELS_BY_LABEL.format("owl__NamedIndividual"))    

    class_map = {}
    for n in nodes

def _read_external_class_map(G: Graph, class_map_file: str):
    raise NotImplementedError


def load_graphsage(G: Graph, write_to_file=False, file_prefix='graphsage_', generate_walks=False, num_walks=10000, class_map_file=None):
    """
    Read a representation of a graph (or subgraph) into the format used by GraphSAGE:
    https://arxiv.org/abs/1706.02216

    This returns 4 data structures, in this order:
    - A networkx graph
    - An ID map (IDs are unique integers assigned to each node)
    - A class map (i.e., node labels)
    - A set of feature matrices (TODO: UNIMPLEMENTED)

    Optionally, this function can also generate a collection of random walks on
    the graph, as specified by the parameter `num_walks`.

    Parameters
    ----------
    G : comptox_ai.Graph
        A graph or subgraph containing the data to fetch.
    write_to_file : bool
        If True, the data will be written to a set of files in the current
        directory.
    file_prefix : str
        The string prefix used at the beginning of the output file names. Has no
        effect if `write_to_file` is False.
    """
    nx_graph = G.nx
    id_map = G.node_idx

    if class_file:
        # We use some external specification for class membership
        class_map = _read_external_class_map(G, class_map_file)
    else:
        # Default - class membership is the primary ontology class
        # for a node.
        class_map = _infer_ontology_class_map(G)

def write_graphsage():
    raise NotImplementedError

def load_gcn(G: Graph):
    """
    Build a representation of a ComptoxAI graph in the format used in https://github.com/tkipf/gcn.

    """
    raise NotImplementedError

def write_gcn():
    raise NotImplementedError