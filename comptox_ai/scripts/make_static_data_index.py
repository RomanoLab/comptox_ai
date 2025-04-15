"""
make_static_data_index.py

This script creates a JSON file that is used to populate dropdowns, etc
on the interactive data browsing page. For example, we don't want to
fetch and then process every ChemicalList node from Neo4j every time
someone opens the data browsing page. This script can be re-ran every time
the underlying data are updated.
"""

from comptox_ai.db import GraphDB
from comptox_ai.utils import load_config
import json

from tqdm import tqdm

import ipdb

cnf = load_config()['neo4j']
db = GraphDB(hostname=cnf['hostname'], username=cnf['username'], password=cnf['password'])

print("Fetching/parsing chemical lists...")

# Get chemical lists
lists = db.run_cypher("MATCH (l:ChemicalList) RETURN l.listAcronym as acronym, l.commonName as name;")
for ll in tqdm(lists):
    # How the heck does this run so fast???
    num_chem_res = db.run_cypher(f"MATCH (l:ChemicalList {{ listAcronym: \"{ll['acronym']}\" }})-[:LISTINCLUDESCHEMICAL]->(:Chemical) RETURN count(l) AS ct;")
    num_chems = num_chem_res[0]['ct']
    ll['num_chems'] = num_chems

print("Fetching/parsing assays...")
# Get Tox21 assays
assays = db.run_cypher(f"MATCH (a:Assay) RETURN a.commonName as assayId, a.assayTarget as assayName;")

qsar_data = {
    'chemicalLists': lists,
    'assays': assays
}

# Can't decide whether to keep it as an API asset or a site asset...
with open("../../web/packages/api/assets/qsar_params_data.json", 'w') as fp:
    json.dump(qsar_data, fp)
with open("../../web/packages/app/src/data/qsar_params_data.json", 'w') as fp:
    json.dump(qsar_data, fp)

print("Done!")