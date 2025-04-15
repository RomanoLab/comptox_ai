# RUN THIS FIRST

import requests
import pickle
from comptox_ai.db import GraphDB


db = GraphDB(hostname="neo4j.comptox.ai")

# get assays
assay_res = db.run_cypher("MATCH (a:Assay) RETURN a;")
assays = [a['a'] for a in assay_res]

all_datasets = dict()

for a in assays:
    print(a['assayTarget'])
    #res = requests.get(f"http://localhost:3000/datasets/makeQsarDataset?assay={a['commonName']}&chemList=PFASMASTER")
    # Do without PFASMASTER; not enough positives!
    res = requests.get(f"http://localhost:3000/datasets/makeQsarDataset?assay={a['commonName']}")
    all_datasets[a['commonName']] = res.json()

with open("./datasets.pkl", 'wb') as fp:
    pickle.dump(all_datasets, fp)