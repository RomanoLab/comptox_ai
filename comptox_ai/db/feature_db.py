"""
Document store interface.

Copyright (c) 2020 by Joseph D. Romano
"""

import os
import glob
import configparser
import urllib.parse
from pathlib import Path

from pymongo import MongoClient

ROOT_DIR = Path(__file__).resolve().parents[2]
if os.path.exists(os.path.join(ROOT_DIR, 'CONFIG.cfg')):
  DEFAULT_CONFIG_FILE = os.path.join(ROOT_DIR, 'CONFIG.cfg')
else:
  DEFAULT_CONFIG_FILE = os.path.join(ROOT_DIR, 'CONFIG-default.cfg')

class FeatureDB(object):
  """
  A database of feature data for entities in ComptoxAI, implemented as a
  document store in MongoDB.

  Parameters
  ----------
  config_file : str, default None
    Relative path to a config file containing a "NEO4J" block, as described
    below. If None, ComptoxAI will look in the ComptoxAI root directory for
    either a "CONFIG.cfg" file or "CONFIG-default.cfg", in that order. If no
    config file can be found in any of those locations, an exception will be
    raised.
  verbose: bool, default True
    Sets verbosity to on or off. If True, status information will be returned
    to the user occasionally.
  """

  def __init__(self, config_file=None, verbose=True):
    self.verbose = verbose
    
    if not config_file:
      self.config_file = DEFAULT_CONFIG_FILE
    else:
      self.config_file = config_file

    self._connect()

  def _connect(self):
    assert self.config_file is not None

    cnf = configparser.ConfigParser()
    cnf.read(self.config_file)
    
    username = urllib.parse.quote_plus(cnf["MONGODB"]["Username"])
    password = urllib.parse.quote_plus(cnf["MONGODB"]["Password"])
    
    if (len(username) > 0) and (len(password) > 0):
      uri = "mongodb://{0}:{1}@127.0.0.1".format(username, password)
    else:
      uri = "mongodb://127.0.0.1"

    self._client = MongoClient(uri)

  def fetch(self):
    pass

  def get_corresponding_graph(self):
    pass