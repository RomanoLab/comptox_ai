from email import header
import numpy as np
from scipy.spatial.distance import cosine, jaccard, cityblock
import pandas as pd

import ipdb

from comptox_ai.db import GraphDB

db = GraphDB()

res = db.run_cypher("MATCH (n:Chemical) WHERE EXISTS(n.maccs) RETURN n.commonName as name, n.xrefDTXSID as dtxsid, n.maccs as maccs;")
pfas_res = db.run_cypher("MATCH (n:ChemicalList { listAcronym: \"PFASMASTER\"})-[r:LISTINCLUDESCHEMICAL]->(m:Chemical) RETURN m.commonName as name;")
pfas_names = [x['name'] for x in pfas_res]

maccs_dict = dict()
for r in res:
    maccs_dict[r['name']] = [int(x) for x in list(r['maccs'])]

pfhxs_maccs = maccs_dict['PFHxS']

pfhxs_jaccard = dict()
pfhxs_jaccard_pfas = dict()
for nm, maccs in maccs_dict.items():
    pfhxs_jaccard[nm] = jaccard(pfhxs_maccs, maccs)
    if nm in pfas_names:
        pfhxs_jaccard_pfas[nm] = cityblock(pfhxs_maccs, maccs)
sort_jaccard = pd.DataFrame([(k, v) for k, v in sorted(pfhxs_jaccard.items(), key=lambda x: x[1], reverse=False)][:1000], columns=["Chemical name", "Distance (lower = more similar)"])
sort_jaccard_pfas = pd.DataFrame([(k, v) for k, v in sorted(pfhxs_jaccard_pfas.items(), key=lambda x: x[1], reverse=False)], columns=["Chemical name", "Distance (lower = more similar)"])

pfhxs_cityblock = dict()
pfhxs_cityblock_pfas = dict()
for nm, maccs in maccs_dict.items():
    pfhxs_cityblock[nm] = cityblock(pfhxs_maccs, maccs)
    if nm in pfas_names:
        pfhxs_cityblock_pfas[nm] = cityblock(pfhxs_maccs, maccs)
sort_cityblock = pd.DataFrame([(k, v) for k, v in sorted(pfhxs_cityblock.items(), key=lambda x: x[1], reverse=False)][:1000], columns=["Chemical name", "Distance (lower = more similar)"])
sort_cityblock_pfas = pd.DataFrame([(k, v) for k, v in sorted(pfhxs_cityblock_pfas.items(), key=lambda x: x[1], reverse=False)], columns=["Chemical name", "Distance (lower = more similar)"])

sort_jaccard.to_csv("./output/pfhxs_similarities_jaccard.tsv", sep="\t", index=False, header=True)
sort_jaccard_pfas.to_csv("./output/pfhxs_similarities_jaccard_PFAS-ONLY.tsv", sep="\t", index=False, header=True)
sort_cityblock.to_csv("./output/pfhxs_similarities_cityblock.tsv", sep="\t", index=False, header=True)
sort_cityblock_pfas.to_csv("./output/pfhxs_similarities_cityblock_PFAS-ONLY.tsv", sep="\t", index=False, header=True)