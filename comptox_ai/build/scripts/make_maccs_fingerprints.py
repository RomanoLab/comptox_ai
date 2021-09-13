"""
make_maccs_fingerprints.py

This is a standalone script to extract SMILES strings from the DSSTOX MS ready
structure data files, and export them to a TSV for subsequent conversion into
MACCS fingerprints.
"""

import pandas as pd
import glob
from tqdm import tqdm
import ipdb

print("Importing and merging Mass Spec-ready structure files from EPA - this may take a while.")

files = glob.glob("D:/Data/epa/DSSTOX_MS_Ready_Chemical_Structures/*.xlsx")

all_smiles = []
for f in tqdm(files):
  df = pd.read_excel(f)
  all_smiles += list(df[['DSSTox_Substance_ID', 'SMILES']].itertuples(index=False, name=None))

df = pd.DataFrame(all_smiles, columns=['DSSTox_Substance_ID', 'SMILES'], index=None)

df.to_csv("D:/Data/epa/DSSTOX_MS_Ready_Chemical_Structures/dsstox_smiles_for_maccs.tsv", sep="\t")


