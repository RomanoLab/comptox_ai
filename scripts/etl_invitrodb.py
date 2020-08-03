# etl_invitrodb.py
#
# Copyright (c) 2020 by Joseph D. Romano
#
# This file is part of the ComptoxAI software toolkit. Please refer to the root
# directory of the source distribution to find the license terms.

from getpass import getpass

import pandas as pd
import pymysql
import pymongo
import ipdb
from tqdm import tqdm
from sqlalchemy import create_engine


print("Connecting to MySQL...")

PWD = getpass("MySQL password: ")

SQL_ENGINE = create_engine('mysql+pymysql://jdromano2:{0}@127.0.0.1/invitrodb'.format(PWD), pool_recycle=3600)
MYSQL_CON = SQL_ENGINE.connect()

# Connect to MongoDB
print("Connecting to MongoDB...")
MONGO_CLIENT = pymongo.MongoClient()
MONGO_DB = MONGO_CLIENT.toxcast
MONGO_CHEMS = MONGO_DB.chemicals
MONGO_ASSAYS = MONGO_DB.assays

print("Number of chemicals in collection: ")
print(MONGO_CHEMS.count_documents({}))
print("Number of assays in collection: ")
print(MONGO_ASSAYS.count_documents({}))
if True:
  print("Deleting any existing chemicals...")
  MONGO_CHEMS.delete_many({})
  MONGO_CHEMS.drop_indexes()
  print("Deleting any existing assays...")
  MONGO_ASSAYS.delete_many({})
  MONGO_ASSAYS.drop_indexes()

# Make an index of all chemicals
CHEM_QRY = "SELECT * FROM invitrodb.chemical"
ASSAY_QRY = "SELECT * FROM assay a JOIN assay_component b ON a.aid = b.aid JOIN assay_component_endpoint c ON b.acid = c.acid"
ASSAY_META_QRY = "SELECT a.aid, a.asid, b.acid, assay_name, assay_component_name FROM assay a JOIN assay_component b ON a.aid = b.aid"

chem_idx = pd.read_sql(CHEM_QRY, MYSQL_CON)
num_chems = len(chem_idx)
assay_idx = pd.read_sql(ASSAY_QRY, MYSQL_CON)
num_assays = len(assay_idx)
assay_meta = pd.read_sql(ASSAY_META_QRY, MYSQL_CON)

print("---------------------")
print("Loaded {0} chemicals from Invitrodb.".format(chem_idx.shape[0]))
print("Available fields in index:")
print([x for x in list(chem_idx.columns)])

print("---------------------")
print("Loaded {0} assays from Invitrodb.".format(assay_idx.shape[0]))

# For each chemical:
#
# 1. Pull the data from Invitrodb (will involve a lot of JOINs)
# 2. Fetch relevant fields, insert into document
# 3. Add results to Mongodb as a document
SAMPLE_QRY = "SELECT spid FROM invitrodb.sample WHERE chid = {0}"
MC4_QRY = "SELECT * FROM invitrodb.mc4 WHERE spid = '{0}'"  # Primary multiple conc. results
MC5_QRY = "SELECT mc5.* FROM invitrodb.mc4 JOIN invitrodb.mc5 ON mc4.m4id = mc5.m5id WHERE mc4.spid = '{0}'"
SC2_QRY = "SELECT * FROM invitrodb.sc2 WHERE spid = '{0}'"  # Primary secondary conc. results
TOX_QRY = "SELECT * FROM invitrodb.cytotox WHERE chid = {0}"

# ASSAYS
new_assays = []
for i, a in tqdm(assay_idx.iterrows(), desc="Assays", position=0, leave=True, total=num_assays):
  a_dict = a.to_dict()
  this_assay = {
    'aid': a_dict['aid'],
    'asid': a_dict['asid'],
    'acid': a_dict['acid'],
    'aeid': a_dict['aeid'],
    'name': a_dict['assay_name'],
    'description': a_dict['assay_desc'],
    'organism': a_dict['organism'],
    'tissue': a_dict['tissue'],
    'cell_format': a_dict['cell_format'],
    'cell_short_name': a_dict['cell_short_name'],
    'cell_growth_mode': a_dict['cell_growth_mode'],
    'assay_footprint': a_dict['assay_footprint'],
    'assay_format_type': a_dict['assay_format_type'],
  }
  new_assays.append(this_assay)

if len(new_assays) > 0:
  MONGO_ASSAYS.insert_many(new_assays, ordered=False)

