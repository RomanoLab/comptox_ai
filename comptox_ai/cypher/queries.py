MIE_DISEASE_PATH = """
MATCH
    (m:ns0__MolecularInitiatingEvent {{ns0__keyEventID: '{}'}}),
	(d:ns0__Disease {{ns0__commonName: '{}'}}),
p=shortestPath((d)-[*]-(m))
WHERE length(p)>1
RETURN p;
"""[1:-1]

FETCH_NODES_BY_LABEL = """
MATCH
    (n:ns0__{})
RETURN n;
"""[1:-1]

FETCH_INDIVIDUAL_NODE_BY_URI = """
MATCH
    (n:owl__NamedIndividual {{ uri: '{}' }})
RETURN n;
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
MERGE (node1:{} {{ {}: {{node1}} }})
MERGE (node2:{} {{ {}: {{node2}} }})
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

BETWEENNESS_CENTRALITY = """
CALL algo.betweenness.stream({{nodeLabel}}, {{relationshipType}}, {{
    direction: {{direction}},
    graph: {{graph}}
}})
YIELD nodeId, centrality
MATCH (n) WHERE id(n) = nodeId
RETURN n.{} AS node, centrality
"""[1:-1]
