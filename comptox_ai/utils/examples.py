"""
A collection of functions that generate example objects, particularly
useful for testing.
"""

import comptox_ai
import os

def load_full_graph():
    if os.path.exists('CONFIG.cfg'):
        CONFIG_FILE = 'CONFIG.cfg'
    else:
        CONFIG_FILE = 'CONFIG-default.cfg'
    
    c = comptox_ai.ComptoxAI(config_file=CONFIG_FILE)

    return c.graph
