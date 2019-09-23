import comptox_ai
import neo4j

import pytest
import os, sys

if os.path.exists('CONFIG.cfg'):
    CONFIG_FILE = 'CONFIG.cfg'
else:
    CONFIG_FILE = 'CONFIG-default.cfg'

class TestGraph(object):
    def test_does_create_bolt_driver(self):
        c = comptox_ai.ComptoxAI(config_file=CONFIG_FILE)

        assert isinstance(c.graph.driver, neo4j.DirectDriver)