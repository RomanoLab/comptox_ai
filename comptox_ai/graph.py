import numpy as np
import nxneo4j
import networkx as nx

# for Spinner
import sys
import time
import threading

from .cypher import queries

from .utils import execute_cypher_transaction

#TODO: Move!!!
class Spinner(object):
    """See https://stackoverflow.com/a/39504463/1730417
    """
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()
    
    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False

class Graph:
    """
    Base class for a knowledge graph used in ComptoxAI.
    """
    def __init__(self, driver, **kwargs):
        """Initialize a ComptoxAI knowledge graph supported by a Neo4j
        graph database instance.
        """

        self.driver_connected = False

        self.driver = driver
        self.test_driver
        

        # If node_labels is the empty list, we don't filter on node type
        self.node_mask = kwargs.get("node_mask", [])
        if isinstance(self.node_mask, str):
            self.node_labels = [self.node_labels]

    # GRAPH LIFECYCLE METHODS

    def __del__(self):
        self.close_connection()

    def test_driver(self):
        if isinstance(self.driver, neo4j.DirectDriver):
            self.driver_connected = True
        else:
            self.driver_connected = False

    def close_connection(self):
        """Manually close the driver linking `self.graph` to a Neo4j
        graph database.
        """
        if self.driver_connected:
            self.driver.close()
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

    # NODE RETRIEVAL METHODS

    def get_node_degrees(self, node_type=None):
        """Retrieve a list of URIs and their corresponding degrees.
        
        Parameters
        ----------
        node_type : str, optional
            Ontology class corresponding to the desired node type, by default None.
        
        Returns
        -------
        list of (str, int)
            Each returned element is a tuple containing a node's URI and that node's degree.
        """
        if node_type is None:
            self.template = queries.FETCH_ALL_NODE_DEGREES
            self.query = self.template
        else:
            self.template = queries.FETCH_NODE_DEGREES_FOR_CLASS
            self.query = self.template.format(node_type)

        query_response = self.run_query_in_session(self.query)

        if len(query_response) == 0:
            return None
        else:
            return [(x['uri'], x['degree']) for x in query_response]

    def fetch_node_by_uri(self, uri):
        """Retrieve a node from Neo4j matching the given URI.
        
        Parameters
        ----------
        uri : str
            URI of the node to fetch.
        
        Returns
        -------
        neo4j.Record
            Node corresponding to the provided URI.
        """
        if uri == None:
            print("No URI given -- aborting")
        else:
            self.template = queries.FETCH_INDIVIDUAL_NODE_BY_URI
            self.query = self.template.format(uri)

            query_response = self.run_query_in_session(self.query)

            if len(query_response) == 0:
                return None
            else:
                assert len(query_response) == 1
                return query_response[0]


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

    def fetch_neighbors_by_uri(self, uri):
        """Fetch nodes corresponding to neighbors of a node represented by a given URI.
        """
        if uri == None:
            print("No URI given -- aborting")
        else:
            self.template = queries.FETCH_NEIGHBORS_BY_URI
            self.query = self.template.format(uri)

        query_response = self.run_query_in_session(self.query)

        if len(query_response) == 0:
            return None
        else:
            return query_response

    # NODE/GRAPH MODIFICATION METHODS

    # GRAPH I/O

    def to_networkx_graph(self):
        """Construct a NetworkX graph object from the data in the
        connected Neo4j graph database.

        Returns
        -------
        networkx.graph
        """
        # NOTE: nxneo4j actually seems to be useless!!!
        # We use nxneo4j to eliminate some of the implementation work
        #n4j_g = nxneo4j.Graph(self.driver)

        # Create an empty NetworkX graph
        #nx_g = nx.graph()

        # Fetch all triples
        self.template = queries.FETCH_ALL_TRIPLES
        self.query = self.template.format()

        print("Fetching all triples for named individuals - this may take a while...")
        with Spinner():
            query_response = self.run_query_in_session(self.query)

        print("All triples received, now processing them...")
        edges = []
        #edge_labels = []
        for triple in query_response:
            n = triple['n'].get('uri').split('#')[-1]
            r = triple['type(r)']
            m = triple['m'].get('uri').split('#')[-1]
            edges.append((n,r,m))
            #edge_labels.append(r)

        G = nx.DiGraph()
        #G.add_edges_from(edges)

        for n, r, m in edges:
            G.add_edge(u_of_edge=n, v_of_edge=m, edge_label=r)

        #return (G, edges, edge_labels)
        return(G)

    def to_graphml(self, G=None, edges=None, edge_labels=None):
        if not all([G, edges, edge_labels]):
            print("Incomplete network data given; calculating via to_networkx_graph()...")
            G, edges, edge_labels = self.to_networkx_graph()
            print("...done")

        


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

        Parameters
        ----------
        sparse : bool (default: `True`)
                 Whether to return the value as a Scipy sparse matrix
                 (default behavior) or a dense Numpy `ndarray`.

        """
        A = np.array()

        G = nxneo4j.Graph(self.driver)

        return A

    def build_incidence_matrix(self, sparse=True):
        """Construct an incidence matrix of individuals in the
        ontology graph.

        
        """
        B = np.array()

        return B

    # GRAPH ALGORITHMS (external implementations; temporary)

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

        shortest_path = Path(query_response['p'].nodes)

        return(shortest_path)

    def page_rank(self, node_type=None):
        """Compute page rank of all owl__NamedIndividual nodes in the attached graph.

        Page rank uses eigenvector centrality to determine "importance" of individual nodes based
        on the centrality of immediate neighbors.
        
        Parameters
        ----------
        node_type : str, optional
            Ontology class of desired nodes. Page rank will be computed over all node types, but
            only the desired type will be returned to the user. If None, no filtering will be
            performed.

        Returns
        -------
        list of tuple
        """
        G = nxneo4j.Graph(self.driver, config={
            'node_label': 'owl__NamedIndividual',
            'relationship_type': None,
            'identifier_property': 'uri'
        })
        
        pr = sorted(nxneo4j.centrality.pagerank(G).items(), key=lambda x: x[1], reverse=True)

        return pr


    # UTILITY METHODS

    def run_query_in_session(self, query):
        """Submit a cypher query transaction to the connected graph database driver and return the
        response to the calling function.

        Parameters
        ----------
        query : str
                String representation of the cypher query to be executed.

        Returns
        -------
        list of neo4j.Record
        """
        with self.driver.session() as session:
            query_response = session.read_transaction(execute_cypher_transaction,
                                                      query)
        return(query_response)


class Path(object):
    def __init__(self, node_list):
        assert len(node_list) >= 1
        
        self.nodes = node_list

        self.start_node = self.nodes[0]
        self.end_node = self.nodes[-1]

    def __repr__(self):
        repr_str = "< 'Path' object of nodes with the following URI suffixes:\n\t["
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
