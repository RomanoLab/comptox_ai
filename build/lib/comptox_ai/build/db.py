#!/usr/bin/env python3
"""

"""

from ista import FlatFileDatabaseParser, MySQLDatabaseParser, load_kb
from ista.util import print_onto_stats

import os
from pathlib import Path
from yaml import load, Loader

import ipdb

import owlready2


def _get_default_config_file():
    root_dir = Path(__file__).resolve().parents[2]
    if os.path.exists(os.path.join(root_dir, "CONFIG.yaml")):
        default_config_file = os.path.join(root_dir, "CONFIG.yaml")
    else:
        default_config_file = os.path.join(root_dir, "CONFIG-default.yaml")
    return default_config_file

config_file = _get_default_config_file()
with open(config_file, "r") as fp:
    CONFIG = load(fp, Loader=Loader)
DATA_DIR = CONFIG["data"]["prefix"]
print("Data directory:", DATA_DIR)
OUT_DIR = CONFIG["data"]["outdir"]
print("Output will be written to:", OUT_DIR)


WARM_START = False

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
onto = owlready2.get_ontology("file://{}".format(os.path.join(repo_root, "comptox.rdf"))).load()

# open config file:
with open("../../CONFIG.yaml", 'r') as fp:
    cnf = load(fp, Loader=Loader)
mysql_config = dict()
mysql_config["host"] = cnf["mysql"]["host"]
mysql_config["user"] = cnf["mysql"]["user"]
mysql_config["passwd"] = cnf["mysql"]["passwd"]
if "socket" in cnf["mysql"]:
    mysql_config["socket"] = cnf["mysql"]["socket"]

#print("INITIAL ONTOLOGY STATISTICS:")
print_onto_stats(onto)

epa = FlatFileDatabaseParser("epa", onto, DATA_DIR)
ncbigene = FlatFileDatabaseParser("ncbigene", onto, DATA_DIR)
drugbank = FlatFileDatabaseParser("drugbank", onto, DATA_DIR)
hetionet = FlatFileDatabaseParser("hetionet", onto, DATA_DIR)
aopdb = MySQLDatabaseParser("aopdb", onto, mysql_config)
aopwiki = FlatFileDatabaseParser("aopwiki", onto, DATA_DIR)
tox21 = FlatFileDatabaseParser("tox21", onto, DATA_DIR)
disgenet = FlatFileDatabaseParser("disgenet", onto, DATA_DIR)

# Add nodes and node properties in a carefully specified order

if WARM_START:
    onto = owlready2.get_ontology("file://{}".format(os.path.join(repo_root, "comptox_mid.rdf"))).load()
