"""
GraphSAGE is an inductive (e.g., "online") deep learning model for large
graphs. It has the advantage of utilizing both local and global information, as
well as incorporating both network topology and node features.
"""

from .nn import NeuralNetwork

class GraphSAGE(NeuralNetwork):
    """
    Implementation of GraphSAGE - an inductive representation learning model
    for very large graphs.[1]_

    See `http://snap.stanford.edu/decagon/`_.

    .. [1] W.L. Hamilton, R. Ying, and J. Leskovec, "Inductive representation
    learning on large graphs," arXiv:1706.02216 [cs.SI], 2017.
    """
    def __init__(self):
        super().__init__()