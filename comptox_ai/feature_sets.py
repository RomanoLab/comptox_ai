class FeatureSet(object):
    """
    A smart container for quantitative data annotated to graph
    database nodes.

    A `FeatureSet` is, fundamentally, a Numpy `ndarray` where each row
    is tied to a node in ComptoxAI's graph database. `FeatureSet`s are
    defined over all nodes of a given type (e.g., proteins, genes,
    diseases, chemical), and their feature space is accordingly
    restricted to features that make sense in the context of that node
    type.

    Feature types
    -------------

    
    """
    def __init__(self):
        
