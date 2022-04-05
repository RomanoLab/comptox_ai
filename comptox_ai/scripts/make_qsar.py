#!/usr/bin/env python3

"""
make_qsar.py : Connect to ComptoxAI, extract a QSAR dataset with user-defined
endpoints, and return it in tabular format.
"""

import argparse
import sys
import json

import ipdb

from comptox_ai.db import GraphDB
from comptox_ai.utils import load_config



def print_dataset_statistics(subgraph):
  print()
  print(f"Number of nodes: {len(subgraph['nodes'])}")
  print(f"Number of edges (relationships): {len(subgraph['relationships'])}")
  print()

# async def get_subgraph(**kwargs)

def main():
  parser = argparse.ArgumentParser(description='Connect to ComptoxAI, extract a QSAR dataset with user-defined endpoints, and return it in tabular format.')
  parser.add_argument('--assay-abbrev', type=str, help='An assay name abbreviation corresponding to a Tox21 assay (see first column of https://tripod.nih.gov/tox21/assays/).')
  parser.add_argument('--chem-list', type=str, default=None, help='Acronym for an EPA chemical list (see first column of https://comptox.epa.gov/dashboard/chemical-lists). If not provided, all chemicals will be used.')
  parser.add_argument('--max-chems', type=int, default=0, help='Maximum number of chemicals to fetch from the database in each target category. High values may result in long query times. If 0, no limit will be used.')
  parser.add_argument('--make-discovery', action='store_true', dest='discovery', help='Generate a discovery dataset with unknown activity endpoints.')
  parser.add_argument('--no_discovery', action='store_false', dest='discovery', help='Do not generate a discovery dataset.')
  parser.set_defaults(discovery=True)

  args = parser.parse_args()

  cnf = load_config()

  username = cnf['neo4j']['username']
  password = cnf['neo4j']['password']
  hostname = cnf['neo4j']['hostname']

  output = sys.stdout
  err = sys.stderr

  format = "json"

  if args.max_chems is not 0:
    limit_str = f" LIMIT {args.max_chems}"
  else:
    limit_str = ""

  # Only prepend the portion of the query containing the chemical list if the
  # --chem-list argument was used
  if args.chem_list:
    chem_list_query_clause = "(l:ChemicalList {{ listAcronym: '{0}' }})-[r1:LISTINCLUDESCHEMICAL]->".format(args.chem_list)
  else:
    chem_list_query_clause = ""
  
  db = GraphDB(hostname=hostname, username=username, password=password)

  res_active = db.run_cypher("""
  MATCH {0}(c:Chemical)-[r2:CHEMICALHASACTIVEASSAY]->(a:Assay {{commonName: '{1}' }})
  WHERE c.maccs IS NOT null
  RETURN c.xrefDTXSID as chemical, c.maccs as maccs{2};
  """.format(chem_list_query_clause, args.assay_abbrev, limit_str))

  res_inactive = db.run_cypher("""
  MATCH {0}(c:Chemical)-[r2:CHEMICALHASINACTIVEASSAY]->(a:Assay {{commonName: '{1}' }})
  WHERE c.maccs IS NOT null
  RETURN c.xrefDTXSID as chemical, c.maccs as maccs{2};
  """.format(chem_list_query_clause, args.assay_abbrev, limit_str))

  # res_discovery = db.run_cypher("""
  # MATCH {0}(c:Chemical)
  # WHERE c.maccs IS NOT null AND NOT (c)-[:CHEMICALHASINACTIVEASSAY]->(:Assay {{commonName: '{1}' }})
  # RETURN c.xrefDTXSID as chemical, c.maccs as maccs{2};
  # """.format(chem_list_query_clause, args.assay_abbrev, limit_str))

  if format == "json":
    final_result = {
      'active': res_active,
      'inactive': res_inactive,
      # 'discovery': len(res_discovery)
    }

  # Not extremely elegant. Explore other options for writing output.
  output.write(json.dumps(final_result))
  
if __name__=="__main__":
  main()