import comptox_ai
from comptox_ai.db import GraphDB, FeatureDB

import pytest

@pytest.fixture
def G():
  G = GraphDB(verbose=True)
  return G

class TestDB(object):
  def test_neo4j_connection_does_exist(self, G):
    assert G._driver.verify_connectivity() is not None

  def test_cypher_query_does_run(self, G):
    x = G.run_cypher("RETURN 'hello';")
    assert len(x[0]) > 0

  def test_gds_list_existing_graphs(self, G):
    x = G.list_existing_graphs()
    assert isinstance(x, list)

  def test_gds_delete_existing_graphs(self, G):
    x = G.drop_all_existing_graphs()

    y = G.list_existing_graphs()

    assert len(y) is 0

  def test_gds_create_graph_native_projection(self, G):
    newgraph1 = G.build_graph_native_projection(
      "testgraph1",
      ["Chemical", "Disease"],
      "*",
    )

    def test_gds_new_num_graphs_is_1(self, G):
      y = G.list_existing_graphs()
      assert len(y) == 1

  def test_gds_delete_graph_native_projection(self, G):
    x = G.drop_existing_graph("testgraph1")
    assert x['graphName'] == "testgraph1"

  def test_gds_create_graph_cypher_projection(self, G):
    newgraph2 = G.build_graph_cypher_projection(
      "testgraph2",
      "MATCH (n) WHERE n:Chemical OR n:Disease RETURN id(n) AS id, labels(n) AS labels",
      "MATCH (c:Chemical)-->(d:Disease) RETURN id(c) as source, id(d) as target"
    )

  def test_gds_delete_graph_cypher_projection(self, G):
    # Note: this test will fail if the previous test fails
    x = G.drop_existing_graph("testgraph2")
    assert x['graphName'] == "testgraph2"