else:
    #####################
    # EPA COMPTOX NODES #
    #####################
    epa.parse_node_type(
        node_type="Chemical",
        source_filename="PubChem_DTXSID_mapping_file.txt",
        fmt="tsv",
        parse_config={
            "iri_column_name": "DTXSID",
            "headers": True,
            "data_property_map": {
                "CID": onto.xrefPubchemCID,
                "SID": onto.xrefPubchemSID,
                "DTXSID": onto.xrefDTXSID,
            },
        },
        merge=False,
        skip=False
    )
    epa.parse_node_type(
        node_type="Chemical",
        source_filename="Dsstox_CAS_number_name.csv",
        fmt="csv",
        parse_config={
            "iri_column_name": "dsstox_substance_id",
            "headers": True,
            "data_property_map": {
                "casrn": onto.xrefCasRN,
                "preferred_name": onto.commonName,
                "dsstox_substance_id": onto.xrefDTXSID,
            },
            "merge_column": {
                "source_column_name": "dsstox_substance_id",
                "data_property": onto.xrefDTXSID,
            },
        },
        merge=True,
        skip=False
    )
    # with open("D:\\projects\\comptox_ai\\comptox_mid.rdf", "wb") as fp:
    #     onto.save(file=fp, format="rdfxml")

    epa.parse_node_type(
        node_type="Chemical",
        source_filename="CUSTOM/chemical_maccs_fingerprints.tsv",
        fmt="tsv",
        parse_config={
            "iri_column_name": "DTXSID",
            "headers": True,
            "data_property_map": {
                "DTXSID": onto.xrefDTXSID,
                "MACCS": onto.maccs
            },
            "merge_column": {
                "source_column_name": "DTXSID",
                "data_property": onto.xrefDTXSID
            }
        },
        merge=True,
        skip_create_new_node=True,  # Don't create an empty chemical node with just a MACCS property if the CID isn't already in the ontology
        skip=False
    )

    ##################
    # CHEMICAL LISTS #
    ##################
    epa.parse_node_type(
        node_type="ChemicalList",
        source_filename="CUSTOM/Chemical Lists.tsv",
        fmt="tsv",
        parse_config={
            "iri_column_name": "LIST_ACRONYM",
            "headers": True,
            "data_property_map": {
                "LIST_ACRONYM": onto.listAcronym,
                "LIST_NAME": onto.commonName,
                "LIST_DESCRIPTION": onto.listDescription
            },
            "data_transforms": {
                "LIST_ACRONYM": lambda x: x.split('/')[-1]
            }
        },
        merge=False,
        skip=False
    )

    ###############################
    # Chemical List relationships #
    ###############################
    epa.parse_relationship_type(
        relationship_type=onto.listIncludesChemical,
        inverse_relationship_type=onto.chemicalInList,
        source_filename="CUSTOM/chemical_lists_relationships.tsv",
        fmt="tsv",
        parse_config = {
            "subject_node_type": onto.ChemicalList,
            "subject_column_name": "list_acronym",
            "subject_match_property": onto.listAcronym,
            "object_node_type": onto.Chemical,
            "object_column_name": "casrn",
            "object_match_property": onto.xrefCasRN,
            "headers": True
        },
        merge=True,
        skip=False
    )

    if os.name == 'nt':
        print("SAVING INITIAL CHEMICAL DATA...")
        with open("D:\\projects\\comptox_ai\\comptox_mid.rdf", "wb") as fp:
            onto.save(file=fp, format="rdfxml")
    elif os.name == 'posix':
        print("SAVING INITIAL CHEMICAL DATA...")
        with open(os.path.join(repo_root, "comptox_mid.rdf"), "wb") as fp:
            onto.save(file=fp, format="rdfxml")
    else:
        raise NotImplementedError("Whoops!")

    #onto = owlready2.get_ontology("file://{}".format(os.path.join(repo_root, "comptox_mid.rdf"))).load()

# Synonyms
epa.parse_node_type(
    node_type="Chemical",
    source_filename="CUSTOM/synonyms.tsv",
    fmt="tsv",
    parse_config={
        "iri_column_name": "DTXSID",
        "headers": True,
        "data_property_map": {
            "DTXSID": onto.xrefDTXSID,
            "synonyms": onto.synonyms
        },
        "merge_column": {
            "source_column_name": "DTXSID",
            "data_property": onto.xrefDTXSID
        }
    },
    merge=True,
    skip_create_new_node=True,
    skip=False
)

# SMILES strings
epa.parse_node_type(
    node_type="Chemical",
    source_filename="CUSTOM/dsstox_smiles_for_maccs.tsv",
    fmt="tsv",
    parse_config={
        "iri_column_name": "DSSTox_Substance_ID",
        "headers": True,
        "data_property_map": {
            "DSSTox_Substance_ID": onto.xrefDTXSID,
            "SMILES": onto.SMILES
        },
        "merge_column": {
            "source_column_name": "DSSTox_Substance_ID",
            "data_property": onto.xrefDTXSID
        }
    },
    merge=True,
    skip_create_new_node=True,
    skip=False
)


