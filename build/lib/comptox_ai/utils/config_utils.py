import os
from pathlib import Path
from yaml import load, Loader
import configparser

def _get_default_config_file():
    root_dir = Path(__file__).resolve().parents[2]
    if os.path.exists(os.path.join(root_dir, 'CONFIG.yaml')):
        default_config_file = os.path.join(root_dir, 'CONFIG.yaml')
    else:
        default_config_file = os.path.join(root_dir, 'CONFIG-default.yaml')
    return default_config_file

def load_config(config_file_path=None):
    """Load a ComptoxAI configuration file from the location specified.

    If the user does not provide a value for `config_file_path`, we will try to
    load a config file from the default location:

    Unix-like: ~/.comptoxai.cfg
    
    Windows: [%HOMEDRIVE%][%HOMEPATH%]\.comptoxai.cfg

    An example configuration file is included in the root directory of the
    ComptoxAI code repository, named "CONFIG-default.cfg".
    
    Parameters
    ----------
    config_file_path : str, optional
        Fully qualified path to a ComptoxAI configuration file, by default None

    Returns
    -------
    config : dict
        Dictionary containing configuration options for ComptoxAI. If the
        provided file does not exist, or there is no file found in the default
        location, None will be returned instead, and the user will be notified
        to try again.
    """
    
    if config_file_path:
        full_fname = config_file_path
    else:
        full_fname = _get_default_config_file()

    try:
        with open(full_fname, 'r') as fp:
            cnf = load(fp, Loader=Loader)
    except FileNotFoundError:
        print("Error: Config file not found. Refer to the documentation for " \
              "details:\n" \
              "http://comptox.ai/docs/guide/building.html")
        return None

    return dict(cnf)
