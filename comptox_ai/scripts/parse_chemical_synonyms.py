#!/usr/bin/env python3

from tkinter import N
from rdkit import Chem
import pandas as pd
import glob
from tqdm import tqdm

synonyms = []

for synonym_file in tqdm(glob.glob("D:\\data\\epa\\DSSTox_synonyms_SDF_File_20180327\\*.sdf")):
    with Chem.SDMolSupplier(synonym_file) as suppl:
        for mol in suppl:
            if mol is None: continue
            mol_dsstox = mol.GetProp('DSSTox_Substance_id')
            mol_synonyms_raw = mol.GetProp('Synonyms')
            mol_synonyms = mol_synonyms_raw.split('\n')

            synonyms.append((mol_dsstox, mol_synonyms))

print("writing to file...")
with open("D:\\data\\epa\\CUSTOM\\synonyms.tsv", 'w', encoding='utf-8') as fp:
    fp.write("DTXSID\tsynonyms\n")
    for syn in synonyms:        
        fp.write(f"{syn[0]}\t{'|'.join(syn[1])}\n")