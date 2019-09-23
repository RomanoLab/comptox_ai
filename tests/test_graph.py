import comptox_ai
import neo4j

import pytest

CONFIG_FILE = 'CONFIG.cfg'

class TestGraph(object):
    def test_does_create_bolt_driver(self):
        c = comptox_ai.ComptoxAI(config_file=CONFIG_FILE)

        assert isinstance(c.graph.driver, neo4j.DirectDriver)