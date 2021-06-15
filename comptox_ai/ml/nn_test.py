import os.path as osp
# from _typeshed import NoneType
from comptox_ai.db.graph_db import Graph, GraphDB
from comptox_ai.ml.train_test_split_edges import train_test_split_edges
import shutil
import os

import torch
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score

from torch_geometric.utils import negative_sampling
import torch_geometric.transforms as T
from torch_geometric.nn import GCNConv
# from torch_geometric.utils import train_test_split_edges

def load_data(graph_name, node_types):
  db = GraphDB()

  db.drop_all_existing_graphs()  # alt: drop graph if exists rather than dropping all graphs 
  db.build_graph_native_projection(
      graph_name=graph_name,
      node_proj=node_types,
      relationship_proj="'*'"
  )

  dir_abspath = os.path.join(os.getcwd(), 'comptox_ai/db/exports', f"{graph_name}")
  try:
      shutil.rmtree(dir_abspath)
  except OSError as e:
      print("Error: %s : %s" % (dir_abspath, e.strerror))

  db.export_graph(graph_name)
  data = db.to_pytorch(graph_name, node_types)

  ## debugging
  print(f"data: {data}")
  print(f"data.x:\n\t{data.x}")
  print(f"data.edge_index:\n\t{data.edge_index}")

  ## train test split data
  print("Train test split beginning..")
  data = train_test_split_edges(data)
  # self.data = data.to(self.device)
  return data


class Net(torch.nn.Module):
  def __init__(self, in_channels, out_channels):
    super(Net, self).__init__()
    self.conv1 = GCNConv(in_channels, 128)
    self.conv2 = GCNConv(128, out_channels)

  def encode(self, x, edge_index):
    x = self.conv1(x, edge_index)
    x = x.relu()
    return self.conv2(x, edge_index)

  def decode(self, z, pos_edge_index, neg_edge_index):
    edge_index = torch.cat([pos_edge_index, neg_edge_index], dim=-1)
    return (z[edge_index[0]] * z[edge_index[1]]).sum(dim=-1)

  def decode_all(self, z):
    prob_adj = z @ z.t()
    return (prob_adj > 0).nonzero(as_tuple=False).t()


def get_link_labels(pos_edge_index, neg_edge_index, device):
    num_links = pos_edge_index.size(1) + neg_edge_index.size(1)
    link_labels = torch.zeros(num_links, dtype=torch.LongTensor, device=device)  # originally- dtype=torch.Float
    link_labels[:pos_edge_index.size(1)] = 1.
    return link_labels


def train(data, model, optimizer):
    model.train()

    neg_edge_index = negative_sampling(
        edge_index=data.train_pos_edge_index, num_nodes=data.num_nodes,
        num_neg_samples=data.train_pos_edge_index.size(1))

    optimizer.zero_grad()
    z = model.encode(data.x, data.train_pos_edge_index)
    link_logits = model.decode(z, data.train_pos_edge_index, neg_edge_index)
    link_labels = get_link_labels(data.train_pos_edge_index, neg_edge_index)
    loss = F.binary_cross_entropy_with_logits(link_logits, link_labels)
    loss.backward()
    optimizer.step()

    return loss


@torch.no_grad()
def test(data, model):
    model.eval()

    z = model.encode(data.x, data.train_pos_edge_index)

    results = []
    for prefix in ['val', 'test']:
        pos_edge_index = data[f'{prefix}_pos_edge_index']
        neg_edge_index = data[f'{prefix}_neg_edge_index']
        link_logits = model.decode(z, pos_edge_index, neg_edge_index)
        link_probs = link_logits.sigmoid()
        link_labels = get_link_labels(pos_edge_index, neg_edge_index)
        results.append(roc_auc_score(link_labels.cpu(), link_probs.cpu()))
    return results

def run_model(data, model, optimizer):
  best_val_auc = test_auc = 0
  for epoch in range(1, 101):
      loss = train(data, model, optimizer)
      val_auc, tmp_test_auc = test(data, model)
      if val_auc > best_val_auc:
          best_val = val_auc
          test_auc = tmp_test_auc
      print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}, Val: {val_auc:.4f}, '
            f'Test: {test_auc:.4f}')

  z = model.encode(data.x, data.train_pos_edge_index)
  final_edge_index = model.decode_all(z)