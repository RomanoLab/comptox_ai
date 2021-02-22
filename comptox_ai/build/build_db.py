'''
How the graph database is built:

- Iterate over node types
  - Iterate over databases, see if node is present
    - If appropriately named parse function is present, parse the nodes
    - Serialize nodes to HDF5
-Iterate over relationship types
  - Identify relationship type parse functions

Parsing function naming conventions:
- For nodes: parse_node_[DB]_[NODE]()
- For relationships: parse_rel_[DB]_[RELNAME]()

At any point, if the node or relationship function is not defined, it
will simply be skipped over (and logged).

'''

from dataclasses import dataclass
from typing import List, Dict
import uuid

@dataclass
class Node:
  """A single node to be added to the graph database."""
  labels: List(str)
  node_attributes: Dict
  uri: str

@dataclass
class Relationship:
  """A relationship linking two nodes in the graph database."""
  start_node: str
  end_node: str
  uri: str
  rel_attributes: Dict

class DbBuilder():
  def __init__(self, name, db_type, has_node_types):
    self.name = name
    self.db_type = db_type
    self.has_node_types = has_node_types

    self.read_source_databases()
    self.read_node_hierarchy()
    
    self.read_node_types()
    self.read_relationship_types()

    self.connect_to_hdf5_store()

  def parse_node_type(self, node_label):
    for db in self.source_dbs:
      if node_defined_in_db(db, node_label):
        try:
          func_name = infer_function_name(db, node_label)

        except NotImplementedError as e:


  def parse_relationship_type(self, relationship_label):
