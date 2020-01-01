#!/usr/bin/env python3

from ..build_all import ScreenManager, Config

from abc import abstractmethod
import owlready2

import os
import re


class Database(object):
    def __init__(self, scr: ScreenManager, config: Config, name: str):
        self.name = name
        self.scr = scr
        self.config = config

    @abstractmethod
    def prepopulate(self, owl: owlready2.namespace.Ontology, cai_ont: owlready2.namespace.Ontology):
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
