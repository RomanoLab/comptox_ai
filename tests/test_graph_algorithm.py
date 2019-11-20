import os
import pytest

import numpy as np

import comptox_ai
from comptox_ai.graph_algorithm import PageRank

if os.path.exists('CONFIG.cfg'):
    CONFIG_FILE = 'CONFIG.cfg'
else:
    CONFIG_FILE = 'CONFIG-default.cfg'


def _validate_pr_results(pr_results):
    results_list = np.array([
        isinstance(pr_results, list),
        isinstance(pr_results[0][0], str),
        isinstance(pr_results[0][1], float)
    ], dtype=bool)

    return np.all(results_list)
    

class TestGraphAlgorithm:
    def test_page_rank_does_instantiate(self):
        try:
            c = comptox_ai.ComptoxAI(config_file=CONFIG_FILE)
            
            pr = PageRank()

            assert ((c is not None) and (pr is not None))
        except:
            print("Uh oh")
            assert False

    def test_page_rank_does_run_mwe(self):
        c = comptox_ai.ComptoxAI(config_file=CONFIG_FILE)

        # Run PageRank on entire graph with no filtering
        pr = PageRank()
        pr.run(c.graph)

        assert _validate_pr_results(pr.results)