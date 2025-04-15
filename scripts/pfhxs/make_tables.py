# RUN THIS SECOND

import pickle
import pandas as pd

with open('./datasets.pkl', 'rb') as fp:
    datasets = pickle.load(fp)

assay_tables = []

for assay_name, ds in datasets.items():
    print(assay_name)
    # We convert each dataset to a Pandas dataframe
    ds_active = [d['maccs'] for d in ds['active']]
    ds_active_names = [d['chemical'] for d in ds['active']]
    active_df = pd.DataFrame(ds_active)
    active_df.index = ds_active_names
    active_df['target'] = 1

    ds_inactive = [d['maccs'] for d in ds['inactive']]
    ds_inactive_names = [d['chemical'] for d in ds['inactive']]
    inactive_df = pd.DataFrame(ds_inactive)
    inactive_df.index = ds_inactive_names
    inactive_df['target'] = 0

    ds_df = pd.concat([active_df, inactive_df]).astype('bool')

    assay_tables.append({
        'assay': assay_name,
        'data': ds_df
    })

with open('./classification_tables.pkl', 'wb') as fp:
    pickle.dump(assay_tables, fp)