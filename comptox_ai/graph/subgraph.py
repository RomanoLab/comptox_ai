import networkx


class Subgraph():
    """
    A graph that consists of a subset of ComptoxAI's full graph database.
    """
    def __init__(self, parent_graph, nodes: list = None, from_nx_subgraph: networkx.classes.Graph = None):
        # super().__init__(driver=parent_graph.driver, build_nx_graph=False)

        self.parent_graph = parent_graph

        if nodes and from_nx_subgraph:
            raise AttributeError("Cannot pass both `nodes` and `from_subgraph` - please try again.")
        elif nodes:
            self.nodes = nodes
            self.nx = parent_graph.nx.subgraph(self.nodes)
        elif from_nx_subgraph:
            self.nodes = list(from_nx_subgraph.nodes())
            self.nx = from_nx_subgraph
