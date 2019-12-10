#!/usr/bin/env python3

from abc import abstractmethod
import os


__all__ = [
    "CTD",
    "Hetionet",
    "EPA"
]

class Database(object):
    def __init__(self, name: str, path_or_file: str):
        self.name = name

        if os.path.isfile(path_or_file):
            self.file = path_or_file
        elif os.path.exists(path_or_file):
            self.path = path_or_file
        else:
            raise FileNotFoundError("Error - data file or path does not exist")


    @abstractmethod
    def prepopulate(self):
        """Load any auxiliary data structures, like code mappings, etc.
        """
        pass

    @abstractmethod
    def fetch_raw_data(self):
        """Pull data into memory from the local filesystem.
        """
        pass

    @abstractmethod
    def parse(self, owl: owlready2.namespace.Ontology):
        """Store in a controlled, internal representation that can be easily
        exported.
        """
        OWL = owl

        pass

    
class CTD(Database):
    def __init__(self, path_or_file="/data1/translational/ctd", name="CTD"):
        super().__init__(name, path_or_file)
        self.requires = [
            Hetionet
        ]

class Hetionet(Database):
    def __init__(self, path_or_file, name="Hetionet"):
        super().__init__(name, path_or_file)
        self.requires = None

class EPA(Database):
    def __init__(self, path_or_file, name="EPA"):
        super().__init__(name, path_or_file)
        self.requires = [
            Hetionet,
            CTD
        ]