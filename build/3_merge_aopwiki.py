#!/usr/bin/env python3

from owlready2 import get_ontology
import pandas as pd
from tqdm import tqdm
from lxml import etree
import json
from collections import Counter

import ipdb, traceback, sys

ONTOLOGY_FNAME = "../comptox.rdf"
ONTOLOGY_POPULATED_FNAME = "../comptox_populated.rdf"
ONTOLOGY_POPULATED_LINKED_FNAME = "../comptox_populated_linked.rdf"
ONTOLOGY_AOP_FNAME = "../comptox_aop.rdf"

ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"
ONTOLOGY_POPULATED_IRI = 'http://jdr.bio/ontologies/comptox-full.owl#'

def strip_tag(tag):
    return tag.split("}")[-1]

OWL = get_ontology("http://www.w3.org/2002/07/owl#")

ont = get_ontology("../comptox_populated_linked.rdf").load()

kes = pd.read_csv("../data/aopwiki/aop_ke_mie_ao.tsv",
                  sep="\t",
                  header=None,
                  names=['aop_id',
                         'key_event_id',
                         'key_event_type',
                         'key_event_name'])

kers = pd.read_csv("../data/aopwiki/aop_ke_ker.tsv",
                   sep="\t",
                   header=None,
                   names=['aop_id',
                          'upstream_event_id',
                          'downstream_event_id',
                          'relationship_id',
                          'direct_or_indirect',
                          'evidence',
                          'quantitative_understanding'])

