"""
Metrics for ComptoxAI graphs and subgraphs.

The scope of this module is derived from:
- http://reference.wolfram.com/language/guide/GraphMeasures.html
- Hern{\'}andez, J.M., \& Van Mieghem, P. (2011). Classification of graph metrics.
"""

from comptox_ai.graph import Graph, Vertex


# Basic measures

def vertex_count(g: Graph):
    if g.nx is None:
        g.to_networkx(store=True)

    return g.nx.number_of_nodes()

def edge_count(g: Graph):
    if g.nx is None:
        g.to_networkx(store=True)

    return g.nx.number_of_edges()

# Degree measures

def vertex_degree(g: Graph, v: Vertex):
    raise NotImplementedError

def vertex_in_degree(g: Graph, v: Vertex):
    raise NotImplementedError

def vertex_out_degree(g: Graph, v: Vertex):
    raise NotImplementedError

# Distance measures

def graph_distance(g: Graph, v1: Vertex, v2: Vertex):
    raise NotImplementedError

# Connectivity measures

def vertex_connectivity(g: Graph, v1: Vertex, v2: Vertex):
    raise NotImplementedError

def edge_connectivity(g: Graph, v1: Vertex, v2: Vertex):
    raise NotImplementedError

# Centrality measures

def closeness_centrality(g: Graph, v: Vertex):
    raise NotImplementedError

def betweenness_centrality(g: Graph, v: Vertex):
    raise NotImplementedError

# Reciprocity and Transitivity

def graph_reciprocity(g: Graph):
    raise NotImplementedError

def global_clustering_coefficient(g: Graph):
    raise NotImplementedError

# Homophily, Assortative Mixing, and Similarity

def graph_assortativity(g: Graph):
    raise NotImplementedError

def vertex_correlation_similarity(g: Graph, v1: Vertex, v2: Vertex):
    raise NotImplementedError