##################
# DRUGBANK NODES #
##################
drugbank.parse_node_type(
    node_type="Chemical",
    source_filename="drug_links.csv",
    fmt="csv",
    parse_config={
        "iri_column_name": "DrugBank ID",
        "headers": True,
        "data_property_map": {
            "DrugBank ID": onto.xrefDrugbank,
            "CAS Number": onto.xrefCasRN
        },
        "merge_column": {
            "source_column_name": "CAS Number",
            "data_property": onto.xrefCasRN,
        },
    },
    merge=True,
    skip=False
)

###################
# NCBI GENE NODES #
###################
ncbigene.parse_node_type(
    node_type="Gene",
    source_filename="Homo_sapiens.gene_info",
    fmt="tsv-pandas",
    parse_config={
        "compound_fields": {
            "dbXrefs": {"delimiter": "|", "field_split_prefix": ":"}
        },
        "iri_column_name": "Symbol",
        "headers": True,
        "data_property_map": {
            "GeneID": onto.xrefNcbiGene,
            "Symbol": onto.geneSymbol,
            "type_of_gene": onto.typeOfGene,
            "Full_name_from_nomenclature_authority": onto.commonName,
            "MIM": onto.xrefOMIM,
            "HGNC": onto.xrefHGNC,
            "Ensembl": onto.xrefEnsembl,
            # TODO: Parse Feature_type and other columns
        },
    },
    merge=False,
    skip=False
)

##################
# DISGENET NODES #
##################
disgenet.parse_node_type(
    node_type="Disease",
    source_filename="disease_mappings_to_attributes.tsv",
    fmt="tsv-pandas",
    parse_config={
        "iri_column_name": "diseaseId",
        "headers": True,
        "data_property_map": {
            "diseaseId": onto.xrefUmlsCUI,
            "name": onto.commonName,
        }
    },
    merge=False,
    skip=False
)

################
# AOP-DB NODES #
################
aopdb.parse_node_type(
    node_type="AOP",
    source_table="aop_info",
    parse_config={
        "iri_column_name": "AOP_id",
        "data_property_map": {
            "AOP_name": onto.commonName,
            "AOP_id": onto.xrefAOPWikiAOPID,
        },
    },
    merge=False,
    skip=False
)
aopdb.parse_node_type(
    node_type="KeyEvent",
    source_table="event_info",
    parse_config={
        "iri_column_name": "event_id",
        "data_property_map": {
            "event_name": onto.commonName,
            "event_id": onto.xrefAOPWikiKEID,
        },
        "data_transforms": {
            "name": lambda x: x.split("; ")[0].strip()  # For some reason, a lot of the event names are duplicated
        },
    },
    merge=False,
    skip=False
)
aopdb.parse_node_type(
    node_type="MolecularInitiatingEvent",
    source_table="event_info",
    parse_config={
        "iri_column_name": "event_id",
        "data_property_map": {"event_id": onto.xrefAOPWikiKEID},
        "filter_column": "event_type",
        "filter_value": "molecular-initiating-event",
        "merge_column": {
            "source_column_name": "event_id",
            "data_property": onto.xrefAOPWikiKEID,
        },
    },
    merge=True,
    append_class=True,
    existing_class="KeyEvent",
    skip=False
)
aopdb.parse_node_type(
    node_type="AdverseOutcome",
    source_table="event_info",
    parse_config={
        "iri_column_name": "event_id",
        "data_property_map": {"event_id": onto.xrefAOPWikiKEID},
        "filter_column": "event_type",
        "filter_value": "adverse-outcome",
        "merge_column": {
            "source_column_name": "event_id",
            "data_property": onto.xrefAOPWikiKEID,
        },
    },
    merge=True,
    append_class=True,
    existing_class="KeyEvent",
    skip=False
)
# To denote something as a stressor we just add the stressor ID to a
# Chemical node. 
# TODO: Make sure to link KeyEvent nodes to Chemicals
aopdb.parse_node_type(
    node_type="Chemical",
    source_table="stressor_info",
    parse_config={
        "iri_column_name": "DTX_id",
        "data_property_map": {"stressor_id": onto.xrefAOPWikiStressorID},
        "merge_column": {
            "source_column_name": "DTX_id",
            "data_property": onto.xrefDTXSID,
        },
    },
    merge=True,
    skip=False
)
# We also want to include AOPDB chemical IDs here (which happen to be MeSH terms)
aopdb.parse_node_type(
    node_type="Chemical",
    source_table="chemical_info",
    parse_config={
        "iri_column_name": "DTX_id",
        "data_property_map": {"ChemicalID": onto.xrefMeSH},
        "merge_column": {
            "source_column_name": "DTX_id",
            "data_property": onto.xrefDTXSID
        }
    },
    merge=True,
    skip=False
)
aopdb.parse_node_type(
    node_type="Pathway",
    source_table="stressor_info",
    parse_config={
        "iri_column_name": "path_id",
        "data_property_map": {
            "path_id": onto.pathwayId,
            "path_name": onto.commonName,
            "ext_source": onto.sourceDatabase,
        },
        "custom_sql_query": "SELECT DISTINCT path_id, path_name, ext_source FROM aopdb.pathway_gene WHERE tax_id = 9606;"
    },
    merge=False,
    skip=False
)


