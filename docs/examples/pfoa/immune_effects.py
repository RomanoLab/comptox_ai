"""
immune_effects.py

Use-case analysis demonstrating ComptoxAI's ability to describe links between
PFOA and immune-modulating genes.
"""

from comptox_ai.db import GraphDB

import pandas as pd

import ipdb

db = GraphDB(hostname="165.123.13.192")

df = pd.read_excel("/data1/innatedb/innatedb_curated_genes.xls")
hsap = df.loc[df['Species']==9606,:]  # Only interested in human genes
hsap_genes = list(pd.unique(hsap['Gene Symbol']))

pfoa_gene_links = db.run_cypher("MATCH (c:Chemical {commonName: \"PFOA\"})-[r]->(g:Gene) RETURN c, r, g;")
increases = [r for r in pfoa_gene_links if r['r'][1] == 'CHEMICALINCREASESEXPRESSION'] 
decreases = [r for r in pfoa_gene_links if r['r'][1] == 'CHEMICALDECREASESEXPRESSION'] 
inc_symbols = [i['g']['geneSymbol'] for i in increases]
dec_symbols = [d['g']['geneSymbol'] for d in decreases]

inc_immuno_genes = [i_s for i_s in inc_symbols if i_s in hsap_genes]
print(f"Number of immuno genes increased by PFOA: {len(inc_immuno_genes)} ({round(len(inc_immuno_genes) / len(inc_symbols), 2)})")
dec_immuno_genes = [d_s for d_s in dec_symbols if d_s in hsap_genes]
print(f"Number of immuno genes decreased by PFOA: {len(dec_immuno_genes)} ({round(len(dec_immuno_genes) / len(dec_symbols), 2)})")

total_num_genes = db.run_cypher("MATCH (g:Gene) RETURN COUNT(g);")[0]['COUNT(g)']

# Compare to prop of immuno genes in all chem-gene associations
all_inc_genes = db.run_cypher("MATCH (c:Chemical)-[r:CHEMICALINCREASESEXPRESSION]->(g:Gene) RETURN g;")
all_inc_genes = [aig['g']['geneSymbol'] for aig in all_inc_genes]
all_dec_genes = db.run_cypher("MATCH (c:Chemical)-[r:CHEMICALDECREASESEXPRESSION]->(g:Gene) RETURN g;")
all_dec_genes = [adg['g']['geneSymbol'] for adg in all_dec_genes]

all_inc_immuno_genes = [aig for aig in all_inc_genes if aig in hsap_genes]
print(f"Number of immuno genes increased overall: {len(all_inc_immuno_genes)} ({round(len(all_inc_immuno_genes)/len(all_inc_genes), 2)})")
all_dec_immuno_genes = [adg for adg in all_dec_genes if adg in hsap_genes]
print(f"Number of immuno genes decreased overall: {len(all_dec_immuno_genes)} ({round(len(all_dec_immuno_genes)/len(all_dec_genes), 2)})")

ipdb.set_trace()
print()
