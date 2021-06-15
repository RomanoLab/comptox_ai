from pandas.core.frame import DataFrame
from yaml import load
from comptox_ai.db.graph_db import GraphDB
import shutil
import os
from comptox_ai.ml.nn_test import *

import torch
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score

from torch_geometric.utils import negative_sampling
from torch_geometric.datasets import Planetoid
import torch_geometric.transforms as T
from torch_geometric.nn import GCNConv
from torch_geometric.utils import train_test_split_edges

graph_name = 'test_graph'
node_list = ['Gene', 'Disease']

data = load_data(graph_name=graph_name, node_types=node_list)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = Net(data.num_features, 64).to(device)
data = data.to(device)
optimizer = torch.optim.Adam(params=model.parameters(), lr=0.01)

run_model(data, model, optimizer)
# Load the data
# nn.load_data(graph_name=graph_name, node_types=node_list)

# # Train the model
# nn.fit()

# # Return predicted links
# nn.predict()
