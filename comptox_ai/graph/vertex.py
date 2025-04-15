import neo4j

from .edge import Edge

class Vertex(object):
    """
    Representation of a vertex in the graph database (also called a /node/).
    """

    def __init__(self, neo4j_record: neo4j.Record, raw_edges=None):
        self.raw_node = neo4j_record['n']
        self.labels = self.raw_node.labels
        self.n4j_id = self.raw_node.id
        self.prop_dict = dict(self.raw_node)

    def __repr__(self):
        return "Vertex {0} with URI suffix: {1}".format(self.n4j_id, self.prop_dict['uri'].split('#')[-1])
