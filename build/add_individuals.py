#!/usr/bin/env python3

from owlready2 import get_ontology
import pandas as pd
from tqdm import tqdm

import ipdb, traceback, sys

ONTOLOGY_FNAME = "../comptox.rdf"
ONTOLOGY_POPULATED_FNAME = "../comptox_populated.rdf"

ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"
ONTOLOGY_POPULATED_IRI = 'http://jdr.bio/ontologies/comptox-full.owl#'


def make_safe_property_label(label):
    """Convert the label ("name") of a property to a safe format.

    We follow the convention that only class names can begin with an uppercase letter.
    This can be explained using the following example: One of the 'pathways' in Hetionet
    is named "Disease", but Disease is already a class in the ontology. Therefore, there
    is no way to distinguish between these two entities in Python.

    This may have to be reevaluated later, if lowercasing entity names is leading to
    more problems down the line.
    """
    return label.replace(" ", "_").lower()

print("Reading objects (ontology, nodes, etc.) into memory...")

# Load graph
ont = get_ontology(ONTOLOGY_FNAME).load()

####
# Add general biomedical data
#### 

# Add hetionet nodes:
# 1. Genes
# 2. Drugs ("Compounds")
# 3. Diseases
# 4. Anatomic entities ("Anatomy")
hetio_nodes = pd.read_csv("../data/hetionet/hetionet-v1.0-nodes.tsv", sep="\t")
print("Adding Hetionet nodes as ontology individuals...")
for idx,n in tqdm(hetio_nodes.iterrows(), total=len(hetio_nodes)):
    nodetype = n[2]
    nm = make_safe_property_label(n[1])

    # Check whether node label already exists:
    duplicate_nm = False
    if ont[nm] is not None:
        duplicate_nm = True
    
    if nodetype=="Anatomy":
        if duplicate_nm:
            nm += "_structuralentity"
        ont.StructuralEntity(nm, xrefUberon=n[0].split("::")[-1])
    elif nodetype=="Biological Process":
        continue
    elif nodetype=="Cellular Component":
        continue
    elif nodetype=="Compound":
        # NOTE: "Compounds" in hetionet are DrugBank entities,
        # which correspond most closely to "Chemical"s in comptox
        if duplicate_nm:
            nm += "_chemical"
        
        drugbank_id = n[0].split("::")[-1]
        ont.Chemical(nm, xrefDrugbank=drugbank_id, chemicalIsDrug=True)
    elif nodetype=="Disease":
        if duplicate_nm:
            nm += "_disease"
        
        doid = n[0].split("::")[-1]
        ont.Disease(nm, xrefDiseaseOntology=doid)
    elif nodetype=="Gene":
        if duplicate_nm:
            nm += "_gene"

        ncbi_gene = n[0].split("::")[-1]
        ont.Gene(nm, geneSymbol=n[1], xrefNcbiGene=ncbi_gene)
    elif nodetype=="Molecular Function":
        continue
    elif nodetype=="Pathway":
        pass  # NOTE: Need to assess quality of "pathway" entities! E.g., why is "Immune System"
              # considered a pathway? And what do the identifiers mean (e.g., PC7_4688)???
        # try:
        #     hetio_id = n[0].split("::")[-1]
        #     p = ont.Pathway(nm)
        #     p.xrefUnknownPathway.append(hetio_id)  # NOTE: can't assign to non-functional property during instantiation
        # except:
        #     ipdb.set_trace()
        #     print("Looks like something went wrong")
    elif nodetype=="Pharmacologic Class":
        # TODO: Add drug class to ontology
        continue
    elif nodetype=="Side Effect":
        # These nodes were sourced from SIDER, which - by definition - describes drug adverse effects.
        if duplicate_nm:
            nm += "_adverseeffect"
        
        ont.AdverseEffect(nm, xrefUmlsCUI=n[0].split("::")[-1])
    elif nodetype=="Symptom":
        # NOTE: May need to revise knowledge model if symptoms can map to multiple MeSH terms (i.e.,
        # if the DbXref is not functional)
        if duplicate_nm:
            nm += "_phenotype"

        ont.Phenotype(nm, xrefMeSH=n[0].split("::")[-1])
del(hetio_nodes)

# Edge parsing functions:
def chemicalBindsGene(edge_row):
    # match chemical via xrefDrugbank
    db_id = edge_row[0].split("::")[-1]
    gene_id = edge_row[2].split("::")[-1]
    
    chem = ont.search_one(xrefDrugbank=db_id)
    gene = ont.search_one(xrefNcbiGene=gene_id)

    if len(chem.chemicalBindsGene) == 0:
        chem.chemicalBindsGene = [gene]
    else:
        chem.chemicalBindsGene.append(gene)

def chemicalCausesEffect(edge_row):
    db_id = edge_row[0].split("::")[-1]
    effect_id = edge_row[2].split("::")[-1]

    chem = ont.search_one(xrefDrugbank=db_id)
    effect = ont.search_one(xrefUmlsCUI=effect_id)

    if len(chem.chemicalCausesEffect) == 0:
        chem.chemicalCausesEffect = [effect]
    else:
        chem.chemicalCausesEffect.append(effect)
    
