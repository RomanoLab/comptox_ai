#!/usr/bin/env python3

from owlready2 import get_ontology
import pandas as pd
from tqdm import tqdm

import ipdb, traceback, sys

ONTOLOGY_FNAME = "../comptox.rdf"
ONTOLOGY_POPULATED_FNAME = "../comptox_populated.rdf"
ONTOLOGY_POPULATED_LINKED_FNAME = "../comptox_populated_linked.rdf"

ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"
ONTOLOGY_POPULATED_IRI = 'http://jdr.bio/ontologies/comptox-full.owl#'

OWL = get_ontology("http://www.w3.org/2002/07/owl#")

ont = get_ontology("../comptox_populated_linked.rdf").load()

kes = pd.read_csv("../data/aop_ke_mie_ao.tsv",
                  sep="\t",
                  header=None,
                  names=['aop_id',
                         'key_event_id',
                         'key_event_type',
                         'key_event_name'])

kers = pd.read_csv("../data/aop_ke_ker.tsv",
                   sep="\t",
                   header=None,
                   names=['aop_id',
                          'upstream_event_id',
                          'downstream_event_id',
                          'relationship_id',
                          'direct_or_indirect',
                          'evidence',
                          'quantitative_understanding'])

ke_components = pd.read_csv("../data/aop_ke_ec.tsv",
                            sep="\t",
                            header=None,
                            names=['aop_id',
                                   'key_event_id',
                                   'action',
                                   'object_source',
                                   'object_ontology_id',
                                   'object_term',
                                   'process_source',
                                   'process_ontology_id',
                                   'process_term'])

print("=====================")
print("LOADED AOP-WIKI DATA:")
print()
print("==COUNT OF ENTITIES==")
print("Key events:              {0}".format(len(kes)))
print("Key event relationships: {0}".format(len(kers)))
print("Key event components:    {0}".format(len(ke_components)))
print()
print("=====================")

