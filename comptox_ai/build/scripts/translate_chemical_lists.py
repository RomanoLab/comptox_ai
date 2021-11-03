"""After running `fetch_chemical_lists.py`, this script translates the GSIDs
into DSSTOX IDs using the ACToR web services
(see https://actorws.epa.gov/actorws/)
"""

import requests
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

# Make nodes for chemical lists
chemical_lists = []

# Make relationships linking chemical lists to specific chemicals (by DSSTOX ID)
chemical_list_relationships = []

ipdb.set_trace()
print()