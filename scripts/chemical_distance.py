import numpy as np
from scipy.spatial.distance import cosine, jaccard, cityblock
import pandas as pd

from comptox_ai.db import GraphDB

db = GraphDB()

res = db.run_cypher("MATCH (n:Chemical) WHERE EXISTS(n.maccs) RETURN n.commonName as name, n.xrefDTXSID as dtxsid, n.maccs as maccs;")

maccs_dict = dict()
for r in res:
    maccs_dict[r['name']] = [int(x) for x in list(r['maccs'])]

pfhxs_maccs = maccs_dict['PFHxS']

pfhxs_jaccard = dict()
for nm, maccs in maccs_dict.items():
    pfhxs_jaccard[nm] = jaccard(pfhxs_maccs, maccs)
sort_jaccard = [(k, v) for k, v in sorted(pfhxs_jaccard.items(), key=lambda x: x[1], reverse=False)][:100]

pfhxs_cityblock = dict()
for nm, maccs in maccs_dict.items():
    pfhxs_cityblock[nm] = cityblock(pfhxs_maccs, maccs)
sort_cityblock = [(k, v) for k, v in sorted(pfhxs_cityblock.items(), key=lambda x: x[1], reverse=False)][:100]

