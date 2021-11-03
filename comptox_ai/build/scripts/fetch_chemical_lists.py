import os
import requests
from yaml import load, Loader
import json
from pathlib import Path
import pandas as pd

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

lists_meta = pd.read_csv(os.path.join(DATA_DIR, 'epa', 'Chemical Lists.tsv'), sep='\t')


all_lists = []

def get_list_page(list_abbrev, page_num):
    r = requests.post(
        f"https://comptox.epa.gov/dashboard/api/chemical_list",
        params={
            "abbreviation": list_abbrev,
            "page": page_num
        }
    )
    if r.status_code == 200:
        this_list_data = r.json()
    else:
        print("Error retrieving {0}".format(list_abbrev))
        return

    return this_list_data

for idx, lm in lists_meta.iterrows():
    list_id = lm.LIST_ACRONYM.split('/')[-1]

    this_list_dict = dict()

    this_list_dict['list_id'] = list_id
    this_list_dict['list_name'] = lm.LIST_NAME
    this_list_dict['n_chemicals'] = lm.NUMBER_OF_CHEMICALS
    this_list_dict['description'] = lm.LIST_DESCRIPTION

    print(list_id)
    
    # The API feeds the data back in pages, but the 0-th page contains a few
    # extra bits of info - the full set of GSIDs, and the total number of pages
    next_page = True
    current_page = 0
    this_list_dict['chemicals'] = list()
    while next_page:
        page_data = get_list_page(list_id, current_page)
        this_list_dict['chemicals'].extend(page_data['chemicals'])
        if current_page == 0:
            this_list_dict['gsids'] = page_data['gsids']
            last_page = page_data['lastPage']
        if current_page == last_page:
            next_page = False
        current_page += 1

    # this_list_dict['gsids'] = this_list_data['gsids']
    all_lists.append(this_list_dict)

ipdb.set_trace()

with open(os.path.join(DATA_DIR, 'epa', 'CUSTOM', 'chemical_lists_data.json'), 'w') as fp:
    json.dump(all_lists, fp)

