"""
Metrics for ComptoxAI graphs and subgraphs.

The scope of this module is derived from:
- http://reference.wolfram.com/language/guide/GraphMeasures.html
- Hern{\'}andez, J.M., \& Van Mieghem, P. (2011). Classification of graph metrics.
"""


def ensure_nx_available(g):
    """
    Check to make sure the graph has a NetworkX representation computed.

    If the NetworkX graph does not exist, a warning is printed and the
    graph object is generated.

    Parameters
    ----------
    g: comptox_ai.graph.Graph
        ComptoxAI graph object to check.
    """
    if not hasattr(g, 'nx'):
        print("WARNING: No networkx graph representation found.")
        print("Since this is needed for most metric computations,")
        print("we will generate it now.")
        g.to_networkx_graph(store=True)
        return False
    return True
    
# Basic measures

def vertex_count(g):
    ensure_nx_available(g)

    return g.nx.number_of_nodes()

def edge_count(g):
    ensure_nx_available(g)

    return g.nx.number_of_edges()

# Degree measures

def vertex_degree(g, v):
    raise NotImplementedError

def vertex_in_degree(g, v):
    raise NotImplementedError

def vertex_out_degree(g, v):
    raise NotImplementedError

# Distance measures

def graph_distance(g, v1, v2):
    raise NotImplementedError

# Connectivity measures

def vertex_connectivity(g, v1, v2):
    raise NotImplementedError

def edge_connectivity(g, v1, v2):
    raise NotImplementedError

# Centrality measures

def closeness_centrality(g, v):
    raise NotImplementedError

def betweenness_centrality(g, v):
    raise NotImplementedError

# Reciprocity and Transitivity

def graph_reciprocity(g):
    raise NotImplementedError

def global_clustering_coefficient(g):
    raise NotImplementedError

# Homophily, Assortative Mixing, and Similarity

def graph_assortativity(g):
    raise NotImplementedError

def vertex_correlation_similarity(g, v1, v2):
    raise NotImplementedError
