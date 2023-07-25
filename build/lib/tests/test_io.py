"""Tests for importing/exporting graph data to/from the graph database."""

import comptox_ai.db

import pytest
import warnings

class TestIO(object):

  @pytest.fixture
  def G(self):
    G = comptox_ai.db.GraphDB(verbose=True, hostname="neo4j.comptox.ai")
    self.G = G

  def test_graphdb_exists(self):
    print(G)