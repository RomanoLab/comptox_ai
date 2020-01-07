import comptox_ai
import neo4j
import networkx
import scipy.sparse

import pytest
import os, sys

# Eventually add option for quick tests (i.e., run on small
# sample database rather than the whole thing)
QUICK_TESTS = False

if os.path.exists('CONFIG.cfg'):
    CONFIG_FILE = 'CONFIG.cfg'
else:
    CONFIG_FILE = 'CONFIG-default.cfg'


if QUICK_TESTS:
    raise NotImplementedError
else:
    @pytest.fixture
    def G():
        G = comptox_ai.utils.examples.load_full_graph()
        return G

class TestGraph(object):
    def test_does_create_bolt_driver(self):
        c = comptox_ai.ComptoxAI(config_file=CONFIG_FILE)

        assert isinstance(c.graph.driver, neo4j.DirectDriver)

    def test_does_load_full_graph_database(self, G):
        assert isinstance(G, comptox_ai.graph.Graph)

    def test_does_convert_neo4j_to_networkx(self, G):
        nx = G.to_networkx_graph()
        assert isinstance(nx, networkx.classes.DiGraph)
        assert len(G.nx.nodes()) > 0
        assert len(G.nx.edges()) > 0

    def test_does_build_valid_adjacency_matrix(self, G):
        A = G.build_adjacency_matrix()

        assert isinstance(A, scipy.sparse.lil_matrix)
