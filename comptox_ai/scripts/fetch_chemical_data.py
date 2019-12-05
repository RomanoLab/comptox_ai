#!/usr/bin/env python3

import os, sys
from dataclasses import dataclass, astuple
import pandas as pd
from tqdm import tqdm
import requests

DSSTOX_PATH = "/data1/chemical/DSSTox/"

ACTORWS_BASE = "https://actorws.epa.gov/actorws/"


# GET BASIC IDS AND MAPPINGS (From DSSTox's MS-Ready mappings)


@dataclass
class Chemical:
    name: str  # preferred name
    casrn: str
    dtxsid: str
    inchi_string: str
    inchi_key: str
    smiles: str
    # qc_level: int

    def parse_devphyschemdb(self):
        url = ACTORWS_BASE + "physchemdb/dev/properties/{}.json".format(self.casrn)
        r = requests.get(url)
        return r.json()


props_file_path = os.path.join(DSSTOX_PATH, "DSSToxMS-Ready.csv")

props = pd.read_csv(props_file_path, sep=",")

chemicals = []

for _, row in tqdm(props.iterrows(), total=len(props)):
    r = dict(row)
    chemicals.append(
        Chemical(
            name=r["Preferred_Name"],
            casrn=r["CAS-RN"],
            dtxsid=r["DSSTox_Substance_ID"],
            inchi_string=r["InChIString"],
            inchi_key=r["InChIKey"],
            smiles=r["SMILES"],
        )
    )


# GET FUNCTIONAL USES WHERE AVAILABLE (from CPDat)

# def get_chemical_by_casrn(casrn):
#     c = [x for x in chemicals if x.casrn == casrn]
#     assert len(c) <= 1
#     if len(c) == 0:
#         return None
#     else:
#         return c[0]

# cpdat_fuse_file_path = os.path.join(DSSTOX_PATH, "CPDat", "functional_uses.csv")
# cpdat_chem_file_path = os.path.join(DSSTOX_PATH, "CPDat", ".csv")

# cpdat_fuse = pd.read_csv(cpdat_fuse_file_path, sep=",")
# cpdat_chem = pd.read_csv(cpdat_chem_file_path, sep=",")

# matched = 0
# for _, row in tqdm(cpdat.iterrows(), total=len(cpdat)):
#     r = dict(row)
#     casrn_match = get_chemical_by_casrn(r['casrn'])


# DUMP ALL CHEMICALS TO FILE READY FOR LOADING INTO NEO4J

chemical_tuples = [astuple(x) for x in chemicals]

print("Writing chemicals to CSV file...")
df = pd.DataFrame(chemical_tuples)
df.columns = list(chemicals[0].__dataclass_fields__.keys())


# Remove duplicates
dups = df.loc[~df.duplicated(),:] # remove duplicated rows


#df.to_csv("chemicals.csv", index=False)
