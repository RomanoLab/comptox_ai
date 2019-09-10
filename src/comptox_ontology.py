#!/usr/bin/env python3

"""
`ComptoxOntology` main class definition
"""

import owlready2
import rdflib
import os, sys
import networkx as nx
import numpy as np
import pandas as pd
import configparser

config = configparser.ConfigParser()
config.read('../NEO4J_CONFIG.cfg')

from cypher import queries

def run_formatted_cypher_query(tx, query):
    for record in tx.run(query):
        print(record)

class ComptoxOntology(object):
    """
    Base class for the Comptox Ontology and its related graph
    knowledge base.
    """
    def __init__(self,
                 uri = "bolt://localhost:7687"
                 username,
                 password):
        # set up Neo4j Bolt connection
        self.uri = uri
        self.username = username
        self.password = password
        try:
            self.driver = GraphDatabase.driver(self.uri,
                                               auth=(self.username,
                                                     self.password))
            self.driver_connected = True
        except:
            print("Error opening connection to Neo4j")
            self.driver_connected = False
            

    def close_connection(self):
        if self.driver_connected:
            self.driver.close()
        else:
            print("Error: Connection to Neo4j is not currently active")

    def open_connection(self,
                        uri = "bolt://localhost:7687"
                        username,
                        password):
        if not self.driver_connected:
            try:
                self.driver = GraphDatabase.driver(self.uri,
                                                   auth=(self.username,
                                                         self.password))
                self.driver_connected = True
            except:
                print("Error opening connection to Neo4j")
                self.driver_connected = False
        else:
            print("Error: Connection to Neo4j is already active.")
            print("       Use `.close_connection()` and try again.")

    def aopShortestPath(self, mie_node: str, ao_node: str):
        """Find the shortest path between an MIE and an adverse
        outcome using the Neo4j representation of the CO's knowledge
        base. 

        :param mie_node: string - name of the MIE
        :param ao_node: string - name of the adverse outcome
        """
        self.template = queries.MIE_DISEASE_PATH
        self.query = self.template.format(mie_node, ao_node)
        
        
