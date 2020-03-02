import nxneo4j

from ._base import GraphAlgorithm

class PageRank(GraphAlgorithm):
    """PageRank algorithm for computing node importances.

    PageRank is the main algorithm used by the Google search engine for ranking
    web pages (nodes) connected by hyperlinks (edges). In spite of its original
    use for search engine queries, it is useful as a general algorithm for
    determining the importance of individual nodes in the graph based on the
    importance of their neighbors (i.e., if node `a` is connected to many nodes
    of high importance, then `a` is also important).

    Briefly, the page rank of node `p_n` is equivalent to the `n`th entry of
    the dominant eigenvector of the rescaled adjacency matrix `\textbf{R}`.

    References
    ----------
    Page, L., Brin, S., Motwani, R., & Winograd, T. (1999). The PageRank 
        citation ranking: Bringing order to the web. Stanford InfoLab.
    """

    def __init__(self, node_type=None):
        super().__init__(node_type)
        self.name = "PageRank"
        self.algorithm_type = "C"

    def _run_internal(self):
        G = nxneo4j.Graph(self.graph.driver, config={
            'node_label': self.node_label,
            'relationship_type': None,
            'identifier_property': 'uri'
        })

        pr = sorted(nxneo4j.centrality.pagerank(G).items(),
                    key=lambda x: x[1],
                    reverse=True)

        self.algorithm_results = pr
