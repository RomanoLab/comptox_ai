import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if os.path.exists(os.path.join(ROOT_DIR, 'CONFIG.cfg')):
  DEFAULT_CONFIG_FILE = os.path.join(ROOT_DIR, 'CONFIG.cfg')
else:
  DEFAULT_CONFIG_FILE = os.path.join(ROOT_DIR, 'CONFIG-default.cfg')

class FeatureDB(object):
  def __init__(self, config_file=None, verbose=True):
    if not config_file:
      self.config_file = DEFAULT_CONFIG_FILE
    else:
      self.config_file = config_file

    self._parse_config()

  def _parse_config():
    assert self.config_file is not None

  def fetch(self):
    pass

  def get_corresponding_graph(self):
    pass