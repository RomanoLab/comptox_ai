"""After running `fetch_chemical_lists.py`, this script translates the GSIDs
into DSSTOX IDs using the ACToR web services
(see https://actorws.epa.gov/actorws/)
"""

import requests
import itertools
from pathlib import Path
from yaml import load, Loader
import json
import os
from tqdm import tqdm

import ipdb

def _get_default_config_file():
    root_dir = Path(__file__).resolve().parents[3]
    if os.path.exists(os.path.join(root_dir, "CONFIG.yaml")):
        default_config_file = os.path.join(root_dir, "CONFIG.yaml")
    else:
        default_config_file = os.path.join(root_dir, "CONFIG-default.yaml")
    return default_config_file


config_file = _get_default_config_file()
with open(config_file, "r") as fp:
    CONFIG = load(fp, Loader=Loader)
DATA_DIR = CONFIG["data"]["prefix"]

with open(os.path.join(DATA_DIR, 'epa', 'CUSTOM', 'chemical_lists_data.json'), 'r') as fp:
    chemical_lists = json.load(fp)

# # Get DSSTOX IDs
# all_gsids = list(set(itertools.chain.from_iterable([x['gsids'] for x in chemical_lists])))
# ipdb.set_trace()

# Make relationships linking chemical lists to specific chemicals (by DSSTOX ID)
chemical_list_relationships = []

# add header
chemical_list_relationships.append('list_acronym\tgsid\tcasrn\n')

for cl in tqdm(chemical_lists):
    for cll in cl['chemicals']:
        chemical_list_relationships.append(f"{cl['list_id']}\t{cll['id']}\t{cll['a']}\n")
        
with open(os.path.join(DATA_DIR, 'epa', 'CUSTOM', 'chemical_lists_relationships.tsv'), 'w') as fp:
    fp.writelines(chemical_list_relationships)