# Add relationships and relationship properties
# Options for "source_type":
#  - MySQL source:
#      - `join_table`: Each row in a table represents a relationship
#        between two entities each defined in their own tables
#      - `foreign_key`: Starting from the subject node, a relationship
#        is inferred by looking up the object node based on a foreign
#        key value in the subject's source table


########################
# AOP-DB RELATIONSHIPS #
########################
aopdb.parse_relationship_type(
    relationship_type=onto.keIncludedInAOP,
    inverse_relationship_type=onto.aopIncludesKE,
    parse_config = {
        "subject_node_type": onto.KeyEvent,
        "subject_column_name": "event_id",
        "subject_match_property": onto.xrefAOPWikiKEID,
        "object_node_type": onto.AOP,
        "object_column_name": "AOP_ids",
        "object_match_property": onto.xrefAOPWikiAOPID,
        "source_table_type": "foreignKey",
        "source_table": "event_info",
        "compound_fields": {
            "AOP_ids": {"delimiter": "; "}  # Notice the space after the ";"
        },
        "data_transforms": {
            "AOP_ids": lambda x: int(x)
        },
    },
    merge=False,
    skip=False
)
aopdb.parse_relationship_type(
    relationship_type=onto.chemicalIncreasesExpression,
    parse_config = {
        "subject_node_type": onto.Chemical,
        "subject_column_name": "DTX_id",
        "subject_match_property": onto.xrefDTXSID,
        "object_node_type": onto.Gene,
        "object_column_name": "entrez",
        "object_match_property": onto.xrefNcbiGene,
        "custom_sql_query": "SELECT * FROM aopdb.chemical_gene WHERE tax_id = 9606 AND InteractionActions LIKE '%increases^expression%';",  # only interested in human expression
        "source_table_type": "foreignKey",
        "source_table": "chemical_gene",
    },
    merge=False,
    skip=False
)
aopdb.parse_relationship_type(
    relationship_type=onto.chemicalDecreasesExpression,
    parse_config = {
        "subject_node_type": onto.Chemical,
        "subject_column_name": "DTX_id",
        "subject_match_property": onto.xrefDTXSID,
        "object_node_type": onto.Gene,
        "object_column_name": "entrez",
        "object_match_property": onto.xrefNcbiGene,
        "custom_sql_query": "SELECT * FROM aopdb.chemical_gene WHERE tax_id = 9606 AND InteractionActions LIKE '%decreases^expression%';",  # only interested in human expression
        "source_table_type": "foreignKey",
        "source_table": "chemical_gene",
    },
    merge=False,
    skip=False
)
aopdb.parse_relationship_type(
    relationship_type=onto.keyEventTriggeredBy,
    parse_config = {
        "subject_node_type": onto.KeyEvent,
        "subject_column_name": "event_id",
        "subject_match_property": onto.xrefAOPWikiKEID,
        "object_node_type": onto.Chemical,
        "object_column_name": "DTX_id",
        "object_match_property": onto.xrefDTXSID,
        "source_table_type": "foreignKey",
        "source_table": "aop_stressor",
    },
    merge=False,
    skip=False
)
aopdb.parse_relationship_type(
    relationship_type=onto.geneInPathway,
    inverse_relationship_type=onto.PathwayContainsGene,
    parse_config = {
        "subject_node_type": onto.Gene,
        "subject_column_name": "entrez",
        "subject_match_property": onto.xrefNcbiGene,
        "object_node_type": onto.Pathway,
        "object_column_name": "path_id",
        "object_match_property": onto.pathwayId,
        "custom_sql_query": "SELECT * FROM aopdb.pathway_gene WHERE tax_id = 9606;",
        "source_table_type": "foreignKey",
        "source_table": "pathway_gene",
    },
    merge=False,
    skip=False
)

