#!/usr/bin/env python3

from comptox_ai.scripts.build.build_all import ScreenManager

from abc import abstractmethod
import owlready2

import os
import re


class Database(object):
    def __init__(self, scr: ScreenManager, name: str, path_or_file: str):
        self.name = name
        self.scr = scr

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
    def parse(
        self, owl: owlready2.namespace.Ontology, cai_ont: owlready2.namespace.Ontology
    ):
        """Store in a controlled, internal representation that can be easily
        exported.
        """
        OWL = owl

        pass
