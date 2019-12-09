#!/usr/bin/env python3

from abc import abstractmethod


__all__ = [
    "CTD",
    "Hetionet"
]

class Database(object):
    @abstractmethod
    def prepopulate(self):
        """
        
        Parameters
        ----------
        object : [type]
            [description]
        """

    @abstractmethod
    def parse(self, fname):
        pass

    @abstractmethod
    def merge(self, ontology):
        pass


class CTD(Database):
    pass

class Hetionet(Database):
    pass

class EPA(Database):
    pass