MIE_DISEASE_PATH = """
MATCH
    (m:ns0__MolecularInitiatingEvent {{ns0__xrefAOPWikiKEID: '{}'}}),
	(d:ns0__Disease {{ns0__commonName: '{}'}}),
p=shortestPath((d)-[*]-(m))
WHERE length(p)>1
RETURN p;
"""[1:-1]

FETCH_ALL_TRIPLES = """
MATCH
    (n:owl__NamedIndividual)-[r]->(m:owl__NamedIndividual)
RETURN
    n, type(r), m;
"""[1:-1]

FETCH_NODES_BY_LABEL = """
MATCH
    (n:{})
RETURN n;
"""[1:-1]

# Note: the list of IDs should be cast to string before formatting this query
FETCH_NODES_BY_ID_LIST = """
MATCH
    (n)
WHERE ID(n) IN {}
RETURN n;
"""[1:-1]

# NOTE: We consider it an orphan if it has NO RELATIONSHIPS TO
# ANOTHER owl__NamedIndividual
FETCH_ORPHAN_NODES = """
MATCH
    (n)
WHERE NOT (n)-[*]-()
RETURN n;
"""[1:-1]

FETCH_ORPHAN_INDIVIDUAL_NODES = """
MATCH
    (n:owl__NamedIndividual)
WHERE NOT (n)-[]-(:owl__NamedIndividual)
RETURN n;
"""[1:-1]

FETCH_NODE_IDS_BY_LABEL = """
MATCH
    (n:{})
RETURN ID(n);
"""[1:-1]

# E.g., when building an index of ontology classes, where
# we can use owl__NamedIndividual to get all individuals,
# then use its other labels to interpret the ontology class.
FETCH_NODE_LABELS_BY_LABEL = """
MATCH
    (n:{})
RETURN ID(n), labels(n);
"""[1:-1]

FETCH_INDIVIDUAL_NODE_BY_URI = """
MATCH
    (n:owl__NamedIndividual {{ uri: '{}' }})
RETURN n;
"""[1:-1]

FETCH_NEIGHBORS_BY_URI = """
MATCH
    (n:owl__NamedIndividual {{ uri: '{}' }})-[]-(m)
RETURN
    m;
"""[1:-1]

FETCH_ALL_NODE_DEGREES = """
MATCH
    (n:owl__NamedIndividual)
RETURN
    n.uri AS uri,
    size((n)-[]-()) AS degree;
"""[1:-1]

FETCH_NODE_DEGREES_FOR_CLASS = """
MATCH
    (n:{})
RETURN
    n.uri AS uri,
    size((n)-[]-()) AS degree;
"""[1:-1]

FETCH_CLASS_URIS = """
MATCH
    (n:owl__Class)
RETURN
    n.uri;
"""[1:-1]

SEARCH_NODE_BY_PROPERTY = """
MATCH
    (n:ns0__AOP)
WHERE
    n.ns0__commonName CONTAINS '{}'
RETURN
    n;
"""[1:-1]

## FROM networkx-neo4j
## (see: https://github.com/neo4j-graph-analytics/networkx-neo4j/blob/master/nxneo4j/base_graph.py)

ADD_NODE = """
MERGE (:{} {{ {}: {{value}} }});
"""[1:-1]

ADD_NODES = """
UNWIND {{values}} AS value
MERGE (:{} {{ {}: value }});
"""[1:-1]

ADD_EDGE = """
MERGE (node1:{} {{ {}: {{node2}} }})
MERGE (node2:{} {{ {}: {{node1}} }})
MERGE (node1)-[:{}]->(node2);
"""[1:-1]

ADD_EDGES = """
UNWIND {{edges}} AS edge
MERGE (node1:{} {{ {}: edge[0] }})
MERGE (node2:{} {{ {}: edge[1] }})
MERGE (node1)-[:{}]->(node2);
"""[1:-1]

NODE_COUNT = """
MATCH (:{})
RETURN count(*) AS numberOfNodes
"""[1:-1]

NODE_COUNTS_BY_LABEL = """
MATCH (n)
RETURN DISTINCT
    labels(n) AS labels,
    count(labels(n)) AS count;
"""[1:-1]

BETWEENNESS_CENTRALITY = """
CALL algo.betweenness.stream({{nodeLabel}}, {{relationshipType}}, {{
    direction: {{direction}},
    graph: {{graph}}
}})
YIELD nodeId, centrality
MATCH (n) WHERE id(n) = nodeId
RETURN n.{} AS node, centrality
"""[1:-1]
