class Path(object):
    """A sequence of graph database nodes representing a directed path.
    """
    def __init__(self, node_list):
        assert len(node_list) >= 1

        self.nodes = node_list

        self.start_node = self.nodes[0]
        self.end_node = self.nodes[-1]

    def __repr__(self):
        repr_str = "< 'Path' object of nodes with the following URI suffixes:"\
                   "\n\t["
        for x in self.nodes:
            repr_str += " {0},\n\t".format(x['uri'].split("#")[-1])
        repr_str = repr_str[:-3]
        repr_str += " ] >"
        return repr_str

    def __iter__(self):
        return (x for x in self.nodes)

    def get_uri_sequence(self):
        uris = []
        for node in self.nodes:
            uris.append(node['uri'])
        return uris
