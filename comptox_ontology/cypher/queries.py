MIE_DISEASE_PATH = """
MATCH
	(d:ns0__Disease {{ns0__commonName: '{}'}}),
	(m:ns0__MolecularInitiatingEvent {{ns0__keyEventID: '{}'}}),
	p=shortestPath((d)-[*]-(m))
WHERE length(p)>1
RETURN p;
"""[1:-1]

FETCH_NODES_BY_LABEL = """
MATCH
    (n:ns0__{})
RETURN n;
"""[1:-1]
