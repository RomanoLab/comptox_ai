# RUN THIS FIRST

import requests
import pickle
from comptox_ai.db import GraphDB


db = GraphDB(hostname="neo4j.comptox.ai")

# get assays
assay_res = db.run_cypher("MATCH (a:Assay) RETURN a;")
assays = [a['a'] for a in assay_res]

active_template= """
MATCH (c:Chemical)-[r2:CHEMICALHASACTIVEASSAY]->(a:Assay {{commonName: '{0}' }})
WHERE c.maccs IS NOT null
RETURN c.xrefDTXSID as chemical, c.maccs as maccs;
"""

inactive_template= """
MATCH (c:Chemical)-[r2:CHEMICALHASINACTIVEASSAY]->(a:Assay {{commonName: '{0}' }})
WHERE c.maccs IS NOT null
RETURN c.xrefDTXSID as chemical, c.maccs as maccs;
"""

all_datasets = dict()

for a in assays:
    print(a['assayTarget'])
    #res = requests.get(f"http://localhost:3000/datasets/makeQsarDataset?assay={a['commonName']}&chemList=PFASMASTER")
    # Do without PFASMASTER; not enough positives!
    res_active = db.run_cypher(active_template.format(a['commonName']))
    res_inactive = db.run_cypher(inactive_template.format(a['commonName']))
    all_datasets[a['commonName']] = {
        'active': res_active,
        'inactive': res_inactive
    }

with open("./datasets.pkl", 'wb') as fp:
    pickle.dump(all_datasets, fp)