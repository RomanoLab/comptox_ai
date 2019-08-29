#!/usr/bin/env python3

from owlready2 import get_ontology
import pandas as pd
from tqdm import tqdm

import ipdb, traceback, sys, math

ONTOLOGY_FNAME = "../comptox.rdf"
ONTOLOGY_POPULATED_FNAME = "../comptox_populated.rdf"

ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"


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

OWL = get_ontology("http://www.w3.org/2002/07/owl#")

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

    # # Check whether node label already exists:
    # duplicate_nm = False
    # if ont[nm] is not None:
    #     duplicate_nm = True
    
    if nodetype=="Anatomy":
        # if duplicate_nm:
        #     nm += "_structuralentity"
        ont.StructuralEntity("se_"+nm, xrefUberon=n[0].split("::")[-1])
    elif nodetype=="Biological Process":
        continue
    elif nodetype=="Cellular Component":
        continue
    elif nodetype=="Compound":
        # NOTE: "Compounds" in hetionet are DrugBank entities,
        # which correspond most closely to "Chemical"s in comptox
        # if duplicate_nm:
        #     nm += "_chemical"
        
        drugbank_id = n[0].split("::")[-1]
        ont.Chemical("chem_"+nm, xrefDrugbank=drugbank_id, chemicalIsDrug=True)
    elif nodetype=="Disease":
        # if duplicate_nm:
        #     nm += "_disease"
        
        doid = n[0].split("::")[-1]
        dis = ont.Disease("dis_"+nm)
        dis.xrefDiseaseOntology = [doid]
    elif nodetype=="Gene":
        # if duplicate_nm:
        #     nm += "_gene"

        ncbi_gene = n[0].split("::")[-1]
        ont.Gene("gene_"+nm, geneSymbol=n[1], xrefNcbiGene=ncbi_gene)
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
        # if duplicate_nm:
        #     nm += "_adverseeffect"
        
        ont.AdverseEffect("ae_"+nm, xrefUmlsCUI=n[0].split("::")[-1])
    elif nodetype=="Symptom":
        # NOTE: May need to revise knowledge model if symptoms can map to multiple MeSH terms (i.e.,
        # if the DbXref is not functional)
        # if duplicate_nm:
        #     nm += "_phenotype"

        ont.Phenotype("phen_"+nm, xrefMeSH=n[0].split("::")[-1])
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

    if len(chem.chemicalTreatsDisease) == 0:
        chem.chemicalTreatsDisease = [disease]
    else:
        chem.chemicalTreatsDisease.append(disease)

def anatomyDownregulatesGene(edge_row):
    db_anatomy = edge_row[0].split("::")[-1]
    db_gene = edge_row[2].split("::")[-1]

    anatomy = ont.search_one(xrefUberon=db_anatomy)
    gene = ont.search_one(xrefNcbiGene=db_gene)

    if len(anatomy.anatomyDownregulatesGene) == 0:
        anatomy.anatomyDownregulatesGene = [gene]
    else:
        anatomy.anatomyDownregulatesGene.append(gene)

def anatomyUpregulatesGene(edge_row):
    db_anatomy = edge_row[0].split("::")[-1]
    db_gene = edge_row[2].split("::")[-1]

    anatomy = ont.search_one(xrefUberon=db_anatomy)
    gene = ont.search_one(xrefNcbiGene=db_gene)

    if len(anatomy.anatomyUpregulatesGene) == 0:
        anatomy.anatomyUpregulatesGene = [gene]
    else:
        anatomy.anatomyUpregulatesGene.append(gene)

def anatomyExpressesGene(edge_row):
    db_anatomy = edge_row[0].split("::")[-1]
    db_gene = edge_row[2].split("::")[-1]

    anatomy = ont.search_one(xrefUberon=db_anatomy)
    gene = ont.search_one(xrefNcbiGene=db_gene)

    if len(anatomy.anatomyExpressesGene) == 0:
        anatomy.anatomyExpressesGene = [gene]
    else:
        anatomy.anatomyExpressesGene.append(gene)

def diseaseLocalizesToAnatomy(edge_row):
    db_disease = edge_row[0].split("::")[-1]
    db_anatomy = edge_row[2].split("::")[-1]

    disease = ont.search_one(xrefDiseaseOntology=db_disease)
    anatomy = ont.search_one(xrefUberon=db_anatomy)

    if len(disease.diseaseLocalizesToAnatomy) == 0:
        disease.diseaseLocalizesToAnatomy = [anatomy]
    else:
        disease.diseaseLocalizesToAnatomy.append(anatomy)

# Add hetionet relationships:
# 1. chemicalBindsGene ("BINDS_CbG")
# 2. chemicalCausesEffect ("CAUSES_CcSE")
# 3. diseaseRegulatesGeneOther ("ASSOCIATES_DaG")
# 4. diseaseUpregulatesGene ("UPREGULATES_DuG")
# 5. diseaseDownregulatesGene ("DOWNREGULATES_DdG")
metaedge_map = {
    'AdG':  anatomyDownregulatesGene,
    'AeG':  anatomyExpressesGene,
    'AuG':  anatomyUpregulatesGene,
    'CbG':  chemicalBindsGene,  # (:Chemical)-[:CHEMICAL_BINDS_GENE]->(:Gene)
    'CcSE': chemicalCausesEffect,  # (:Chemical)-[:CHEMICAL_CAUSES_EFFECT]->(:SideEffect)
    'CdG':  None,
    'CpD':  None,  # SKIP FOR NOW! Are palliative effects of chemicals important to us at this point?
    'CrC':  None,
    'CtD':  chemicalTreatsDisease,
    'CuG':  None,
    'DaG':  diseaseRegulatesGeneOther,
    'DdG':  diseaseDownregulatesGene,
    'DlA':  diseaseLocalizesToAnatomy,
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

print("Linking nodes using Hetionet relationships...")
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


# # Load graph
# ont = get_ontology(ONTOLOGY_POPULATED_FNAME).load()


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
        
        disease = ont.Disease("dis_"+nm_safe, xrefMeSH=mesh)
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
                disease = ont.Disease("dis_"+nm_safe, xrefMeSH=mesh)
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

