import pandas as pd

from comptox_ai.db import GraphDB

db = GraphDB()

drugbank_node_degree_query = """
CALL gds.degree.stream(
    {
        nodeProjection: "*",
        relationshipProjection: "*",
        orientation: "UNDIRECTED"
    }
) YIELD
nodeId, score
WITH
    gds.util.asNode(nodeId).commonName AS chemicalName,
    score AS nodeDegree,
    LABELS(gds.util.asNode(nodeId)) AS labels,
    gds.util.asNode(nodeId).xrefDrugbank AS drugbankId
WHERE 'Chemical' IN labels AND drugbankId IS NOT NULL
RETURN chemicalName, nodeDegree, drugbankId
ORDER BY nodeDegree DESC, chemicalName DESC
LIMIT 1000;
"""

drugbank_res = db.run_cypher(drugbank_node_degree_query)
drugbank_df = pd.DataFrame(drugbank_res)

drugbank_df.to_csv("./output/top_chemicals.csv", sep=",", index=False, header=True)

disease_node_degree_query = """
CALL gds.degree.stream(
    {
        nodeProjection: "*",
        relationshipProjection: "*",
        orientation: "UNDIRECTED"
    }
) YIELD
nodeId, score
WITH
    gds.util.asNode(nodeId).commonName AS disease,
    score AS nodeDegree,
    LABELS(gds.util.asNode(nodeId)) AS labels,
    gds.util.asNode(nodeId).xrefUmlsCUI AS umlsCUI
WHERE 'Disease' IN labels AND umlsCUI IS NOT NULL
RETURN disease, nodeDegree, umlsCUI
ORDER BY nodeDegree DESC, disease DESC
LIMIT 1000;
"""

disease_res = db.run_cypher(disease_node_degree_query)
disease_df = pd.DataFrame(disease_res)

disease_df.to_csv("./output/top_diseases.csv", sep=",", index=False, header=True)