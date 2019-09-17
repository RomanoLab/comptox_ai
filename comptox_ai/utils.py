from rdflib import Graph as RDFGraph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
import networkx as nx

import statistics

def execute_cypher_transaction(tx, query, **kwargs):
    """Given a Bolt transaction object and a cypher query, execute the
    query on the transaction object and return all records in the
    query response as a list.
    """

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

def rdf_file_to_rdflib(rdf_filename):
    """Read an XML-formatted RDF file and parse into an RDFlib graph
    object.
    """
    rg = RDFGraph()
    rg.parse(rdf_filename, format='xml')
    return rg

def rdflib_to_networkx(rdflib_obj):
    """Given an RDFlib graph object, convert it to a networkx
    graph. 

    Some of the utilities and features of networkx graphs are
    replicated by ComptoxAI's custom graph object, so internal methods
    should be considered first.
    """
    G = rdflib_to_networkx_graph(rdflib_obj)
    return G

def summarize_networkx_graph(nx_graph):
    def mean(numbers):
        return float(sum(numbers)) / max(len(numbers), 1)

    def num_leaf_nodes(g):
        """Returns the number of nodes with a degree of 1."""
        leaf_nodes = 0
        for u in g:
            if g.degree[u] == 1:
                leaf_nodes += 1
        return leaf_nodes
    
    # Network size
    print("NETWORK SIZE")
    print("============")
    print("The network has {} nodes and {} edges".format(nx_graph.number_of_nodes(),
                                                         nx_graph.number_of_edges()))
    print()

    # Network size
    print("LEAF NODES")
    print("============")
    print("The network has {} leaf nodes".format(num_leaf_nodes(nx_graph)))
    print()

    # Density
    print("DENSITY")
    print("============")
    print("The network density is {}".format(nx.density(nx_graph)))
    print()

    # Degree centrality -- mean and stdev
    dc = nx.degree_centrality(nx_graph)
    degrees = []
    for k,v in dc.items():
        degrees.append(v)

    print("DEGREE CENTRALITY")
    print("=================")
    print("The mean degree centrality is {}, with stdev {}".format(mean(degrees),
                                                                   statistics.stdev(degrees)))
    print("The densest node is {}, with value {}".format(max(dc, key=dc.get),
                                                         max(dc.values())))
    print("The sparsest node is {}, with value {}".format(min(dc, key=dc.get),
                                                          min(dc.values())))
