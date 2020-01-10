from .databases import Database
from .hetionet import Hetionet
from .ctd import CTD

import os

import pandas as pd
import owlready2

import ipdb

class EPA(Database):
    def __init__(self, scr, config, name="EPA"):
        super().__init__(name=name, scr=scr, config=config)
        self.path = os.path.join(self.config.data_prefix, 'epa')
        self.requires = [Hetionet, CTD]

    def prepopulate(self, owl: owlready2.namespace.Ontology, cai_ont: owlready2.namespace.Ontology):
        self.cai_ont = cai_ont
        self.owl = owl

        # We have several mapping files to load:
        # 1. PubChem_DTXSID_mapping_file.txt (TSV)
        # 2. DSSTox_Mapping_20160701/dsstox_20160701.tsv (TSV)
        pubchem_dtxsid_map_file = os.path.join(self.path, 'PubChem_DTXSID_mapping_file.txt')
        dsstox_map_file = os.path.join(self.path, "DSSTox_Mapping_20160701", "dsstox_20160701.tsv", )
        cas_map_file = os.path.join(self.path, "Dsstox_CAS_number_name.xlsx")

        pubchem_dtxsid_map = pd.read_csv(pubchem_dtxsid_map_file, sep="\t")
        # Remove weird rows at end with invalid & duplicate DTXSIDs
        pubchem_dtxsid_map = pubchem_dtxsid_map.loc[pubchem_dtxsid_map['DTXSID'].str.startswith('DTX'),:]

        dsstox_inchi_map = pd.read_csv(dsstox_map_file, sep="\t", header=None, names=['DTXSID', 'InChI String', 'InChIKey'])
        # For some reason, the final row (and only the final row) has no InChIKey
        dsstox_inchi_map = dsstox_inchi_map.loc[~dsstox_inchi_map.isnull().any(axis=1), :]

        self.epa_map = pd.merge(dsstox_inchi_map, pubchem_dtxsid_map, how='outer', on='DTXSID')

        cas_map = pd.read_excel(cas_map_file)
        self.epa_map.merge(cas_map, how='outer', left_on='DTXSID', right_on='dsstox_substance_id')

        ipdb.set_trace()
        print()