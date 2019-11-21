from abc import ABC, abstractmethod

class GraphAlgorithm(ABC):
    """Prototype for a generic graph algorithm, implemented as a Python ABT.
    
    Parameters
    ----------
    object : [type]
        [description]
    """

    def __init__(self, node_type=None):
        """Construct a new graph algorithm using parameters general to all
        algorithms. Algorithm-specific parameters should be implemented in
        child classes.
        
        Parameters
        ----------
        node_type : str or list, optional
            Node label (or list of node labels) to create a subgraph on which
            the algorithm will be run (e.g., a filter on nodes), by default 
            None.
        """
        if node_type:
            self.node_type = node_type
        else:
            self.node_type = None
        self.algorithm_results = None
        self.graph = None

        if self.node_type is None:
            self.node_label = 'owl__NamedIndividual'
        else:
            self.node_label = f"ns0__{self.node_type}"

    def __repr__(self):
        return "Graph algorithm: {0}".format(
            str(self.__class__.__name__)
        )

    @abstractmethod
    def _run_internal(self):
        pass

    def run(self, graph):
        self.graph = graph

        if self.graph._validate_connection_status():
            self.validate_params()
            
            self._run_internal()

        return self.algorithm_results

    @abstractmethod
    def _validate_internal(self):
        pass

    def validate_params(self):
        """Validate whether algorithm parameters and graph are 'compatible'.
        """
        if self.graph is None:
            print("Error: Algorithm must be associated with a graph before parameters can be validated.")
            return False

        self._validate_internal()