ke_components = pd.read_csv("../data/aopwiki/aop_ke_ec.tsv",
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

# aop_wiki = etree.parse("../data/aopwiki/aop-wiki-xml-2019-07-01.xml")
# root = aop_wiki.getroot()
# ex_chem = [x for x in root if x.tag.split("}")[-1] == 'chemical'][0]
# ex_stress = [x for x in root if x.tag.split("}")[-1] == 'stressor'][0]
# ex_aop = [x for x in root if x.tag.split("}")[-1] == 'aop'][0]
# aop_xml_list = [x for x in root if x.tag.split("}")[-1] == 'aop']
with open("../data/aopwiki/aops.json", 'r') as fp:
    aops = json.load(fp)
aop_dict = {}
for a in aops:
    aop_dict[str(a['id'])] = a

print()
print("=================================")
print("===== LOADED AOP-WIKI DATA: =====")
print()
print("== COUNT OF ENTITIES ==")
print("Key events:              {0}".format(len(kes)))
print("Key event relationships: {0}".format(len(kers)))
print("Key event components:    {0}".format(len(ke_components)))
print()
print("=================================")
print()

# print("Count of AOP Wiki element types:")
# print(Counter([x.tag.split("}")[-1] for x in root]).most_common())


# ADD AOP WIKI NODES TO GRAPH
already_parsed_kes = []
already_parsed_aops = []
for i, ke in tqdm(kes.iterrows(), total=len(kes)):
    ke_type = ke.key_event_type
    ke_id = ke.key_event_id
    ke_name = ke.key_event_name
    ke_aop_id = ke.aop_id

    if ke_id in already_parsed_kes:
        continue  # Don't re-add something we've already seen
    already_parsed_kes.append(ke_id)

    # Prepend "ke_" to avoid name conflicts
    safe_name = "ke_"+ke_name.lower().replace(" ","_")

    # do we have a node already for the AOP?
    aop_id = ke.aop_id
    if aop_id in already_parsed_aops:
        existing_aop = True
    else:
        existing_aop = False

    if ke_type == 'MolecularInitiatingEvent':
        new_mie_node = ont.MolecularInitiatingEvent(safe_name,
                                                    keyEventID=ke_id,
                                                    keyEventName=ke_name)
        if existing_aop:
            # add this MIE to the AOP
            aop_node = ont.search(xrefAOPWiki=aop_id)
            assert len(aop_node) == 1
            aop_node = aop_node[0]
            aop_node.aopHasMIE.append(new_mie_node)
        else:
            # Create an AOP with this as an MIE
            if aop_id.split(":")[-1] in aop_dict.keys(): # Don't do anything if it's an obsolete AOP
                aop_data = aop_dict[aop_id.split(":")[-1]]
                safe_aop_name = 'aop_'+aop_data['short_name'].lower().replace(" ","_")
                new_aop_node = ont.AOP(safe_aop_name)
                new_aop_node.aopHasMIE = [new_mie_node]
                
    elif ke_type == 'KeyEvent':
        new_ke_node = ont.KeyEvent(safe_name,
                                   keyEventID=ke_id,
                                   keyEventName=ke_name)
        if existing_aop:
            # add this MIE to the AOP
            aop_node = ont.search(xrefAOPWiki=aop_id)
            assert len(aop_node) == 1
            aop_node = aop_node[0]
            aop_node.aopContainsKE.append(new_ke_node)
        else:
            # Create an AOP with this as an MIE
            if aop_id.split(":")[-1] in aop_dict.keys(): # Don't do anything if it's an obsolete AOP
                aop_data = aop_dict[aop_id.split(":")[-1]]
                safe_aop_name = 'aop_'+aop_data['title'].lower().replace(" ","_")
                new_aop_node = ont.AOP(safe_aop_name)
                new_aop_node.aopContainsKE = [new_ke_node]

    elif ke_type == 'AdverseOutcome':
        new_ao_node = ont.AdverseOutcome(safe_name,
                                         keyEventID=ke_id,
                                         keyEventName=ke_name)
        if existing_aop:
            # add this MIE to the AOP
            aop_node = ont.search(xrefAOPWiki=aop_id)
            assert len(aop_node) == 1
            aop_node = aop_node[0]
            aop_node.aopCausesAO.append(new_ao_node)
        else:
            # Create an AOP with this as an MIE
            if aop_id.split(":")[-1] in aop_dict.keys(): # Don't do anything if it's an obsolete AOP
                aop_data = aop_dict[aop_id.split(":")[-1]]
                safe_aop_name = 'aop_'+aop_data['title'].lower().replace(" ","_")
                new_aop_node = ont.AOP(safe_aop_name)
                new_aop_node.aopCausesAO = [new_ao_node]

    else:
        raise ValueError("Unexpected key event type: {}".format(ke_type))

# Come back to this to parse level of organization, supporting evidence, biological events, etc...
# for elem in root:
#     s_tag = strip_tag(elem.tag)
#     if s_tag == 'key-event':
#         ipdb.set_trace()
#         print()
#     elif s_tag == 'key-event-relationship':
#         pass
#     elif s_tag == 'stressor':
#         pass
#     elif s_tag == 'biological-object':
#         pass
#     elif s_tag == 'biological-process':
#         pass
#     elif s_tag == 'chemical':
#         pass
#     elif s_tag == 'aop':
#         pass
#     elif s_tag == 'taxonomy':
#         pass
#     elif s_tag == 'biological-action':
#         pass
#     elif s_tag == 'vendor-specific':
#         pass
#     else:
#         raise ValueError("Unexpected XML tag in AOP Wiki data: {0}".format(s_tag))

# ADD AOP WIKI RELATIONSHIPS TO GRAPH
already_parsed_kers = []
for i,ker in kers.iterrows():
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

    upstream_event = ont.search(keyEventID=upstream_event_id)
    downstream_event = ont.search(keyEventID=downstream_event_id)

    if (upstream_event == []) or (downstream_event == []):
        ipdb.set_trace()
        print()

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


# LINK AOP NODES TO OTHER ONTOLOGY NODES


print("Writing to disk as RDF file...")
try:
    ont.save(file=ONTOLOGY_AOP_FNAME, format="rdfxml")
    pass
except TypeError:
    extype, value, tb = sys.exc_info()
    print("Uh oh, something went wrong when serializing the populated ontology to disk. Entering debug mode...")
    traceback.print_exc()
    ipdb.post_mortem(tb)
