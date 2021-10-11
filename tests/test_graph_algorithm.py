import os
import pytest

import numpy as np

import comptox_ai
#from comptox_ai.graph_algorithm import PageRank, ShortestPath
from comptox_ai.graph_algorithm import ShortestPath

if os.path.exists('CONFIG.cfg'):
    CONFIG_FILE = 'CONFIG.cfg'
else:
    CONFIG_FILE = 'CONFIG-default.cfg'


def _validate_pr_result_format(pr_results):
    results_list = np.array([
        isinstance(pr_results, list),
        isinstance(pr_results[0][0], str),
        isinstance(pr_results[0][1], float)
    ], dtype=bool)

    return np.all(results_list)
    

class TestGraphAlgorithm:
    # def test_page_rank_does_instantiate(self):
    #     try:
    #         c = comptox_ai.ComptoxAI(config_file=CONFIG_FILE)
            
    #         pr = PageRank()

    #         assert ((c is not None) and (pr is not None))
    #     except:
    #         print("Uh oh")
    #         assert False

    # def test_page_rank_does_run_mwe(self):
    #     c = comptox_ai.ComptoxAI(config_file=CONFIG_FILE)

    #     # Run PageRank on entire graph with no filtering
    #     pr = PageRank()
    #     pr.run(c.graph)

    #     assert _validate_pr_result_format(pr.algorithm_results)

    def test_shortest_path_returns_path(self):
        c = comptox_ai.ComptoxAI(config_file=CONFIG_FILE)

        # Find the shortest path between "mie_increase_urinary_bladder_calculi"
        # and "dis_adenoma"
        sp = ShortestPath(mie_node="793", ao_node="Adenoma")
        sp.run(c.graph)

        assert isinstance(sp.algorithm_results, comptox_ai.graph.Path)