import os, sys
import configparser
from neo4j import GraphDatabase

# NOTE: The code below is probably somewhat fragile - need to add exception
# handling and support for multiple platforms, etc.

if os.path.exists("../CONFIG.cfg"):
  CONFIG_FILE = "../CONFIG.cfg"
else:
  CONFIG_FILE = "../CONFIG-default.cfg"

cnf = configparser.ConfigParser()
cnf.read(CONFIG_FILE)
NEO4J_UNAME = cnf["NEO4J"]["Username"]
NEO4J_PWD   = cnf["NEO4J"]["Password"]
NEO4J_URI   = "bolt://localhost:7687"

RDF_FNAME = r"D:\\Data\\comptox_ai\\comptox_full_trimmed.rdf"

##################
# Cypher Queries #
##################

QRY_DROP_ALL_NODES_AND_RELS = """
MATCH (n)
DETACH DELETE n
"""[1:-1]

QRY_CREATE_RESOURCE_CONSTRAINT = """
CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE
"""[1:-1]

CALL_INIT_GRAPH_CONFIG = """
CALL n10s.graphconfig.init(
  { 
    handleVocabUris: "IGNORE",
    applyNeo4jNaming: true
  }
)
"""[1:-1]

CALL_IMPORT_RDF = """
CALL n10s.rdf.import.fetch(
  "file:///{0}",
  "RDF/XML"
)
""".format(RDF_FNAME)[1:-1]

##################

class ComptoxAIDatabase(object):
  def __init__(self, uri, user, password):
    self._driver = GraphDatabase.driver(uri, auth=(user, password))

  def close(self):
    self._driver.close()

  def run_cypher(self, query_str):
    with self._driver.session() as session:
      print()
      print("RUNNING QUERY:")
      print(query_str)
      res = session.write_transaction(self._run_transaction, query_str)
      return res

  @staticmethod
  def _run_transaction(tx, query):
    result = tx.run(query)
    return result.values()

db = ComptoxAIDatabase(NEO4J_URI, NEO4J_UNAME, NEO4J_PWD)

if True:
  db.run_cypher(QRY_DROP_ALL_NODES_AND_RELS)

try:
  db.run_cypher(QRY_CREATE_RESOURCE_CONSTRAINT)
except Exception:
  print("Resource constraint already exists - skipping")
db.run_cypher(CALL_INIT_GRAPH_CONFIG)
db.run_cypher(CALL_IMPORT_RDF)
