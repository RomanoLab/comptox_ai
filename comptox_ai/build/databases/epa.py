from .databases import Database
from .hetionet import Hetionet
from .ctd import CTD

import os

class EPA(Database):
    def __init__(self, scr, config, name="EPA"):
        super().__init__(name, path_or_file)
        self.path = os.path.join(self.config.data_prefix, 'epa')
        self.requires = [Hetionet, CTD]
