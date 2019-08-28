#!/usr/bin/env python3

from owlready2 import get_ontology
import pandas as pd
from tqdm import tqdm

import ipdb, traceback, sys, math

ONTOLOGY_FNAME = "../comptox.rdf"
ONTOLOGY_POPULATED_FNAME = "../comptox_populated.rdf"
ONTOLOGY_POPULATED_LINKED_FNAME = "../comptox_populated_linked.rdf"

ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"

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
    #ipdb.set_trace()
    dbid = m_row[0]
    casrn = m_row[2]
    if isinstance(casrn, float):  # If pandas thinks it is a float, that means it encountered NaN
        print("Skipping map parsing for drug: {0}".format(m_row[1]))
        continue
    match = ont.search(xrefDrugbank=dbid)
    if len(match) > 0:
        if len(match) > 1:
            ipdb.set_trace()
        num_matches += 1
        safe_add_property(match[0], ont.xrefCasRN, casrn)
        
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

def parse_ctd_omim(altDiseaseIDs):
    matched_doids = []
    for x in altDiseaseIDs:
        if x[:5] == "OMIM:":
            matched_doids.append(x[5:])
    return matched_doids

num_ambiguities = 0

print("Merging diseases...")
diseases = pd.read_csv("~/projects/aop_neo4j/ctd_dumps/diseases.csv")
for idx, d_row in tqdm(diseases.iterrows(), total=len(diseases)):
    mesh             = d_row[0].split(":")[-1]
    nm               = d_row[1]
    alt_ids          = eval_list_field(d_row[2])
    tree_nums        = eval_list_field(d_row[3])
    parent_tree_nums = eval_list_field(d_row[4])

    doid = parse_ctd_doid(alt_ids)
    omim = parse_ctd_omim(alt_ids)

    disease = None  # Make sure this variable remains in scope

    if len(doid) == 0:
        # No DOID for this disease in CTD; create disease using MeSH
        nm_safe = nm.lower().replace(" ","_")
        disease = ont.Disease(nm_safe, xrefMeSH=mesh)
        # TODO: UNCOMMENT THESE LINES AFTER xrefOMIM IS BUILT INTO THE ONTOLOGY
        # if len(omim) > 0:
        #     disease.xrefOMIM = omim
    else:
        # We have at least one DOID in CTD for this disease

        # First, do we have multiple diseases already for this MeSH disease?
        matches = []
        for x in doid:
            res = ont.search(xrefDiseaseOntology=x)
            if (len(res) > 0):
                [matches.append(xx) for xx in res]

        if len(matches) == 0:
            # We made it this far, so we can create a new disease
            try:
                disease = ont.Disease(nm, xrefMeSH=mesh)
                disease.xrefDiseaseOntology = doid
            except TypeError:
                print("Error creating node '{0}' - skipping".format(nm))
                continue
        elif len(matches) == 1:
            # We have one (and only one) matching disease; we can just edit it
            disease = matches[0]
            [safe_add_property(disease, ont.xrefDiseaseOntology, d) for d in doid]
            disease.xrefMeSH = mesh
        else:
            # Uh oh, we have multiple matching diseases in the ontology. Need to reassess...
            num_ambiguities += 1
            #ipdb.set_trace()
            print("Whoopsie! {0}".format(nm))
print("Number of ambiguities: {0}".format(num_ambiguities))    
del(diseases)

print("Linking chemicals to diseases via CTD data...")
chem_dis = pd.read_csv("~/projects/aop_neo4j/ctd_dumps/chemical_disease.csv")
unmatched_chem_dis_count = 0
num_chem_dis_added = 0
for idx, cd_row in tqdm(chem_dis.iterrows(), total=len(chem_dis)):
    # Check to make sure we have both the chemical and the disease
    chem_mesh = cd_row[1].split(":")[-1]
    chem = ont.search(xrefMeSHUI=chem_mesh)  # NOTE: Need to use xrefMeSHUI here
    dis_mesh = cd_row[5].split(":")[-1]
    dis = ont.search(xrefMeSH=dis_mesh)

    if len(chem) == 0 or len(dis) == 0:
        #ipdb.set_trace()
        unmatched_chem_dis_count += 1
    elif len(dis) == 0:
        ipdb.set_trace()
    else:
        # We have a match for both the chemical and disease, we can add the relationship
        #safe_add_property(chem, ont.chemicalAssociatesWithDisease, dis)
        chem = chem[0]
        dis = dis[0]
        try:
            if len(chem.chemicalAssociatesWithDisease) == 0:
                chem.chemicalAssociatesWithDisease = [dis]
            else:
                chem.chemicalAssociatesWithDisease.append(dis)
            num_chem_dis_added += 1
        except AttributeError:
            ipdb.set_trace()
            print()
del(chem_dis)

print("Number of chemical-disease relationships that couldn't match to the database: {0}".format(unmatched_chem_dis_count))
print("Number of chemical-disease links added to the populated ontology: {0}".format(num_chem_dis_added))





print("Writing populated ontology to disk (as RDF-formatted XML)...")
try:
    ont.save(file=ONTOLOGY_POPULATED_LINKED_FNAME, format="rdfxml")
    pass
except TypeError:
    extype, value, tb = sys.exc_info()
    print("Uh oh, something went wrong when serializing the populated ontology to disk. Entering debug mode...")
    traceback.print_exc()
    ipdb.post_mortem(tb)

