#!/usr/bin/env python3

"""
`ComptoxAI` main class definition
"""

import owlready2
import rdflib
from neo4j import GraphDatabase
import os, sys
import networkx as nx
import numpy as np
import scipy as sp
import pandas as pd
import ipdb
import configparser

import nxneo4j

from .graph import Graph


class ComptoxAI(object):
    """
    Base class for the Comptox Ontology and its related graph
    knowledge base.
    """
    def __init__(self,
                 username = None,
                 password = None,
                 uri = None,
                 config_file = None):

        # Connect to neo4j and set up graph object
        if (username is None) or (password is None) or (uri is None):
            if config_file is not None:
                print("Loading configuration file...")

                config = configparser.ConfigParser()
                config.read(config_file)

                self.username = config['NEO4J']['Username']
                self.password = config['NEO4J']['Password']
                hostname = config['NEO4J']['Hostname']
                protocol = config['NEO4J']['Protocol']
                port = config['NEO4J']['Port']
                self.uri = "{0}://{1}:{2}".format(protocol, hostname, port)
                print(self.uri)
            else:
                print("Incomplete database configuration provided---aborting.")
        else:
            self.uri = uri
            self.username = username
            self.password = password
        try:
            #ipdb.set_trace()
            driver = GraphDatabase.driver(self.uri,
                                          auth=(self.username,
                                                self.password))

            self.graph = Graph(driver=driver)
            self.graph.driver_connected = True
        except Exception as ex:
            print("Error opening connection to Neo4j")
            print(ex)
            self.driver_connected = False

        # Create ontology
        # TODO
        self.ontology = None
