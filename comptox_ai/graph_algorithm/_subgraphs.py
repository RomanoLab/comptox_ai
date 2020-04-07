"""
Algorithms and search strategies for extracting subgraphs from a larger parent
graph.
"""

from textwrap import dedent

import networkx as nx

from ..graph import Graph


def parse_path_spec(template_str: str):
    """Parse a Neo4j path template string.

    For more complete documentation of the path template's format, please refer
    to `comptox_ai.graph_algorithm.BigraphExtractor`.
    
    Parameters
    ----------
    template_str : str
        String representation of a Neo4j path specification.
    """
    class_rel = template_str.split("->")
    path_spec_fmt = []
    for cr in class_rel:
        split = cr.split('-')
        if len(split) == 2:
            path_spec_fmt.append(
                (split[0][1:-1], split[1][1:-1])
            )
        elif len(split) == 1:
            path_spec_fmt.append(
                (split[0][1:-1], None)
            )
        else:
            raise RuntimeError("Invalid template string--cannot parse.")

    return path_spec_fmt

class BigraphExtractor(object):
    """
    Algorithm for extracting all subgraphs from a larger parent graph.

    Given two ontology classes (i.e., node types) $A$ and $B$ and a path template
    defining allowed intermediate nodes and edges, this algorithm constructs a
    bipartite graph linking entities in $A$ to entities in $B$.

    This algorithm is especially useful as a first step in an enrichment analysis
    experiment. For example, if $A$ is chemicals and $B$ is genes, the output can
    be used to construct a statistical model that searches for chemicals enriched
    for a certain set of genes.

    Another (related) application is cluster analysis, where you can search for
    similar members of $A$ based upon overlapping connections to members of $B$.

    Parameters
    ----------
    graph : comptox_ai.graph.Graph
        ComptoxAI graph object to run the algorithm on.
    template_str : str
        Template string that specifies the metapath along which to extract
        bigraphs. The path spec template string should be formatted as follows:
        ``'(Class1)-[relType1]->(Class2)-[relType2]->...->(ClassN)'``
    """
    
    def __init__(self, graph: Graph, template_str: str):
        self.graph = graph

        path_spec = parse_path_spec(template_str)

        # Build match clause
        cypher_path_clause = ""
        for i, ps in enumerate(path_spec):
            class_abbrev = "c{0}".format(i+1)
            class_str = "({0}:ns0__{1})".format(class_abbrev, ps[0])

            cypher_path_clause += class_str

            if ps[1] is not None:
                rel_abbrev = "r{0}".format(i+1)
                rel_str = "[{0}:ns0__{1}]".format(rel_abbrev, ps[1])

                cypher_path_clause += "-{0}->".format(rel_str)

        # Build return clause
        first = "c1"
        last = "c{0}".format(len(path_spec))
        cypher_return_clause = "id({0}) AS A, id({1}) AS B".format(first, last)

        cypher_full_stmt = dedent("""
        MATCH {0}
        RETURN {1};
        """[1:-1].format(cypher_path_clause, cypher_return_clause))

        self.cypher = cypher_full_stmt


    def run(self):
        """Run the bigraph extraction algorithm.

        The algorithm is summarized as follows:

        1. Use template_str to build a metapath corresponding to the edge
           semantics of the bigraph (done by initializer).
        2. Execute the metapath match query and store node ID pairs
           corresponding to edges in the bigraph.
        3. Use py2neo interface to retrieve meaningful labels for the entities.
        4. Construct the corresponding bigraph in NetworkX.

        Returns
        -------
        nx.Graph
            Bipartite graph extracted from the ComptoxAI graph database.
        """
        res = self.graph._data._graph.run(self.cypher)

        pairs = res.data()

        # TODO: Pull out something more useful than the node ID

        A_nodes = set([p[0] for p in pairs])
        B_nodes = set([p[1] for p in pairs])

        bigraph = nx.Graph()

        bigraph.add_nodes_from(A_nodes, bipartite=0)
        bigraph.add_nodes_from(B_nodes, bipartite=1)

        bigraph.add_edges_from(pairs)

        return bigraph