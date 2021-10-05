"""Input/output routines for ComptoxAI's graph database

io.py

Copyright (c) 2021 by Joseph D. Romano
"""

from comptox_ai.db import GraphDB
from comptox_ai.utils import _get_default_config_file, _make_timestamped_output_directory

from yaml import load, Loader
from pathlib import Path
import pandas as pd
import os
import datetime as dt


# FOR DEBUGGING ONLY:
NODE_LABELS = [
  'Gene',
  'Pathway',
  'Assay'
]
OUTPUT_TYPE = 'tsv'

class DbExporter():
  """Base class for exporting subgraphs from ComptoxAI's graph database.

  Notes
  -----
  Users shouldn't usually try to interact with this class directly. They should
  instead call the appropriate `GraphDB` method (e.g., `db.export()`).
  """
  def __init__(self, db: comptox_ai.db.GraphDB):
    self.db = db
    self.metagraph = db.get_metagraph()


class GraphExporter(DbExporter):
  """Exporter for serializing graphs to graph-like formats, meant for
  consumption by graph-based libraries (like DGL, PyTorch Geometric, networkx,
  etc.).

  Notes
  -----
  Users shouldn't usually try to interact with this class directly. They should
  instead call the appropriate `GraphDB` method (e.g., `db.export()`).
  """
  def __init__(self, db: comptox_ai.db.GraphDB):
    super().__init__(db)


class TabularExporter(DbExporter):
  """Exporter for serializing graphs to tabular formats, meant for secondary
  processing by 'traditional' (i.e., non-graph-based) tools, such as
  scikit-learn. Such tabular datasets are mainly useful for establishing
  baseline comparisons to the GraphML algorithms that make up the main focus of
  ComptoxAI's models.

  Notes
  -----
  Users shouldn't usually try to interact with this class directly. They should
  instead call the appropriate `GraphDB` method (e.g., `db.export()`).
  """
  def __init__(self, db: comptox_ai.db.GraphDB):
    super().__init__(db)