##########################
# DISGENET RELATIONSHIPS #
##########################
disgenet.parse_relationship_type(
    relationship_type=onto.geneAssociatesWithDisease,
    source_filename="curated_gene_disease_associations.tsv",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Gene,
        "subject_column_name": "geneSymbol",
        "subject_match_property": onto.geneSymbol,
        "object_node_type": onto.Disease,
        "object_column_name": "diseaseId",
        "object_match_property": onto.xrefUmlsCUI,
        "filter_column": "diseaseType",
        "filter_value": "disease",
        "headers": True
    },
    merge=False,
    skip=False
)
# TODO: Evaluate disease-disease associations. In DisGeNET, it seems to be
# based on Jaccard distance of genes and variants overlap, which may not be
# right for ComptoxAI.
# For now: Use disease-disease associations from hetionet.

##########################
# HETIONET RELATIONSHIPS #
##########################
hetionet.parse_relationship_type(
    relationship_type=onto.chemicalIncreasesExpression,
    source_filename="hetionet-v1.0-edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Chemical,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefDrugbank,
        "object_node_type": onto.Gene,
        "object_column_name": "target",
        "object_match_property": onto.xrefNcbiGene,
        "filter_column": "metaedge",
        "filter_value": "CuG",
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split("::")[-1],
            "target": lambda x: int(x.split("::")[-1])  # I foresee this causing problems in the future - should all IDs be cast to str?
        },
    },
    merge=True,  # Merge with aopdb/ctd chemical-gene ixns
    skip=False
)
hetionet.parse_relationship_type(
    relationship_type=onto.chemicalDecreasesExpression,
    source_filename="hetionet-v1.0-edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Chemical,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefDrugbank,
        "object_node_type": onto.Gene,
        "object_column_name": "target",
        "object_match_property": onto.xrefNcbiGene,
        "filter_column": "metaedge",
        "filter_value": "CdG",
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split("::")[-1],
            "target": lambda x: int(x.split("::")[-1])  # I foresee this causing problems in the future - should all IDs be cast to str?
        },
    },
    merge=True,
    skip=False
),
hetionet.parse_relationship_type(
    relationship_type=onto.chemicalBindsGene,
    source_filename="hetionet-v1.0-edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Chemical,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefDrugbank,
        "object_node_type": onto.Gene,
        "object_column_name": "target",
        "object_match_property": onto.xrefNcbiGene,
        "filter_column": "metaedge",
        "filter_value": "CbG",
        "headers": True,
        "data_transforms": {
            "source": lambda x: x.split("::")[-1],
            "target": lambda x: int(x.split("::")[-1])  # I foresee this causing problems in the future - should all IDs be cast to str?
        },
    },
    merge=False,
    skip=False
)
hetionet.parse_relationship_type(
    relationship_type=onto.geneInteractsWithGene,
    source_filename="hetionet-v1.0-edges.sif",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Gene,
        "subject_column_name": "source",
        "subject_match_property": onto.xrefNcbiGene,
        "object_node_type": onto.Gene,
        "object_column_name": "target",
        "object_match_property": onto.xrefNcbiGene,
        "filter_column": "metaedge",
        "filter_value": "GiG",
        "headers": True,
        "data_transforms": {
            "source": lambda x: int(x.split("::")[-1]),
            "target": lambda x: int(x.split("::")[-1])  # I foresee this causing problems in the future - should all IDs be cast to str?
        },
    },
    merge=False,
    skip=False
)

