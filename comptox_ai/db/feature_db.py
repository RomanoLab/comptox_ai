"""
Document store interface.

Copyright (c) 2020 by Joseph D. Romano
"""

import os
import glob
import configparser
import urllib.parse
from pathlib import Path
from yaml import load, Loader

from pymongo import MongoClient

ROOT_DIR = Path(__file__).resolve().parents[2]
if os.path.exists(os.path.join(ROOT_DIR, 'CONFIG.yaml')):
  DEFAULT_CONFIG_FILE = os.path.join(ROOT_DIR, 'CONFIG.yaml')
else:
  DEFAULT_CONFIG_FILE = os.path.join(ROOT_DIR, 'CONFIG-default.yaml')

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

    # cnf = configparser.ConfigParser()
    # cnf.read(self.config_file)
    with open(self.config_file, 'r') as fp:
      cnf = load(fp, Loader=Loader)

    unm = cnf['mongodb']['username']
    pwd = cnf['mongodb']['password']
    username = urllib.parse.quote_plus(unm) if unm else ''
    password = urllib.parse.quote_plus(pwd) if pwd else ''
    
    if (len(username) > 0) and (len(password) > 0):
      uri = "mongodb://{0}:{1}@127.0.0.1".format(username, password)
    else:
      uri = "mongodb://127.0.0.1"

    self._client = MongoClient(uri)

  def is_connected(self):
    """
    Return True if the connection to MongoDB is active and valid.

    Returns
    -------
    bool
      `True` if there is an active connection to MongoDB, otherwise `False`.

    Notes
    -----
    This performs a pretty crude test at the moment - basically, if the client
    can see any databases, the check passes. A more robust approach might be
    good to implement in the future.
    """
    if isinstance(self._client.list_database_names(), list):
      return len(self._client.list_database_names()) > 0
    return False

  def fetch(self):
    pass

  def get_corresponding_graph(self):
    pass