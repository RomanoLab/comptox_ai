import numpy as np
import ipdb

from .utils import test_neo4j_driver_connection, execute_cypher_transaction

from .cypher.queries import FETCH_NODE_IDS_BY_LABEL

class FeatureSet(object):
    """
    A smart container for quantitative data annotated to graph
    database nodes.

    A `FeatureSet` is, fundamentally, a Numpy `ndarray` where each row
    is tied to a node in ComptoxAI's graph database. `FeatureSet`s are
    defined over all nodes of a given type (e.g., proteins, genes,
    diseases, chemical), and their feature space is accordingly
    restricted to features that make sense in the context of that node
    type.

    Feature types
    -------------

    
    """
    def __init__(self, node_type, feature_space_len = 0,
                 node_count = 0, n4j_driver=None):
        """Create a new feature set for a specific node type
        """
        self.data = np.empty((node_count, feature_space_len))
        self.data[:] = np.nan

        self.node_type = node_type

        if test_neo4j_driver_connection(n4j_driver):
            self.linked_driver = n4j_driver
        else:
            print("Can't find a valid Neo4j driver object---reconfigure using `connect_to_graph_db_driver()`.")
            self.linked_driver = None

    @property
    def driver_is_connected(self):
        return (self.linked_driver is None)

    def connect_to_graph_db_driver(self, driver):
        if self.linked_driver is not None:
            print("Connecting to Neo4j graph database...")
        else:
            print("Reconfiguring connection to Neo4j...")
        self.linked_driver = driver

        if not test_neo4j_driver_connection(driver):
            print("Connection to Neo4j unsuccessful! Please try again.")
            self.linked_driver = None

    def synchronize_with_graph_db(self):
        if self.driver_is_connected():
            print("Error: Need to connect to graph before feature set can be synchronized.")
            return False

        query = FETCH_NODE_IDS_BY_LABEL.format(self.node_type)

        # Pull IDs and names for the corresponding node type
        with self.driver.session() as session:
            query_response = session.read_transaction(execute_cypher_transaction,
                                                      query)

        ipdb.set_trace()
        print()
