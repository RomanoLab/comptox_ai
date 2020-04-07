from .databases import Database
from comptox_ai.build.build_all import ScreenManager

import pandas as pd
import numpy as np
import owlready2
from tqdm import tqdm

import os
import re
import itertools

# from pathos.multiprocessing import ProcessingPool as Pool
# import dill
# dill.detect.trace(True)

import ipdb


def process_edges(rels, medge_func_map):

    # ipdb.set_trace()

    for _, r in tqdm(rels.iterrows(), total=len(rels), desc="    "):
        edge_type = r[1]
        func = medge_func_map[edge_type]

        if func:
            func(edge_row=r)


class Hetionet(Database):
    # def __init__(self, scr, path_or_file="/data1/translational/hetionet", name="Hetionet"):
    def __init__(self, scr, config, name="Hetionet"):
        super().__init__(name=name, scr=scr, config=config)
        self.path = os.path.join(self.config.data_prefix, 'hetionet')
        self.requires = None

    def make_safe_property_label(self, label):
        """Convert the label ("name") of a property to a safe format.

        We follow the convention that only class names can begin with an
        uppercase letter. This can be explained using the following example:
        One of the 'pathways' in Hetionet is named "Disease", but Disease is
        already a class in the ontology. Therefore, there is no way to
        distinguish between these two entities in Python.

        This may have to be reevaluated later, if lowercasing entity names is
        leading to more problems down the line.
        """
        safe = re.sub(r"[!@#$,()\'\"]", "", label)
        safe = safe.replace(" ", "_").lower()

        return safe

    def prepopulate(self, owl: owlready2.namespace.Ontology, cai_ont: owlready2.namespace.Ontology):
        pass

    def fetch_raw_data(self):
        self.hetio_nodes = pd.read_csv(
            os.path.join(self.path, "hetionet-v1.0-nodes.tsv"), sep="\t"
        )
        self.hetio_rels = pd.read_csv(
            os.path.join(self.path, "hetionet-v1.0-edges.sif"), sep="\t"
        )

    def parse(
        self, owl: owlready2.namespace.Ontology, cai_ont: owlready2.namespace.Ontology
    ):
        self.cai_ont = cai_ont

        self.scr.draw_progress_page("===Parsing Hetionet===")
        prog_step = 1

        self.scr.add_progress_step("Adding primary node types", prog_step)
        prog_step += 1

        # Nodes:
        for _, n in tqdm(
            self.hetio_nodes.iterrows(), total=len(self.hetio_nodes), desc="    "
        ):
            nodetype = n[2]
            nm = n[1]
            safe_nm = self.make_safe_property_label(nm)

            # # Check whether node label already exists:
            # duplicate_nm = False
            # if ont[nm] is not None:
            #     duplicate_nm = True

            if nodetype == "Anatomy":
                # if duplicate_nm:
                #     nm += "_structuralentity"
                self.cai_ont.StructuralEntity(
                    "se_" + safe_nm, xrefUberon=n[0].split("::")[-1], commonName=nm
                )
            elif nodetype == "Biological Process":
                continue
            elif nodetype == "Cellular Component":
                continue
            elif nodetype == "Compound":
                # NOTE: "Compounds" in hetionet are DrugBank entities,
                # which correspond most closely to "Chemical"s in comptox
                # if duplicate_nm:
                #     nm += "_chemical"

                drugbank_id = n[0].split("::")[-1]
                self.cai_ont.Chemical(
                    "chem_" + safe_nm,
                    xrefDrugbank=drugbank_id,
                    chemicalIsDrug=True,
                    commonName=nm,
                )
            elif nodetype == "Disease":
                # if duplicate_nm:
                #     nm += "_disease"

                doid = n[0].split("::")[-1]
                dis = self.cai_ont.Disease("dis_" + safe_nm, commonName=nm)
                dis.xrefDiseaseOntology = [doid]
            elif nodetype == "Gene":
                # if duplicate_nm:
                #     nm += "_gene"

                ncbi_gene = n[0].split("::")[-1]
                self.cai_ont.Gene(
                    "gene_" + safe_nm,
                    geneSymbol=n[1],
                    xrefNcbiGene=ncbi_gene,
                    commonName=nm,
                )
            elif nodetype == "Molecular Function":
                continue
            elif nodetype == "Pathway":
                pass  # NOTE: Need to assess quality of "pathway" entities! E.g., why is "Immune System"
                # considered a pathway? And what do the identifiers mean (e.g., PC7_4688)???
                # try:
                #     hetio_id = n[0].split("::")[-1]
                #     p = self.cai_ont.Pathway(nm)
                #     p.xrefUnknownPathway.append(hetio_id)  # NOTE: can't assign to non-functional property during instantiation
                # except:
                #     ipdb.set_trace()
                #     print("Looks like something went wrong")
            elif nodetype == "Pharmacologic Class":
                # TODO: Add drug class to ontology
                continue
            elif nodetype == "Side Effect":
                # These nodes were sourced from SIDER, which - by definition - describes drug adverse effects.
                # if duplicate_nm:
                #     nm += "_adverseeffect"

                self.cai_ont.AdverseEffect(
                    "ae_" + safe_nm, xrefUmlsCUI=n[0].split("::")[-1], commonName=nm
                )
            elif nodetype == "Symptom":
                # NOTE: May need to revise knowledge model if symptoms can map to multiple MeSH terms (i.e.,
                # if the DbXref is not functional)
                # if duplicate_nm:
                #     nm += "_phenotype"

                self.cai_ont.Phenotype(
                    "phen_" + safe_nm, xrefMeSH=n[0].split("::")[-1], commonName=nm
                )

        # Relationships:
        # 1. chemicalBindsGene ("BINDS_CbG")
        # 2. chemicalCausesEffect ("CAUSES_CcSE")
        # 3. diseaseRegulatesGeneOther ("ASSOCIATES_DaG")
        # 4. diseaseUpregulatesGene ("UPREGULATES_DuG")
        # 5. diseaseDownregulatesGene ("DOWNREGULATES_DdG")
        self.scr.add_progress_step("Connecting nodes", prog_step)
        prog_step += 1
        self.metaedge_map = {
            "AdG": self.anatomyDownregulatesGene,
            "AeG": self.anatomyExpressesGene,
            "AuG": self.anatomyUpregulatesGene,
            "CbG": self.chemicalBindsGene,  # (:Chemical)-[:CHEMICAL_BINDS_GENE]->(:Gene)
            "CcSE": self.chemicalCausesEffect,  # (:Chemical)-[:CHEMICAL_CAUSES_EFFECT]->(:SideEffect)
            "CdG": None,
            "CpD": None,  # SKIP FOR NOW! Are palliative effects of chemicals important to us at this point?
            "CrC": None,
            "CtD": self.chemicalTreatsDisease,
            "CuG": None,
            "DaG": self.diseaseRegulatesGeneOther,
            "DdG": self.diseaseDownregulatesGene,
            "DlA": self.diseaseLocalizesToAnatomy,
            "DpS": None,
            "DrD": None,
            "DuG": self.diseaseUpregulatesGene,
            "GcG": None,
            "GiG": None,
            "GpBP": None,
            "GpCC": None,
            "GpMF": None,
            "GpPW": None,
            "Gr>G": None,
            "PCiC": None,
        }

        # NOTE: Need to rethink multiprocessing; it's not possible to serialize
        # self.cai_ont, or merge the results from multiple threads into a single
        # ontology object.

        # First, we split self.hetio_rels vertically into 8
        # smaller arrays.
        # split_rels = np.array_split(self.hetio_rels, 8)

        # Now, we construct a list of tuples
        # pool_func_args = zip(
        #     split_rels,
        #     itertools.repeat(self.metaedge_map),
        # )
        # pool_arg_1, pool_arg_2 = zip(*pool_func_args)
        # pool = Pool(nodes=8)
        # pool.map(process_edges, pool_arg_1, pool_arg_2)
        
        # process_edges(pool_arg_1[0], pool_arg_2[0])

        if True:
            process_edges(self.hetio_rels, self.metaedge_map)

    # Edge parsing methods:
    def chemicalBindsGene(self, edge_row):
        # match chemical via xrefDrugbank
        db_id = edge_row[0].split("::")[-1]
        gene_id = edge_row[2].split("::")[-1]

        chem = self.cai_ont.search_one(xrefDrugbank=db_id)
        gene = self.cai_ont.search_one(xrefNcbiGene=gene_id)

        if len(chem.chemicalBindsGene) == 0:
            chem.chemicalBindsGene = [gene]
        else:
            chem.chemicalBindsGene.append(gene)

    def chemicalCausesEffect(self, edge_row):
        db_id = edge_row[0].split("::")[-1]
        effect_id = edge_row[2].split("::")[-1]

        chem = self.cai_ont.search_one(xrefDrugbank=db_id)
        effect = self.cai_ont.search_one(xrefUmlsCUI=effect_id)

        if len(chem.chemicalCausesEffect) == 0:
            chem.chemicalCausesEffect = [effect]
        else:
            chem.chemicalCausesEffect.append(effect)

    def diseaseRegulatesGeneOther(self, edge_row):
        dis_id = edge_row[0].split("::")[-1]
        gene_id = edge_row[2].split("::")[-1]

        disease = self.cai_ont.search_one(xrefDiseaseOntology=dis_id)
        gene = self.cai_ont.search_one(xrefNcbiGene=gene_id)

        if len(disease.diseaseRegulatesGeneOther) == 0:
            disease.diseaseRegulatesGeneOther = [gene]
        else:
            disease.diseaseRegulatesGeneOther.append(gene)

    def diseaseDownregulatesGene(self, edge_row):
        dis_id = edge_row[0].split("::")[-1]
        gene_id = edge_row[2].split("::")[-1]

        disease = self.cai_ont.search_one(xrefDiseaseOntology=dis_id)
        gene = self.cai_ont.search_one(xrefNcbiGene=gene_id)

        if len(disease.diseaseDownregulatesGene) == 0:
            disease.diseaseDownregulatesGene = [gene]
        else:
            disease.diseaseDownregulatesGene.append(gene)

    def diseaseUpregulatesGene(self, edge_row):
        dis_id = edge_row[0].split("::")[-1]
        gene_id = edge_row[2].split("::")[-1]

        disease = self.cai_ont.search_one(xrefDiseaseOntology=dis_id)
        gene = self.cai_ont.search_one(xrefNcbiGene=gene_id)

        if len(disease.diseaseUpregulatesGene) == 0:
            disease.diseaseUpregulatesGene = [gene]
        else:
            disease.diseaseUpregulatesGene.append(gene)

    def chemicalTreatsDisease(self, edge_row):
        db_id = edge_row[0].split("::")[-1]
        dis_id = edge_row[2].split("::")[-1]

        chem = self.cai_ont.search_one(xrefDrugbank=db_id)
        disease = self.cai_ont.search_one(xrefDiseaseOntology=dis_id)

        if len(chem.chemicalTreatsDisease) == 0:
            chem.chemicalTreatsDisease = [disease]
        else:
            chem.chemicalTreatsDisease.append(disease)

    def anatomyDownregulatesGene(self, edge_row):
        db_anatomy = edge_row[0].split("::")[-1]
        db_gene = edge_row[2].split("::")[-1]

        anatomy = self.cai_ont.search_one(xrefUberon=db_anatomy)
        gene = self.cai_ont.search_one(xrefNcbiGene=db_gene)

        if len(anatomy.anatomyDownregulatesGene) == 0:
            anatomy.anatomyDownregulatesGene = [gene]
        else:
            anatomy.anatomyDownregulatesGene.append(gene)

    def anatomyUpregulatesGene(self, edge_row):
        db_anatomy = edge_row[0].split("::")[-1]
        db_gene = edge_row[2].split("::")[-1]

        anatomy = self.cai_ont.search_one(xrefUberon=db_anatomy)
        gene = self.cai_ont.search_one(xrefNcbiGene=db_gene)

        if len(anatomy.anatomyUpregulatesGene) == 0:
            anatomy.anatomyUpregulatesGene = [gene]
        else:
            anatomy.anatomyUpregulatesGene.append(gene)

    def anatomyExpressesGene(self, edge_row):
        db_anatomy = edge_row[0].split("::")[-1]
        db_gene = edge_row[2].split("::")[-1]

        anatomy = self.cai_ont.search_one(xrefUberon=db_anatomy)
        gene = self.cai_ont.search_one(xrefNcbiGene=db_gene)

        if len(anatomy.anatomyExpressesGene) == 0:
            anatomy.anatomyExpressesGene = [gene]
        else:
            anatomy.anatomyExpressesGene.append(gene)

    def diseaseLocalizesToAnatomy(self, edge_row):
        db_disease = edge_row[0].split("::")[-1]
        db_anatomy = edge_row[2].split("::")[-1]

        disease = self.cai_ont.search_one(xrefDiseaseOntology=db_disease)
        anatomy = self.cai_ont.search_one(xrefUberon=db_anatomy)

        if len(disease.diseaseLocalizesToAnatomy) == 0:
            disease.diseaseLocalizesToAnatomy = [anatomy]
        else:
            disease.diseaseLocalizesToAnatomy.append(anatomy)
