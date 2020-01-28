from abc import abstractmethod, abstractproperty

class GraphMixin(object):
    def get_nodes(self):
        raise NotImplementedError

    def set_nodes(self, nodes):
        raise NotImplementedError

    def get_edges(self):
        raise NotImplementedError

    def set_edges(self, edges):
        raise NotImplementedError
