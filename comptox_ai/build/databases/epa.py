from .databases import Database
from .hetionet import Hetionet
from .ctd import CTD
from .utils import safe_add_property, make_safe_property_label

import os
import tempfile

import numpy as np
import pandas as pd
import owlready2
from tqdm import tqdm

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
        # Convert dtypes so they play nice later
        cid_intarray = np.array(np.nan_to_num(np.array(pubchem_dtxsid_map['CID'], float)), dtype=int)
        cid_intarray = pd.array(cid_intarray, dtype=pd.Int32Dtype())
        pubchem_dtxsid_map['CID'] = cid_intarray
        pubchem_dtxsid_map['SID'] = pd.array(pubchem_dtxsid_map['SID'], dtype=pd.Int32Dtype())

        dsstox_inchi_map = pd.read_csv(dsstox_map_file, sep="\t", header=None, names=['DTXSID', 'InChI String', 'InChIKey'])
        # For some reason, the final row (and only the final row) has no InChIKey
        dsstox_inchi_map = dsstox_inchi_map.loc[~dsstox_inchi_map.isnull().any(axis=1), :]

        self.epa_map = pd.merge(dsstox_inchi_map, pubchem_dtxsid_map, how='outer', on='DTXSID')
        del(dsstox_inchi_map)
        del(pubchem_dtxsid_map)

        cas_map = pd.read_excel(cas_map_file)
        self.epa_map = self.epa_map.merge(cas_map, how='outer', left_on='DTXSID', right_on='dsstox_substance_id')
        del(cas_map)
        self.epa_map.drop(columns='dsstox_substance_id', inplace=True)
        self.epa_map.dropna(axis=0, subset=['DTXSID'], inplace=True)

    def parse(self, owl: owlready2.namespace.Ontology, cai_ont: owlready2.namespace.Ontology):
        self.cai_ont = cai_ont

        self.scr.draw_progress_page("===Parsing EPA Comptox data===")
        prog_step = 1
        
        # # We save the map as a large CSV file and merge the data using the bulk import
        # # feature of Neo4j's LOAD CSV statement; it's (probably) more efficient this way
        # self.scr.add_progress_step("Saving map to temporary file", prog_step)
        # prog_step += 1
        # f = tempfile.NamedTemporaryFile()
        # self.epa_map.to_csv(f)

        self.scr.add_progress_step("Merging chemicals from map file", prog_step)
        prog_step += 1

        # if True:
        #     return
        
        for i, row in tqdm(self.epa_map.iterrows(), total=len(self.epa_map)):
            #ipdb.set_trace()
            if not pd.isnull(row['casrn']):
                match = self.cai_ont.search(xrefCasRN=row['casrn'])
                
                if len(match) == 0:
                    # We need to create a new chemical
                    safe_nm = make_safe_property_label(row['preferred_name'])
                    chemical = self.cai_ont.Chemical("chem_"+safe_nm, preferredName=row['preferred_name'], xrefCasRN=row['casrn'], xrefDtxsid=row['DTXSID'], inchiKey=row['InChIKey'], inchi=row['InChI String'], xrefPubchemSID=row['SID'], xrefPubchemCID=row['CID'])
                elif len(match) == 1:
                    # We already have the chemical, so merge into 'match'
                    safe_add_property(match[0], self.cai_ont.xrefDtxsid, row['DTXSID'])
                    safe_add_property(match[0], self.cai_ont.inchiKey, row['InChIKey'])
                    safe_add_property(match[0], self.cai_ont.inchi, row['InChI String'])
                    safe_add_property(match[0], self.cai_ont.xrefPubchemSID, row['SID'])
                    safe_add_property(match[0], self.cai_ont.xrefPubchemCID, row['CID'])
                else:
                    # Uh oh, why do we have multiple chemicals with the same CasRN?
                    raise RuntimeError("Multiple chemicals found for CasRN {0}".format(row['casrn']))
            else:
                # No CasRN; we create a new chemical that doesn't have a CasRN
                chemical = self.cai_ont.Chemical("chem_"+safe_nm, xrefDtxsid=row['DTXSID'], inchiKey=row['InChIKey'], inchi=row['InChI String'], xrefPubchemSID=row['SID'], xrefPubchemCID=row['CID'])
