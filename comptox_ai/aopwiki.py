import json
from dataclasses import dataclass, field
from typing import List

from lxml import etree

import ipdb


def get_subtree_element(element, subtree_type):
    element = [x for x in element if x.tag.split("}")[-1] == subtree_type]
    # try:
    #     assert len(element) <= 1
    # except AssertionError:
    #     ipdb.set_trace()
    #     print()
    if len(element) == 1:
        return element[0]
    elif len(element) > 1:
        return element
    else:
        return None

@dataclass
class Stressor:
    name: str
    stressor_id: str

@dataclass
class KE:
    title: str
    short_name: str
    ke_id: str

    organization_level: str

    stressor_ids: List[str]
    stressors: List[Stressor] = field(default_factory=list)

@dataclass
class AOP:
    title: str
    short_name: str
    aop_id: str
    
    mie_ids: List[str]
    ao_ids: List[str]
    ke_ids: List[str]
    
    mies: List[KE] = field(default_factory=list)
    aos: List[KE] = field(default_factory=list)
    kes: List[KE] = field(default_factory=list)


class AopWiki(object):
    def __init__(self, xml_fname):
        self.xml_fname = xml_fname

        self.tree = etree.parse(self.xml_fname)
        self.root = self.tree.getroot()

        self.ex_chem = [x for x in self.root if x.tag.split("}")[-1] == 'chemical'][0]
        self.ex_stress = [x for x in self.root if x.tag.split("}")[-1] == 'stressor'][0]
        self.ex_aop = [x for x in self.root if x.tag.split("}")[-1] == 'aop'][0]
        self.aop_xml_list = [x for x in self.root if x.tag.split("}")[-1] == 'aop']

        # AOPs and KEs are stored in dicts where their AOPWIKI id is the key and the value
        # is an instance of the corresponding dataclass. These are filled later.
        self.aops = dict()
        self.kes = dict()

        self.parse_wiki()

    def get_all_elements_of_type(self, type):
        """Fetch all elements in self.root that match a particular element type (e.g., `aop`).
        
        Parameters
        ----------
        type : str
            String label corresponding to an entity type in the AOP wiki. Some examples include
            'aop', 'stressor', 'chemical', 'key-event'...
        """

        matching_nodes = [x for x in self.root if x.tag.split("}")[-1] == type]

        if len(matching_nodes) > 0:
            return matching_nodes
        else:
            return None

    def add_aop(self, aop_element):
        title = get_subtree_element(aop_element, 'title').text
        short_name = get_subtree_element(aop_element, 'short-name').text
        aop_id = aop_element.get('id')

        aop_mie = get_subtree_element(aop_element, 'molecular-initiating-event')
        if isinstance(aop_mie, etree._Element):
            aop_mie_id = [aop_mie.get('key-event-id')]
        elif isinstance(aop_mie, list):
            aop_mie_id = [x.get('key-event-id') for x in aop_mie]
        elif aop_mie is None:
            print(f"Warning: No Molecular Initiating Event for AOP: {title}")
            aop_mie_id = None
        else:
            ipdb.set_trace()
            print()
        
        aop_ao = get_subtree_element(aop_element, 'adverse-outcome')
        if isinstance(aop_ao, etree._Element):
            aop_ao_id = [aop_ao.get('key-event-id')]
        elif isinstance(aop_ao, list):
            aop_ao_id = [x.get('key-event-id') for x in aop_ao]
        elif aop_ao is None:
            print(f"Warning: No Adverse Outcome for AOP: {title}")
            aop_ao_id = None
        else:
            ipdb.set_trace()
            print()
            
        
        aop_kes = get_subtree_element(aop_element, 'key-events')
        aop_ke_ids = [x.get('id') for x in aop_kes]

        new_aop = AOP(
            title = title,
            short_name = short_name,
            aop_id = aop_id,
            
            mie_ids = aop_mie_id,
            ao_ids = aop_ao_id,
            ke_ids = aop_ke_ids
        )

        if not new_aop.aop_id in self.aops.keys():
            self.aops[new_aop.aop_id] = new_aop
            return True
        else:
            print(f"Error: Duplicate AOP id {new_aop.aop_id}")
            print(f"(skipping for now)")
            return False

    def add_ke(self, ke_element):
        title = get_subtree_element(ke_element, 'title').text
        short_name = get_subtree_element(ke_element, 'short-name').text
        ke_id = ke_element.get('id')

        org_level = get_subtree_element(ke_element, 'biological-organization-level').text
        
        stressors = get_subtree_element(ke_element, 'key-event-stressors')
        stressor_ids = []
        if stressors is not None:
            for stressor in stressors:
                stressor_ids.append(stressor.get('stressor-id'))

        new_ke = KE(
            title = title,
            short_name = short_name,
            ke_id = ke_id,
            organization_level = org_level,
            stressor_ids = stressor_ids
        )

        if not new_ke.ke_id in self.kes.keys():
            self.kes[new_ke.ke_id] = new_ke
            return True
        else:
            print(f"Error: Duplicate Key Event id {new_ke.ke_id}")
            print(f"(skipping for now)")
            return False


    def add_all_aops(self):
        aops = self.get_all_elements_of_type('aop')

        for aop in aops:
            self.add_aop(aop)

    def add_all_kes(self):
        kes = self.get_all_elements_of_type('key-event')

        for ke in kes:
            self.add_ke(ke)


    def parse_wiki(self):
        # First we add the elements
        self.add_all_aops()
        self.add_all_kes()
        #self.add_all_chemicals()
        #self.add_all_stressors()

        # Then we link them together