import nxneo4j

from ._base import GraphAlgorithm

class PageRank(GraphAlgorithm):
    """PageRank algorithm for computing node importances.

    PageRank is the main algorithm used by the Google search engine for ranking
    web pages (nodes) connected by hyperlinks (edges). In spite of its original
    purpose, 
    
    Parameters
    ----------
    GraphAlgorithm : [type]
        [description]
    """

    def __init__(self, node_type=None):
        super().__init__(node_type)

    def run(self, graph):
        self.graph = graph

        if self.node_type is None:
            node_label = 'owl__NamedIndividual'
        else:
            node_label = f"ns0__{self.node_type}"

        G = nxneo4j.Graph(self.graph.driver, config={
            'node_label': node_label,
            'relationship_type': None,
            'identifier_property': 'uri'
        })

        pr = sorted(nxneo4j.centrality.pagerank(G).items(),
                    key=lambda x: x[1],
                    reverse=True)

        self.results = pr

    