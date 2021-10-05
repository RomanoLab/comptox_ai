#!/usr/bin/env python3

"""Post-installation routines to clean ComptoxAI's Neo4j database.

After importing the database into Neo4j using n10s (neosemantics), there are a
few final steps that need to be performed to make the database more
user-friendly. For the most part, these are just cleaning up extra entities
left over from the OWL format (e.g., removing "NamedIndividual" and "Resource"
node labels).
"""

from comptox_ai.db.graph_db import GraphDB

from neo4j.exceptions import ClientError

def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False

print("This script cleans unnecessary junk out of the ComptoxAI graph database (mainly artifacts from the OWL2 specification).")
cont = yes_or_no("Do you want to continue? WARNING: This is a destructive operation! If you aren't sure, quit now!")
if not cont:
    raise SystemExit

# Keep an eye out for config file loading issues here.
db = GraphDB()

# Note: This is the config for n10s before import:
# CALL n10s.graphconfig.init({
# 	handleVocabUris: 'IGNORE',
# 	handleMultival: 'ARRAY',
# 	handleRDFTypes: 'LABELS',
# 	applyNeo4jNaming: true
# })

# Remove useless node labels
db.run_cypher("MATCH (n:Resource) REMOVE n:Resource;", verbose=True)
db.run_cypher("MATCH (n:NamedIndividual) REMOVE n:NamedIndividual;", verbose=True)
db.run_cypher("MATCH (n:AllDisjointClasses) REMOVE n:AllDisjointClasses;", verbose=True)
db.run_cypher("MATCH (n:AllDisjointProperties) REMOVE n:AllDisjointProperties;", verbose=True)
db.run_cypher("MATCH (n:DatatypeProperty) REMOVE n:DatatypeProperty;", verbose=True)
db.run_cypher("MATCH (n:FunctionalProperty) REMOVE n:FunctionalProperty;", verbose=True)
db.run_cypher("MATCH (n:ObjectProperty) REMOVE n:ObjectProperty;", verbose=True)
db.run_cypher("MATCH (n:AnnotationProperty) REMOVE n:AnnotationProperty;", verbose=True)
db.run_cypher("MATCH (n:_GraphConfig) REMOVE n:_GraphConfig;", verbose=True)
db.run_cypher("MATCH (n:Ontology) REMOVE n:Ontology;", verbose=True)
db.run_cypher("MATCH (n:Restriction) REMOVE n:Restriction;", verbose=True)
db.run_cypher("MATCH (n:Class) REMOVE n:Class;", verbose=True)

# Now, delete any nodes that have no labels
db.run_cypher("MATCH (n) WHERE size(labels(n)) = 0 DETACH DELETE n;", verbose=True)

# Create indexes
meta = db.get_metagraph()
for nt in meta.node_labels:
    try:
        db.run_cypher(f"CREATE INDEX {nt.lower()}_uri_index FOR (n:{nt}) ON (n.uri);", verbose=True)
    except ClientError:
        print(f"Node index on {nt} already exists - skipping.")
        continue