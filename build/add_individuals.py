#!/usr/bin/env python3

from owlready2 import get_ontology
import pandas as pd

import ipdb, traceback, sys

ONTOLOGY_FNAME = "../comptox.rdf"
ONTOLOGY_POPULATED_FNAME = "../comptox_populated.rdf"


def summarize_graph(grph):
    print("Entities in graph: {0}".format(len(grph)))
    print("Number of nodes: {0}".format(len(grph.all_nodes())))

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
for idx,n in hetio_nodes.iterrows():
    nodetype = n[2]
    if nodetype=="Anatomy":
        ont.StructuralEntity(n[1].replace(" ","_"), xrefUberon=n[0].split("::")[-1])
    elif nodetype=="BiologicalProcess":
        continue
    elif nodetype=="CellularComponent":
        continue
    elif nodetype=="Compound":
        # NOTE: "Compounds" in hetionet are DrugBank entities,
        # which correspond most closely to "Chemical"s in comptox
        name = n[1]
        drugbank_id = n[0].split("::")[-1]
        ont.Chemical(name.replace(" ","_"), xrefDrugbank=drugbank_id, chemicalIsDrug=True, chemicalName=name)
    elif nodetype=="Disease":
        continue
    elif nodetype=="Gene":
        symbol = n[1]
        ncbi_gene = n[0].split("::")[-1]
        ont.Gene(symbol, geneSymbol=symbol, xrefNcbiGene=ncbi_gene)
    elif nodetype=="MolecularFunction":
        continue
    elif nodetype=="Pathway":
        continue
    elif nodetype=="Pharmacologic Class":
        continue
    elif nodetype=="Side Effect":
        continue
    elif nodetype=="Symptom":
        continue

# Add hetionet relationships:
# 1. chemicalBindsGene ("BINDS_CbG")
# 2. chemicalCausesEffect ("CAUSES_CcSE")
# 3. diseaseRegulatesGeneOther ("ASSOCIATES_DaG")
# 4. diseaseUpregulatesGene ("UPREGULATES_DuG")
# 5. diseaseDownregulatesGene ("DOWNREGULATES_DdG")


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

# Write modified graph (TO DIFFERENT FILE)
try:
    ont.save(file=ONTOLOGY_POPULATED_FNAME, format="rdfxml")
except TypeError:
    extype, value, tb = sys.exc_info()
    traceback.print_exc()
    ipdb.post_mortem(tb)
