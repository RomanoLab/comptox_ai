from .databases import Database
from .hetionet import Hetionet
from .utils import safe_add_property, eval_list_field, make_safe_property_label

import pandas as pd
import owlready2
from tqdm import tqdm

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

class CTD(Database):
    def __init__(self, path_or_file="/data1/translational/ctd", name="CTD"):
        super().__init__(name, path_or_file)
        self.requires = [Hetionet]

    def prepopulate(self):
        # Build drugbank ID --> CASRN map
        self.drugbank_map = pd.read_csv("/data1/drug/drugbank/drug_links.csv")

        num_matches = 0
        for idx, m_row in self.drugbank_map.iterrows():
            dbid = m_row[0]
            casrn = m_row[2]
            if isinstance(casrn, float):  # If pandas thinks it is a float, that means it encountered NaN
                print("Skipping map parsing for drug: {0}".format(m_row[1]))
                continue
            match = self.cai_ont.search(xrefDrugbank=dbid)
            if len(match) > 0:
                if len(match) > 1:
                    # ipdb.set_trace()
                    raise RuntimeError("")
                num_matches += 1
                safe_add_property(match[0], self.cai_ont.xrefCasRN, casrn)

    def fetch_raw_data(self):
        # Nodes
        self.chemicals = pd.read_csv("~/projects/aop_neo4j/ctd_dumps/chemicals.csv")
        self.diseases = pd.read_csv("~/projects/aop_neo4j/ctd_dumps/diseases.csv")

        # Edges
        self.chem_dis = pd.read_csv("~/projects/aop_neo4j/ctd_dumps/chemical_disease.csv")

    def parse(self, owl: owlready2.namespace.Ontology, cai_ont: owlready2.namespace.Ontology):
        self.cai_ont = cai_ont
        # Chemicals
        for _, c_row in tqdm(self.chemicals.iterrows(), total=len(self.chemicals)):
            casrn = c_row[0]
            mesh = c_row[1].split(":")[-1]
            name = c_row[2]

            # Is it in the ontology already?
            match = self.cai_ont.search(xrefCasRN=casrn)
            if len(match) > 0:
                # yes it is

                safe_add_property(match[0], self.cai_ont.chemicalIsInCTD, True)
                safe_add_property(match[0], self.cai_ont.xrefMeSHUI, mesh)

        # Diseases
        for _, d_row in tqdm(self.diseases.iterrows(), total=len(self.diseases)):
            mesh             = d_row[0].split(":")[-1]
            nm               = d_row[1]
            alt_ids          = eval_list_field(d_row[2])
            tree_nums        = eval_list_field(d_row[3])
            parent_tree_nums = eval_list_field(d_row[4])

            doid = parse_ctd_doid(alt_ids)
            omim = parse_ctd_omim(alt_ids)

            safe_nm = make_safe_property_label(nm)

            disease = None  # Make sure this variable remains in scope

            if len(doid) == 0:
                # No DOID for this disease in CTD; create disease using MeSH
                
                disease = self.cai_ont.Disease("dis_"+safe_nm, xrefMeSH=mesh, commonName=nm)
                # TODO: UNCOMMENT THESE LINES AFTER xrefOMIM IS BUILT INTO THE ONTOLOGY
                # if len(omim) > 0:
                #     disease.xrefOMIM = omim
            else:
                # We have at least one DOID in CTD for this disease

                # First, do we have multiple diseases already for this MeSH disease?
                matches = []
                for x in doid:
                    res = self.cai_ont.search(xrefDiseaseOntology=x)
                    if (len(res) > 0):
                        [matches.append(xx) for xx in res]

                if len(matches) == 0:
                    # We made it this far, so we can create a new disease
                    try:
                        disease = self.cai_ont.Disease("dis_"+safe_nm, xrefMeSH=mesh, commonName=nm)
                        disease.xrefDiseaseOntology = doid
                    except TypeError:
                        print("Error creating node '{0}' - skipping".format(nm))
                        continue
                elif len(matches) == 1:
                    # We have one (and only one) matching disease; we can just edit it
                    disease = matches[0]
                    [safe_add_property(disease, self.cai_ont.xrefDiseaseOntology, d) for d in doid]
                    disease.xrefMeSH = mesh
                else:
                    # Uh oh, we have multiple matching diseases in the ontology. Need to reassess...
                    num_ambiguities += 1
                    #ipdb.set_trace()
                    print("Whoopsie! {0}".format(nm))

        # Chemicals <-> Diseases
        unmatched_chem_dis_count = 0
        num_chem_dis_added = 0
        for idx, cd_row in tqdm(chem_dis.iterrows(), total=len(chem_dis)):
            # Check to make sure we have both the chemical and the disease
            chem_mesh = cd_row[1].split(":")[-1]
            chem = self.cai_ont.search(xrefMeSHUI=chem_mesh)  # NOTE: Need to use xrefMeSHUI here
            dis_mesh = cd_row[5].split(":")[-1]
            dis = self.cai_ont.search(xrefMeSH=dis_mesh)

            if len(chem) == 0 or len(dis) == 0:
                #ipdb.set_trace()
                unmatched_chem_dis_count += 1
            elif len(dis) == 0:
                raise RuntimeError
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
                    print("Wait a minute...")
