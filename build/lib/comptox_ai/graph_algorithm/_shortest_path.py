from ._base import GraphAlgorithm
from ..graph import Path

from ..cypher import queries

class ShortestPath(GraphAlgorithm):
    """Compute the shortest path between two points on a graph.
    """

    def __init__(self, mie_node: str, ao_node: str, node_type=None):
        """Construct the ShortestPath algorithm.
        
        Parameters
        ----------
        mie_node : string
            xrefAOPWikiKEID for an MIE
        ao_node : string
            Common name for a disease
        node_type : string or list, optional
            Node (or list of nodes) to build a subgraph for the algorithm's
            database, by default None
        """
        super().__init__(node_type)
        self.name = "Shortest Path"
        self.algorithm_type = "C"

        self.query_input = {
            'mie_node': mie_node,
            'ao_node': ao_node
        }

    def _run_internal(self):
        query_response = None

        self.template = queries.MIE_DISEASE_PATH
        self.query = self.template.format(self.query_input['mie_node'],
                                          self.query_input['ao_node'])
        
        query_response = self.graph.run_query_in_session(self.query)

        assert len(query_response) <= 1

        if len(query_response) == 1:
            query_response = query_response[0]

        shortest_path = Path(query_response['p'].nodes)

        self.algorithm_results = shortest_path

    def _validate_internal(self):
        pass