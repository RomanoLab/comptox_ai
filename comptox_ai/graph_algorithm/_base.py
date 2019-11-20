from abc import ABC, abstractmethod

class GraphAlgorithm(ABC):
    """Prototype for a generic graph algorithm, implemented as a Python ABT.
    
    Parameters
    ----------
    object : [type]
        [description]
    """

    def __init__(self, node_type=None):
        if node_type:
            self.node_type = node_type
        else:
            self.node_type = None
        self.algorithm_results = None

    def __repr__(self):
        return "Graph algorithm: {0}".format(
            str(self.__class__.__name__)
        )

    @abstractmethod
    def run(self):
        pass