# CHEMICALS
new_chemicals = [ ]
for i, c in tqdm(chem_idx.iterrows(), desc="Chemicals", position=0, leave=True, total=num_chems):
  # get samples corresponding to chemical
  cur_chid = c['chid']
  samples = list(pd.read_sql(SAMPLE_QRY.format(cur_chid), MYSQL_CON).spid)
  
  #mc4_rows = []
  mc5_rows = []
  sc2_rows = []
  
  #for sample in tqdm(samples, desc="Samples", position=1, leave=True):
  for sample in samples:
    # get multiple conc. data

    # TODO: Decide whether we need to parse mc4 data (is mc5 good enough?)
    #sample_mc4 = pd.read_sql(MC4_QRY.format(sample), MYSQL_CON)
    #if len(sample_mc4) > 0:

      # NOTE: There are a LOT of columns in mc4. We don't need all of them, at
      # least for the time being.
      
      #ipdb.set_trace()
      #continue  # No need to query sc2

    sample_mc5 = pd.read_sql(MC5_QRY.format(sample), MYSQL_CON)
    if len(sample_mc5) > 0:

      # NOTE: There are a LOT of columns in mc4. We don't need all of them, at
      # least for the time being.
      mc5_rows.extend(
        sample_mc5[['m5id', 'm4id', 'aeid', 'modl', 'hitc', 'fitc', 'coff', 'actp',
                    'modl_er', 'modl_tp', 'modl_ga', 'modl_gw', 'modl_la', 'modl_lw',
                    'modl_prob', 'modl_rmse', 'modl_acc', 'modl_acb', 'modl_ac10',
                    'model_type']].to_dict('records')
      )
      
      #ipdb.set_trace()
      continue  # No need to query sc2

    # get single conc. data
    sample_sc2 = pd.read_sql(SC2_QRY.format(sample), MYSQL_CON)
    if len(sample_sc2) > 0:
      sc2_rows.extend(
        sample_sc2[['s2id', 'aeid', 'spid', 'bmad', 'max_med', 'coff', 'hitc']].to_dict('records')
      )

  chemical_cytotox = pd.read_sql(TOX_QRY.format(cur_chid), MYSQL_CON)
  cytotox_data = None
  if len(chemical_cytotox) > 0:
    if len(chemical_cytotox) > 1:
      raise RuntimeError("Multiple cytotoxicity reports found for {0}".cur_chid)

    cytotox_data = chemical_cytotox.to_dict('records')[0]

  # build document
  new_doc = {
    'dsstox_substance_id': c['dsstox_substance_id'],
    'chid': c['chid'],
    'casrn': c['casn'],
    'name': c['chnm'],
    'sc_data': sc2_rows,
    'mc_data': mc5_rows,
    'cytotox_data': cytotox_data
  }

  new_chemicals.append(new_doc)

if len(new_chemicals) > 0:
  MONGO_CHEMS.insert_many(new_chemicals, ordered=False)

ch_idx_1 = pymongo.IndexModel([ ("chid", pymongo.HASHED) ])
ch_idx_2 = pymongo.IndexModel([ ("name", pymongo.TEXT) ])
MONGO_CHEMS.create_indexes([ch_idx_1, ch_idx_2])

as_idx_1 = pymongo.IndexModel([ ("aid", pymongo.HASHED) ])
as_idx_2 = pymongo.IndexModel([ ("aeid", pymongo.HASHED) ])
MONGO_ASSAYS.create_indexes([as_idx_1, as_idx_2])

# Link chemicals to assays
all_chems = MONGO_CHEMS.find({})
print("Linking chemicals to arrays...")
for ac in tqdm(all_chems, desc="Assay references", position=0, leave=True, total=MONGO_CHEMS.count_documents({})):
  this_chem_id = ac['_id']

  #ipdb.set_trace()

  new_sc_data = []
  for i, x in enumerate(ac['sc_data']):
    #ipdb.set_trace()
    
    this_aeid = x['aeid']
  
    assay_ref = MONGO_ASSAYS.find_one({'aeid': this_aeid})
    assay_ref_id = assay_ref['_id']

    x['assay_id'] = assay_ref_id

    new_sc_data.append(x)
  
  MONGO_CHEMS.update_one({'_id': this_chem_id}, {'$set': {'sc_data': new_sc_data}})

  new_mc_data = []
  for j, y in enumerate(ac['mc_data']):
    this_aeid = y['aeid']
  
    assay_ref = MONGO_ASSAYS.find_one({'aeid': this_aeid})
    assay_ref_id = assay_ref['_id']

    y['assay_id'] = assay_ref_id

    new_mc_data.append(y)

  MONGO_CHEMS.update_one({'_id': this_chem_id}, {'$set': {'mc_data': new_mc_data}})

