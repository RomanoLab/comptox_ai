from .cypher import queries

from .utils import execute_cypher_transaction

class Graph:
    """
    Base class for a knowledge graph used in ComptoxAI.
    """
    def __init__(self, driver, **kwargs):
        """Initialize a ComptoxAI knowledge graph supported by a Neo4j
        graph database instance.
        """

        self.driver = driver

        # If node_labels is the empty list, we don't filter on node type
        self.node_mask = kwargs.get("node_mask", [])
        if isinstance(self.node_mask, str):
            self.node_labels = [self.node_labels]
 
    def aop_shortest_path(self, mie_node: str, ao_node: str):
        """Find the shortest path between an MIE and an adverse
        outcome using the Neo4j representation of the CO's knowledge
        base. 

        Parameters
        ----------
        mie_node : string
                   Name of the MIE
        ao_node : string
                  Name of the adverse outcome
        """
        query_response = None

        if self._validate_connection_status():
            
            self.template = queries.MIE_DISEASE_PATH
            self.query = self.template.format(mie_node, ao_node)

            # Run the query
            query_response = self.run_query_in_session(self.query)

            assert len(query_response) <= 1

            if len(query_response) == 1:
                query_response = query_response[0]

        return(query_response)

    def fetch_nodes_by_label(self, label):
        """
        Fetch all nodes of a given label from the graph.

        The returned object is a list of Neo4j `Record`s, each
        containing a node `n` that has the queried label. Note that
        Neo4j allows multiple labels per node, so other labels may be
        present in the query results as well.

        Parameters
        ----------
        label: string
               Ontology class name corresponding to
               the type of node desired
        """
        if label == None:
            print("No label provided -- skipping")
        else:
            self.template = queries.FETCH_NODES_BY_LABEL
            self.query = self.template.format(label)

            query_response = self.run_query_in_session(self.query)

            return(query_response)

    def build_adjacency_matrix(self, sparse=True):
        """Construct an adjacency matrix of individuals in the
        ontology graph.

        The adjacency matrix is a square matrix where each row and
        each column corresponds to one of the nodes in the graph. The
        value of cell $(i,j)$ is 1 if a directed edge goes from
        $\textrm{Node}_i$ to $\textrm{Node}_j$, and is $-1$ if an edge
        goes from $\textrm{Node}_j$ to $\textrm{Node}_i$. 

        In the case of an undirected graph, the adjacency matrix is
        symmetric.
        """
        A = np.array()
        
        return A

    def build_incidence_matrix(self, sparse=True):
        """Construct an incidence matrix of individuals in the
        ontology graph.

        
        """
        B = np.array()

        return B
    
    def __del__(self):
        self.close_connection()

    def close_connection(self):
        """Manually close the driver linking `self.graph` to a Neo4j
        graph database.
        """
        if self.driver_connected:
            self.graph.driver.close()
        else:
            print("Error: Connection to Neo4j is not currently active")

    def open_connection(self,
                        username,
                        password,
                        uri = "bolt://localhost:7687"):
        """Manually establish a connection between `self.graph` and a
        Neo4j graph database.
        """
        if not self.driver_connected:
            try:
                self.driver = GraphDatabase.driver(self.uri,
                                                   auth=(self.username,
                                                         self.password))
                self.driver_connected = True
            except:
                print("Error opening connection to Neo4j")
                self.driver_connected = False
        else:
            print("Error: Connection to Neo4j is already active")
            print("       (Use `.close_connection()` and try again)")

    def _validate_connection_status(self):
        """Internal test for whether a connection to a Neo4j graph
        database currently exists and is active.
        """
        if not self.driver_connected:
            raise RuntimeError("Attempted to query Neo4j without an active database connection")
        return True

    def run_query_in_session(self, query):
        with self.driver.session() as session:
            query_response = session.read_transaction(execute_cypher_transaction,
                                                      query)
        return(query_response)
