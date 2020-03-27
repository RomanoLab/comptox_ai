from .databases import Database
from .hetionet import Hetionet
from .utils import safe_add_property, eval_list_field, eval_list_field_delim, make_safe_property_label

import os
import pandas as pd
import owlready2
from tqdm import tqdm

import ipdb

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
    def __init__(self, scr, config, name="CTD"):
        super().__init__(name=name, scr=scr, config=config)
        self.path = os.path.join(self.config.data_prefix, 'ctd')
        self.drugbank_path = os.path.join(self.config.data_prefix, 'drugbank')
        self.requires = [Hetionet]

    def prepopulate(self, owl: owlready2.namespace.Ontology, cai_ont: owlready2.namespace.Ontology):
        self.cai_ont = cai_ont
        
        # Build drugbank ID --> CASRN map
        drugbank_file = os.path.join(self.drugbank_path, 'drug_links.csv')
        self.drugbank_map = pd.read_csv(drugbank_file)

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
        self.chemicals = pd.read_csv(os.path.join(self.path, 'CTD_chemicals.csv'), comment='#')
        self.diseases = pd.read_csv(os.path.join(self.path, 'CTD_diseases.csv'), comment='#')

        # Edges
        self.chem_dis = pd.read_csv(os.path.join(self.path,"CTD_chemicals_diseases.csv"), comment='#')

    def parse(self, owl: owlready2.namespace.Ontology, cai_ont: owlready2.namespace.Ontology):
        self.cai_ont = cai_ont

        self.scr.draw_progress_page("===Parsing CTDBase===")
        prog_step = 1
        self.scr.add_progress_step("Adding chemicals", prog_step)
        prog_step += 1

        # NOTE: BIG CAVEAT:
        # The CSV files for CTD have the header lines commented out.
        # Currently, I just remove the "#" from the corresponding line, but
        # this isn't a sustainable solution. Will need to revisit.

        # Chemicals
        for _, c_row in tqdm(self.chemicals.iterrows(), total=len(self.chemicals)):
            name = c_row[0]
            mesh = c_row[1].split(":")[-1]
            casrn = c_row[2]

            # Is it in the ontology already?
            match = self.cai_ont.search(xrefCasRN=casrn)
            if len(match) > 0:
                # yes it is

                safe_add_property(match[0], self.cai_ont.chemicalIsInCTD, True)
                safe_add_property(match[0], self.cai_ont.xrefMeSHUI, mesh)

        self.scr.add_progress_step("Adding Diseases", prog_step)
        prog_step += 1

        # Diseases
        num_ambiguities = 0
        for _, d_row in tqdm(self.diseases.iterrows(), total=len(self.diseases)):
            nm               = d_row[0]
            mesh             = d_row[1].split(":")[-1]
            alt_ids          = eval_list_field_delim(d_row[2])
            tree_nums        = eval_list_field_delim(d_row[5])
            parent_tree_nums = eval_list_field_delim(d_row[6])

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
                    # TODO: Figure out some way to report ambiguities that doesn't look awful.
                    # print("Whoopsie! {0}".format(nm))

        self.scr.add_progress_step("Linking Chemicals to Diseases", prog_step)
        prog_step += 1

        # Set `True` to skip relationship parsing
        if True:
            return

        # Chemicals <-> Diseases
        unmatched_chem_dis_count = 0
        num_chem_dis_added = 0
        for idx, cd_row in tqdm(self.chem_dis.iterrows(), total=len(self.chem_dis)):
            # Check to make sure we have both the chemical and the disease
            chem_mesh = cd_row[1].split(":")[-1]
            chem = self.cai_ont.search(xrefMeSHUI=chem_mesh)  # NOTE: Need to use xrefMeSHUI here
            dis_mesh = cd_row[4].split(":")[-1]
            dis = self.cai_ont.search(xrefMeSH=dis_mesh)

            if len(chem) == 0 or len(dis) == 0:
                #ipdb.set_trace()
                unmatched_chem_dis_count += 1
            # elif len(dis) == 0:
            #     raise RuntimeError
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
