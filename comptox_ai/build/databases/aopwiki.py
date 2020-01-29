from .databases import Database
from .utils import safe_add_property, eval_list_field, eval_list_field_delim, make_safe_property_label

import os
import pandas as pd
import owlready2
from lxml import etree
from tqdm import tqdm
import json

import ipdb

class AOPWiki(Database):
    def __init__(self, scr, config, name="AOP-Wiki"):
        super().__init__(name=name, scr=scr, config=config)
        self.path = os.path.join(self.config.data_prefix, 'aopwiki')
        
    def prepopulate(self, owl: owlready2.namespace.Ontology, cai_ont: owlready2.namespace.Ontology):
        self.aop_wiki = etree.parse(os.path.join(self.path, 'aop-wiki-xml-2019-07-01.xml'))
        root = self.aop_wiki.getroot()
        self.ex_chem = [x for x in root if x.tag.split("}")[-1] == 'chemical'][0]
        self.ex_stress = [x for x in root if x.tag.split("}")[-1] == 'stressor'][0]
        self.ex_aop = [x for x in root if x.tag.split("}")[-1] == 'aop'][0]
        self.aop_xml_list = [x for x in root if x.tag.split("}")[-1] == 'aop']

    def fetch_raw_data(self):
        self.kes = pd.read_csv(os.path.join(self.path, "aop_ke_mie_ao.tsv"),
                                sep="\t",
                                header=None,
                                names=['aop_id',
                                        'key_event_id',
                                        'key_event_type',
                                        'key_event_name'])

        self.kers = pd.read_csv(os.path.join(self.path, "aop_ke_ker.tsv"),
                                sep="\t",
                                header=None,
                                names=['aop_id',
                                        'upstream_event_id',
                                        'downstream_event_id',
                                        'relationship_id',
                                        'direct_or_indirect',
                                        'evidence',
                                        'quantitative_understanding'])

        self.ke_components = pd.read_csv(os.path.join(self.path, "aop_ke_ec.tsv"),
                                        sep="\t",
                                        header=None,
                                        names=['aop_id',
                                            'key_event_id',
                                            'action',
                                            'object_source',
                                            'object_ontology_id',
                                            'object_term',
                                            'process_source',
                                            'process_ontology_id',
                                            'process_term'])

        with open(os.path.join(self.path, "aops.json"), 'r', encoding="utf8") as fp:
            aop_json = json.load(fp)
        self.aop_dict = {}
        for a in aop_json:
            self.aop_dict[str(a['id'])] = a

    def parse(self, owl: owlready2.namespace.Ontology, cai_ont: owlready2.namespace.Ontology):

        self.scr.draw_progress_page("===Parsing AOP-Wiki data===")
        prog_step = 1

        self.scr.add_progress_step("Adding AOP nodes to the graph", prog_step)
        prog_step += 1
        
        # ADD AOP WIKI NODES TO GRAPH
        already_parsed_kes = []
        already_parsed_aops = []
        for i, ke in tqdm(self.kes.iterrows(), total=len(self.kes)):
            ke_type = ke.key_event_type
            ke_id = ke.key_event_id
            ke_name = ke.key_event_name
            ke_aop_id = ke.aop_id

            if ke_id in already_parsed_kes:
                continue  # Don't re-add something we've already seen
            already_parsed_kes.append(ke_id)

            # Prepend "ke_" to avoid name conflicts
            if ke_type == 'MolecularInitiatingEvent':
                safe_name = "mie_"+make_safe_property_label(ke_name)
            elif ke_type == 'KeyEvent':
                safe_name = "ke_"+make_safe_property_label(ke_name)
            elif ke_type == 'AdverseOutcome':
                safe_name = "ao_"+make_safe_property_label(ke_name)
            else:
                raise ValueError("Unknown key event type")

            # do we have a node already for the AOP?
            aop_id = ke.aop_id
            if aop_id in already_parsed_aops:
                existing_aop = True
            else:
                existing_aop = False

            if ke_type == 'MolecularInitiatingEvent':
                new_mie_node = cai_ont.MolecularInitiatingEvent(safe_name,
                                                            keyEventID=ke_id,
                                                            commonName=ke_name)
                if existing_aop:
                    # add this MIE to the AOP
                    aop_node = cai_ont.search(xrefAOPWiki=aop_id)
                    assert len(aop_node) == 1
                    aop_node = aop_node[0]
                    aop_node.aopHasMIE.append(new_mie_node)
                else:
                    # Create an AOP with this as an MIE
                    if aop_id.split(":")[-1] in self.aop_dict.keys(): # Don't do anything if it's an obsolete AOP
                        aop_data = self.aop_dict[aop_id.split(":")[-1]]
                        safe_aop_name = 'aop_'+make_safe_property_label(aop_data['short_name'])
                        new_aop_node = cai_ont.AOP(safe_aop_name, commonName=aop_data['short_name'])
                        new_aop_node.aopHasMIE = [new_mie_node]
                        
            elif ke_type == 'KeyEvent':
                new_ke_node = cai_ont.KeyEvent(safe_name,
                                        keyEventID=ke_id,
                                        commonName=ke_name)
                if existing_aop:
                    # add this MIE to the AOP
                    aop_node = cai_ont.search(xrefAOPWiki=aop_id)
                    assert len(aop_node) == 1
                    aop_node = aop_node[0]
                    aop_node.aopContainsKE.append(new_ke_node)
                else:
                    # Create an AOP with this as an MIE
                    if aop_id.split(":")[-1] in self.aop_dict.keys(): # Don't do anything if it's an obsolete AOP
                        aop_data = self.aop_dict[aop_id.split(":")[-1]]
                        safe_aop_name = 'aop_'+make_safe_property_label(aop_data['title'])
                        new_aop_node = cai_ont.AOP(safe_aop_name, commonName=aop_data['title'])
                        new_aop_node.aopContainsKE = [new_ke_node]

            elif ke_type == 'AdverseOutcome':
                new_ao_node = cai_ont.AdverseOutcome(safe_name,
                                                keyEventID=ke_id,
                                                commonName=ke_name)
                if existing_aop:
                    # add this MIE to the AOP
                    aop_node = cai_ont.search(xrefAOPWiki=aop_id)
                    assert len(aop_node) == 1
                    aop_node = aop_node[0]
                    aop_node.aopCausesAO.append(new_ao_node)
                else:
                    # Create an AOP with this as an MIE
                    if aop_id.split(":")[-1] in self.aop_dict.keys(): # Don't do anything if it's an obsolete AOP
                        aop_data = self.aop_dict[aop_id.split(":")[-1]]
                        safe_aop_name = 'aop_'+make_safe_property_label(aop_data['title'])
                        new_aop_node = cai_ont.AOP(safe_aop_name, commonName=aop_data['title'])
                        new_aop_node.aopCausesAO = [new_ao_node]

            else:
                raise ValueError("Unexpected key event type: {}".format(ke_type))

        self.scr.add_progress_step("Adding AOP-Wiki relationships to graph", prog_step)
        prog_step += 1

        # ADD AOP WIKI RELATIONSHIPS TO GRAPH
        already_parsed_kers = []
        for i,ker in tqdm(self.kers.iterrows(), total=len(self.kers)):
            aop_id = ker[0]
            rel_id = ker[3]
            upstream_event_id = ker[1]
            downstream_event_id = ker[2]
            adj_or_nonadj = ker[4]
            evidence = ker[5]
            quantitative = ker[6]

            if rel_id in already_parsed_kers:
                continue  # Don't re-add something we've already seen
            already_parsed_kers.append(rel_id)

            upstream_event = cai_ont.search(keyEventID=upstream_event_id)
            downstream_event = cai_ont.search(keyEventID=downstream_event_id)

            if (upstream_event == []) or (downstream_event == []):
                #ipdb.set_trace()
                print("mismatch: {}; {}".format(upstream_event_id, downstream_event_id))
                continue

            upstream_event = upstream_event[0]
            downstream_event = downstream_event[0]

            if upstream_event.keyEventTriggers == None:
                upstream_event.keyEventTriggers = [downstream_event]
            else:
                upstream_event.keyEventTriggers.append(downstream_event)

            if downstream_event.keyEventTriggeredBy == None:
                downstream_event.keyEventTriggeredBy = [upstream_event]
            else:
                downstream_event.keyEventTriggeredBy.append(upstream_event)

        # find all AOs that have a ke_component (i.e., likely linked to diseases)
        all_aos = cai_ont.search(is_a=cai_ont.AdverseOutcome)
        ao_event_ids = [x.keyEventID for x in all_aos]
        ao_event_ids = [x for x in list(set(ao_event_ids)) if x is not None]
        ao_components = self.ke_components.loc[self.ke_components['key_event_id'].isin(ao_event_ids),:]
        for i,aoc in tqdm(ao_components.iterrows(), total=len(ao_components)):
            ao_event_id = aoc['key_event_id']
            object_source = aoc['object_source']
            process_source = aoc['process_source']

            # Pull out potential disease terms from 'object' and 'process'
            if object_source == 'MESH':
                object_disease = aoc['object_ontology_id']
            else:
                object_disease = None

            if process_source == 'MESH':
                process_disease = aoc['process_ontology_id']
            else:
                process_disease = None

            # Conditionally set disease of interest to either 'process_disease' or 'object_disease'
            # (If both are MeSH terms, we need to debug!)
            two_disease_flag = False
            if process_disease and object_disease:
                two_disease_flag = True
                linked_disease_1 = cai_ont.search(xrefMeSH=process_disease)
                linked_disease_2 = cai_ont.search(xrefMeSH=object_disease)
                if len(linked_disease_1) > 0 and len(linked_disease_2) > 0:
                    disease_node = [linked_disease_1[0], linked_disease_2[0]]
                elif len(linked_disease_1) == 1:
                    linked_disease = linked_disease_1
                elif len(linked_disease_2) == 1:
                    linked_disease = linked_disease_2
                else:
                    # Neither matched to an existing MeSH reference
                    continue
            elif process_disease:
                linked_disease = process_disease
            elif object_disease:
                linked_disease = object_disease
            else:
                continue

            if not two_disease_flag:
                disease_node = cai_ont.search(xrefMeSH=linked_disease)
            
            if len(disease_node) == 0:
                continue

            for dn in disease_node:
                print("LINKING -- {0} --> {1}".format(ao_event_id, dn))
                ao = cai_ont.search(keyEventID=ao_event_id)
                assert len(ao) == 1
                if len(ao[0].aoManifestedAsDisease) == 0:
                    ao[0].aoManifestedAsDisease = [dn]
                else:
                    ao[0].aoManifestedAsDisease.append(dn)