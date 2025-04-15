#!/usr/bin/env python3
"""
Little script that fetches all of the chemical lists on the EPA's Comptox
Dashboard. Uses an undocumented portion of the dashboard API that was
discovered by digging through network activity while browsing the website.

This relies on a small data file (that is totally subject to deprecation)
downloaded from the home page for all chemical lists, which is included in this
code repository.

The output of the script is a new CSV file containing all chemical list data,
written to the same directory containing the index of chemical lists loaded as
input to the script.
"""

import requests
import scrapy
import pandas as pd
from tqdm import tqdm

from typing import List
import os


lists_file_path = os.path.join('..','..','data','external','epa','Chemical Lists.tsv')
lists = pd.read_csv(lists_file_path, sep="\t")

list_abbreviations = []

for i, l in lists.iterrows():
  list_url = l['LIST_ACRONYM']
  list_abbreviations.append(list_url.split("/")[-1])

def get_list_by_abbrev(abbrev: str):
  r = requests.post(
    'https://comptox.epa.gov/dashboard/api/chemical_list',
    data={"page": 0, "abbreviation": abbrev}
  )
  return r.json()

def make_list_df(abbrev: str):
  chem_list = get_list_by_abbrev(abbrev)
  df_convert = pd.DataFrame(chem_list['chemicals'])
  df_convert['List'] = abbrev
  return df_convert

print("Retrieving all chemical list data...")
all_list_dfs = []
for x in tqdm(list_abbreviations):
  all_list_dfs.append(make_list_df(x))

complete_list_data = pd.concat(all_list_dfs, ignore_index=True)

out_path = os.path.join('..','..','data','external','epa','chem_lists_data.csv')
complete_list_data.to_csv(out_path, sep=',', index=False, header=True)