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

def eval_list_field(list_string):
    """Convert a list from a Neo4j CSV dump into a Python list.

    In the Neo4j database dumps, lists are stored as strings. Therefore,
    in order to use them as lists, we need to evaluate the string representation.
    """
    list_eval = eval(list_string)
    return list_eval


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

print("Merging chemicals...")
chemicals = pd.read_csv("~/projects/aop_neo4j/ctd_dumps/chemicals.csv")
for idx,c_row in tqdm(chemicals.iterrows(), total=len(chemicals)):
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

def parse_ctd_doid(altDiseaseIDs):
    matched_doids = []
    for x in altDiseaseIDs:
        if x[:3] == "DO:":
            matched_doids.append(x[3:])
    # if len(matched_doids) > 0:
    #     return matched_doids
    # else:
    #     return None
    return matched_doids

print("Merging diseases...")
diseases = pd.read_csv("~/projects/aop_neo4j/ctd_dumps/diseases.csv")
for idx, d_row in tqdm(diseases.iterrows(), total=len(diseases)):
    mesh             = d_row[0].split(":")[-1]
    nm               = d_row[1]
    alt_ids          = eval_list_field(d_row[2])
    tree_nums        = eval_list_field(d_row[3])
    parent_tree_nums = eval_list_field(d_row[4])

    doid = parse_ctd_doid(alt_ids)

    disease = None  # Make sure this variable remains in scope

    if len(doid) == 0:
        # No DOID; search using MeSH<->DOID mapping, else create new individual
        pass
    elif len(doid) == 1:
        # We have a singular match
        disease = ont.search(xrefDiseaseOntology=doid[0])
    else:
        # We have multiple matches

        # First, do we have multiple diseases already for this MeSH disease?
        matches = []
        for x in doid:
            res = ont.search(xrefDiseaseOntology=x)
            if (len(res) > 0):
                [matches.append(xx) for xx in res]

        if len(matches) == 0:
            # We made it this far, so we can create a new disease
            disease = ont.Disease(nm, xrefMeSH=mesh)
            disease.xrefDiseaseOntology = doid
        elif len(matches) == 1:
            # We have one (and only one) matching disease; we can just edit it
            disease = matches[0]
            [safe_add_property(disease, ont.xrefDiseaseOntology, d) for d in doid]
            disease.xrefMeSH = mesh
        else:
            # Uh oh, we have multiple matching diseases in the ontology. Need to reassess...
            ipdb.set_trace()
            print("Whoopsie!")
    
    
del(diseases)

print("Linking chemicals to diseases via CTD data...")
