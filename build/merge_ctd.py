#!/usr/bin/env python3

from owlready2 import get_ontology
import pandas as pd
from tqdm import tqdm

import ipdb, traceback, sys

ONTOLOGY_FNAME = "../comptox.rdf"
ONTOLOGY_POPULATED_FNAME = "../comptox_populated.rdf"

ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"
ONTOLOGY_POPULATED_IRI = 'http://jdr.bio/ontologies/comptox-full.owl#'

OWL = get_ontology("http://www.w3.org/2002/07/owl#")


def safe_add_property(entity, prop, value):
    """Add a value to a property slot on a node.

    Importantly, the method below is compatible with both functional and
    non-functional properties. If a property is functional, it either
    creates a new list or extends an existing list.

    This function cuts down on boilerplate code considerably when setting
    many property values in the ontology.
    """
    if OWL.FunctionalProperty in prop.is_a:
        setattr(entity, prop._python_name, value)
    else:
        if len(getattr(entity, prop._python_name)) == 0:
            setattr(entity, prop._python_name, [value])
        else:
            getattr(entity, prop._python_name).append(value)


# Load graph
ont = get_ontology(ONTOLOGY_POPULATED_FNAME).load()


# Load mapping between drugbank ID and CAS RN
drugbank_map = pd.read_csv("../data/drug_links.csv")
# Add CAS RN where available
num_matches = 0
for idx, m_row in drugbank_map.iterrows():
    dbid = m_row[0]
    casrn = m_row[2]
    match = ont.search(xrefDrugbank=dbid)
    if len(match) > 0:
        if len(match) > 1:
            ipdb.set_trace()
        num_matches += 1
        safe_add_property(match[0], ont.xrefCasRN, casrn)
        
print(num_matches)

print("Reading objects (ontology, nodes, etc.) into memory...")


chemicals = pd.read_csv("~/projects/aop_neo4j/ctd_dumps/chemicals.csv")
for idx,c_row in chemicals.iterrows():
    casrn = c_row[0]
    mesh = c_row[1].split(":")[-1]
    name = c_row[2]

    # Is it in the ontology already?
    match = ont.search(xrefCasRN=casrn)
    if len(match) > 0:
        # yes it is

        safe_add_property(match[0], ont.chemicalIsInCTD, True)
        safe_add_property(match[0], ont.xrefMeSHUI, mesh)
del(chemicals)

diseases = pd.read_csv("~/projects/aop_neo4j/ctd_dumps/diseases.csv")
for idx, d_row in diseases.iterrows():
    mesh = c_row[0].split(":")[-1]
    ipdb.set_trace()
del (diseases)