# # Save the ontology to a new file
# with open("D:\\projects\\comptox_ai\\comptox_mid.rdf", "wb") as fp:
#     onto.save(file=fp, format="rdfxml")

aopwiki.parse_relationship_type(
    relationship_type=onto.keyEventTriggers,
    source_filename="aop_ke_ker.tsv",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.KeyEvent,
        "subject_column_name": "upstream_event_id",
        "subject_match_property": onto.xrefAOPWikiKEID,
        "object_node_type": onto.KeyEvent,
        "object_column_name": "downstream_event_id",
        "object_match_property": onto.xrefAOPWikiKEID,
        "filter_column": "direct_or_indirect",
        "filter_value": "adjacent",
        "headers": ["aop_id", "upstream_event_id", "downstream_event_id",
            "relationship_id", "direct_or_indirect",
            "evidence_for_relationship",
            "quantitative_understanding_for_relationship"],
        "data_transforms": {
            "upstream_event_id": lambda x: int(x.split(":")[-1]),
            "downstream_event_id": lambda x: int(x.split(":")[-1])
        }
    },
    merge=False,
    skip=False
)

tox21.parse_node_type(
    node_type="Assay",
    source_filename="tox21_assay_info.tsv",
    fmt="tsv",
    parse_config={
        "iri_column_name": "protocol_name",
        "headers": True,
        "data_property_map": {
            "protocol_name": onto.commonName,
            "assay_target": onto.assayTarget,
            "target_category": onto.targetCategory,
            "cell_line": onto.cellLine,
            "cell_type": onto.cellType
        }
    },
    merge=False,
    skip=False
)

tox21.parse_relationship_type(
    relationship_type=onto.chemicalHasActiveAssay,
    source_filename="tox21_assay_samples_all.tsv",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Chemical,
        "subject_column_name": "compound_pubchem_cid",
        "subject_match_property": onto.xrefPubchemCID,
        "object_node_type": onto.Assay,
        "object_column_name": "assay_name",
        "object_match_property": onto.commonName,
        "filter_column": "assay_outcome",
        "filter_value": "1",
        "headers": True,
        "data_transforms": {
            "compound_pubchem_cid": lambda x: x.split("_")[-1]
        }
    },
    merge=False,
    skip=False
)

tox21.parse_relationship_type(
    relationship_type=onto.chemicalHasInactiveAssay,
    source_filename="tox21_assay_samples_all.tsv",
    fmt="tsv",
    parse_config={
        "subject_node_type": onto.Chemical,
        "subject_column_name": "compound_pubchem_cid",
        "subject_match_property": onto.xrefPubchemCID,
        "object_node_type": onto.Assay,
        "object_column_name": "assay_name",
        "object_match_property": onto.commonName,
        "filter_column": "assay_outcome",
        "filter_value": "0",
        "headers": True,
        "data_transforms": {
            "compound_pubchem_cid": lambda x: x.split("_")[-1]
        }
    },
    merge=False,
    skip=False
)

ipdb.set_trace()

# Save the ontology to a new file
with open(os.path.join(OUT_DIR, "comptox_populated.rdf"), "wb") as fp:
    onto.save(file=fp, format="rdfxml")

print("Ontology build successful!")
print_onto_stats(onto)

def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False

if yes_or_no("Do you want to load the database into Neo4j right away?"):
    load_kb(os.path.join(OUT_DIR, "comptox_populated.rdf"))
