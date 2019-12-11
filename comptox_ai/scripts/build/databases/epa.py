from .databases import Database
from .hetionet import Hetionet
from .ctd import CTD

class EPA(Database):
    def __init__(self, path_or_file="/data1/chemical/epa", name="EPA"):
        super().__init__(name, path_or_file)
        self.requires = [Hetionet, CTD]
