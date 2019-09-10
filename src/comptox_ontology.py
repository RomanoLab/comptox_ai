#!/usr/bin/env python3

"""
`ComptoxOntology` main class definition
"""

import owlready2
import rdflib
from neo4j import GraphDatabase
import os, sys
import networkx as nx
import numpy as np
import pandas as pd
import ipdb
import configparser

config = configparser.ConfigParser()
config.read('../NEO4J_CONFIG.cfg')

from cypher import queries

def execute_cypher_transaction(tx, query):
    records = []
    for record in tx.run(query):
        print(record)
        records.append(record)
    return(records)

class ComptoxOntology(object):
    """
    Base class for the Comptox Ontology and its related graph
    knowledge base.
    """
    def __init__(self,
                 username = None,
                 password = None,
                 uri = None):
        # set up Neo4j Bolt connection
        if (username is None) or (password is None) or (uri is None):
            print("Incomplete authentication data provided---using local configuration file.")
            self.username = config['NEO4J']['Username']
            self.password = config['NEO4J']['Password']
            hostname = config['NEO4J']['Hostname']
            protocol = config['NEO4J']['Protocol']
            port = config['NEO4J']['Port']
            self.uri = "{0}://{1}:{2}".format(protocol, hostname, port)
        else:
            self.uri = uri
            self.username = username
            self.password = password
        try:
            #ipdb.set_trace()
            self.driver = GraphDatabase.driver(self.uri,
                                               auth=(self.username,
                                                     self.password))
            self.driver_connected = True
        except:
            print("Error opening connection to Neo4j")
            self.driver_connected = False

    def __del__(self):
        self.close_connection()

    def close_connection(self):
        if self.driver_connected:
            self.driver.close()
        else:
            print("Error: Connection to Neo4j is not currently active")

    def open_connection(self,
                        username,
                        password,
                        uri = "bolt://localhost:7687"):
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
            print("Error: Connection to Neo4j is already active")
            print("       (Use `.close_connection()` and try again)")

    def validate_connection_status(self):
        if not self.driver_connected:
            raise RuntimeError("Attempted to query Neo4j without an active database connection")
        return True

    def run_query_in_session(self, query):
        with self.driver.session() as session:
            query_response = session.read_transaction(execute_cypher_transaction,
                                                      query)
        return(query_response)

    def aopShortestPath(self, mie_node: str, ao_node: str):
        """Find the shortest path between an MIE and an adverse
        outcome using the Neo4j representation of the CO's knowledge
        base. 

        :param mie_node: string - name of the MIE
        :param ao_node: string - name of the adverse outcome
        """
        query_response = None

        if self.validate_connection_status():
            
            self.template = queries.MIE_DISEASE_PATH
            self.query = self.template.format(mie_node, ao_node)

            # Run the query
            query_response = self.run_query_in_session(self.query)

        return(query_response)

    def fetch_nodes_by_label(self, label):
        if label == None:
            print("No label provided -- skipping")
        else:
            self.template = queries.FETCH_NODES_BY_LABEL
            self.query = self.template.format(label)

            query_response = self.run_query_in_session(self.query)

            return(query_response)
        

# For testing basic functionality
if __name__=="__main__":
    co = ComptoxOntology()
    shortest_path = co.aopShortestPath("Event:888","Parkinsonian Disorders")
    adverse_outcomes = co.fetch_nodes_by_label("AdverseOutcome")