def diseaseRegulatesGeneOther(edge_row):
    dis_id = edge_row[0].split("::")[-1]
    gene_id = edge_row[2].split("::")[-1]

    disease = ont.search_one(xrefDiseaseOntology=dis_id)
    gene = ont.search_one(xrefNcbiGene=gene_id)

    if len(disease.diseaseRegulatesGeneOther) == 0:
        disease.diseaseRegulatesGeneOther = [gene]
    else:
        disease.diseaseRegulatesGeneOther.append(gene)

def diseaseDownregulatesGene(edge_row):
    dis_id = edge_row[0].split("::")[-1]
    gene_id = edge_row[2].split("::")[-1]

    disease = ont.search_one(xrefDiseaseOntology=dis_id)
    gene = ont.search_one(xrefNcbiGene=gene_id)

    if len(disease.diseaseDownregulatesGene) == 0:
        disease.diseaseDownregulatesGene = [gene]
    else:
        disease.diseaseDownregulatesGene.append(gene)

def diseaseUpregulatesGene(edge_row):
    dis_id = edge_row[0].split("::")[-1]
    gene_id = edge_row[2].split("::")[-1]

    disease = ont.search_one(xrefDiseaseOntology=dis_id)
    gene = ont.search_one(xrefNcbiGene=gene_id)

    if len(disease.diseaseUpregulatesGene) == 0:
        disease.diseaseUpregulatesGene = [gene]
    else:
        disease.diseaseUpregulatesGene.append(gene)

def chemicalTreatsDisease(edge_row):
    db_id = edge_row[0].split("::")[-1]
    dis_id = edge_row[2].split("::")[-1]
    
    chem = ont.search_one(xrefDrugbank=db_id)
    disease = ont.search_one(xrefDiseaseOntology=dis_id)

    try:
        if len(chem.chemicalTreatsDisease) == 0:
            chem.chemicalTreatsDisease = [disease]
        else:
            chem.chemicalTreatsDisease.append(disease)
    except:
        ipdb.set_trace()
        print()

# Add hetionet relationships:
# 1. chemicalBindsGene ("BINDS_CbG")
# 2. chemicalCausesEffect ("CAUSES_CcSE")
# 3. diseaseRegulatesGeneOther ("ASSOCIATES_DaG")
# 4. diseaseUpregulatesGene ("UPREGULATES_DuG")
# 5. diseaseDownregulatesGene ("DOWNREGULATES_DdG")
metaedge_map = {
    'AdG':  None,
    'AeG':  None,
    'AuG':  None,
    'CbG':  chemicalBindsGene,  # (:Chemical)-[:CHEMICAL_BINDS_GENE]->(:Gene)
    'CcSE': chemicalCausesEffect,  # (:Chemical)-[:CHEMICAL_CAUSES_EFFECT]->(:SideEffect)
    'CdG':  None,
    'CpD':  None,  # SKIP FOR NOW! Are palliative effects of chemicals important to us at this point?
    'CrC':  None,
    'CtD':  chemicalTreatsDisease,
    'CuG':  None,
    'DaG':  diseaseRegulatesGeneOther,
    'DdG':  diseaseDownregulatesGene,
    'DlA':  None,
    'DpS':  None,
    'DrD':  None,
    'DuG':  diseaseUpregulatesGene,
    'GcG':  None,
    'GiG':  None,
    'GpBP': None,
    'GpCC': None,
    'GpMF': None,
    'GpPW': None,
    'Gr>G': None,
    'PCiC': None,
}

hetio_rels = pd.read_csv("../data/hetionet/hetionet-v1.0-edges.sif", sep="\t")
for idx,r in tqdm(hetio_rels.iterrows(), total=len(hetio_rels)):
    edge_type = r[1]
    func = metaedge_map[edge_type]

    if func:
        func(edge_row=r)

 
# Add hetionet property keys:
# 1.

####
# Add toxicology data
####

# 1. Add toxins from CTDBase
# 2. Add exposure studies (and asserted entities)
# 3. Add chemical--disease links (annotate as coming from toxicology source)
# 4.

# Add AOP data:
# 1. Add key events
# 2. Specify (if not already done) key initiating events; LINK TO CHEMICALS
# 3. Link KEs to adverse outcomes (either link to AEs and then to Disease/Phenotype or remove AEs entirely)

# Some final housekeeping
# ont.name = 'comptox-full'  # Name needs to be different from unpopulated ontology
# ont.base_iri = ONTOLOGY_POPULATED_IRI

ipdb.set_trace()

# Write modified graph (TO DIFFERENT FILE)
print("Writing populated ontology to disk (as RDF-formatted XML)...")
try:
    ont.save(file=ONTOLOGY_POPULATED_FNAME, format="rdfxml")
    pass
except TypeError:
    extype, value, tb = sys.exc_info()
    print("Uh oh, something went wrong when serializing the populated ontology to disk. Entering debug mode...")
    traceback.print_exc()
    ipdb.post_mortem(tb)

