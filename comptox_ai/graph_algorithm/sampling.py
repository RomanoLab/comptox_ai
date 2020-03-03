"""
Algorithms for sampling large directed graphs.

Many graph analysis techniques are intractable (or, at the least, inconvenient)
when graphs become large. ComptoxAI's graph is *very* large, and can therefore
benefit from sampling strategies that produce subgraphs which retain important
characteristics present in the parent graph.

A practical example of how graph sampling is used in ComptoxAI is for
generating a smaller graph to be used in unit testing. As a result, we can
perform a full suite of unit tests without the need to generate, transfer, or
load the entire database on CI systems.

We focus on techniques in particular described in [1]_.

.. [1] Leskovec, J., & Faloutsos, C. (2006, August). "Sampling from large
   graphs." In Proceedings of the 12th ACM SIGKDD international conference on
   Knowledge discovery and data mining (pp. 631-636).
"""

from ..graph import Graph

from ._base import GraphAlgorithm

from random import choice
import ipdb

def _run_forest_fire(g: Graph, sample_size: float=0.17, p_f: float=0.35,
                     p_b: float=0.20):
    """Run the forest fire graph sampling algorithm.

    Default parameters are based on the assumption the graph is "densifying" -
    i.e., that as nodes are added, the density of the node increases.
    
    Parameters
    ----------
    g : comptox_ai.graph.Graph
        The graph to sample from (in 'networkx' format
    sample_size : float (default: 0.17)
        A number from 0. to 1.0 indicating the proportional size of the sampled
        graph, relative to the parent graph.
    p_f : float (default: 0.35)
        Forward burning probability.
    p_b : float (default: 0.20)
        Backwards burning probability.
    """
    nx_g = g._data._graph

    v_seen = []

    while True:
        v = choice(list(nx_g.nodes()))  # evaluate performance - typecasting to list may be computationally bad
        if v in v_seen:
            continue
        v_seen.append(v)

        ipdb.set_trace()


class SampleGraph(GraphAlgorithm):
    """Sample a large graph, returning a subgraph that maintains
    characteristics of the parent graph.

    Parameters
    ----------
    method : str
        Name of the specific sampling algorithm to be used. As of now, the
        default option is the only available algorithm: {'forest-fire'}.

    Returns
    -------
    comptox_ai.graph.Graph
        A subgraph of the parent ComptoxAI graph.

    Notes
    -----
    
    This class wraps an arbitrary set of sampling algorithms, any of which can
    be used to fit specific scenarios. The default algorithm is the "forest
    fire" algorithm, originally described in [2]_.

    References
    ----------

    .. [2] Leskovec, J., Kleinberg, J., & Faloutsos, C. (2005, August). Graphs
       over time: densification laws, shrinking diameters and possible
       explanations. In Proceedings of the eleventh ACM SIGKDD international
       conference on Knowledge discovery in data mining (pp. 177-187).
    """
    def __init__(self, method='forest-fire'):
        self.req_format = 'networkx'
        super().__init__()

    def _run_algorithm(self):
        new_graph = _run_forest_fire(self.graph)
        return new_graph
