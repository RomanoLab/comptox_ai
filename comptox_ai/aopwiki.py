import json
import sys, os
from dataclasses import dataclass, field
from typing import List

from lxml import etree

import ipdb


def get_subtree_element(element, subtree_type):
    element = [x for x in element if x.tag.split("}")[-1] == subtree_type]
    if len(element) == 1:
        return element[0]
    elif len(element) > 1:
        return element
    else:
        return None


@dataclass
class Chemical:
    chemical_id: str
    dsstox_id: str
    casrn: str
    jchem_inchi_key: str
    indigo_inchi_key: str
    synonyms: List[str]


@dataclass
class Stressor:
    name: str
    stressor_id: str
    chemical_ids: List[str]
    chemicals: List[Chemical] = field(default_factory=list)


@dataclass
class KE:
    title: str
    short_name: str
    ke_id: str

    organization_level: str

    stressor_ids: List[str]
    stressors: List[Stressor] = field(default_factory=list)

    upstream_kes: List['KE'] = field(default_factory=list)
    downstream_kes: List['KE'] = field(default_factory=list)


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

        # AOPs and KEs are stored in dicts where their AOPWIKI id is the key and
        # the value is an instance of the corresponding dataclass. These are
        # filled later.
        self.aops = dict()
        self.kes = dict()
        self.stressors = dict()
        self.chemicals = dict()

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
        """Add a single AOP instance to the AOPWiki object from its XML source.

        Parameters
        ----------
        aop_element : lxml.etree._Element
            An XML node corresponding to an Adverse Outcome Pathway (i.e., 
            having the tag `{http://www.aop.org/aop-xml}aop`).

        Returns
        -------
        bool
            `True` if new AOP has been added to `self.aops`, `False` otherwise.
        """
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
            title=title,
            short_name=short_name,
            aop_id=aop_id,
            mie_ids=aop_mie_id,
            ao_ids=aop_ao_id,
            ke_ids=aop_ke_ids
        )

        if new_aop.aop_id not in self.aops.keys():
            self.aops[new_aop.aop_id] = new_aop
            return True
        else:
            print(f"Error: Duplicate AOP id {new_aop.aop_id}")
            print(f"(skipping for now)")
            return False

    def add_ke(self, ke_element):
        """Add a single Key Event instance to the AOPWiki object from its
        XML source.

        Parameters
        ----------
        ke_element : lxml.etree._Element
            An XML node corresponding to a Key Event (i.e., having the tag
            `{http://www.aop.org/aop-xml}key-element`).

        Returns
        -------
        bool
            `True` if new KE has been added to `self.kes`, `False` otherwise.
        """
        title = get_subtree_element(ke_element, 'title').text
        short_name = get_subtree_element(ke_element, 'short-name').text
        ke_id = ke_element.get('id')

        org_level = get_subtree_element(ke_element,
                                        'biological-organization-level').text

        stressors = get_subtree_element(ke_element, 'key-event-stressors')
        stressor_ids = []
        if stressors is not None:
            for stressor in stressors:
                stressor_ids.append(stressor.get('stressor-id'))

        new_ke = KE(
            title=title,
            short_name=short_name,
            ke_id=ke_id,
            organization_level=org_level,
            stressor_ids=stressor_ids
        )

        if new_ke.ke_id not in self.kes.keys():
            self.kes[new_ke.ke_id] = new_ke
            return True
        else:
            print(f"Error: Duplicate Key Event id {new_ke.ke_id}")
            print(f"(skipping for now)")
            return False

    def add_stressor(self, stressor_element):
        """Add a single Stressor instance to the AOPWiki object from its
        XML source.

        Parameters
        ----------
        ke_element : lxml.etree._Element
            An XML node corresponding to a stressor (i.e., having the tag
            `{http://www.aop.org/aop-xml}stressor`).

        Returns
        -------
        bool
            `True` if new stressor has been added to `self.stressors`,
            `False` otherwise.
        """
        name = get_subtree_element(stressor_element, 'name').text

        stressor_id = stressor_element.get('id')

        chemicals = get_subtree_element(stressor_element, 'chemicals')
        chemical_ids = []
        if chemicals is not None:
            for chem in chemicals:
                chemical_ids.append(chem.get('chemical-id'))

        new_stressor = Stressor(
            name=name,
            stressor_id=stressor_id,
            chemical_ids=chemical_ids,
        )

        if new_stressor.stressor_id not in self.stressors.keys():
            self.stressors[new_stressor.stressor_id] = new_stressor
            return True
        else:
            print(f"Error: Duplicate stressor id {new_stressor.stressor_id}")
            print(f"(skipping for now)")
            return False

    def add_chemical(self, chemical_element):
        """Add a single Chemical instance to the AOPWiki object from its
        XML source.

        Parameters
        ----------
        ke_element : lxml.etree._Element
            An XML node corresponding to a chemical (i.e., having the tag
            `{http://www.aop.org/aop-xml}chemical`).

        Returns
        -------
        bool
            `True` if new chemical has been added to `self.chemicals`,
            `False` otherwise.
        """
        chemical_id = chemical_element.get('id')

        dsstox_id = get_subtree_element(chemical_element, 'dsstox-id').text
        casrn = get_subtree_element(chemical_element, 'casrn').text
        jchem_inchi_key = get_subtree_element(chemical_element, 'jchem-inchi-key').text
        indigo_inchi_key = get_subtree_element(chemical_element, 'indigo-inchi-key').text

        syn_nodes = chemical_element.get('synonyms')
        if syn_nodes:
            synonyms = [x.text for x in syn_nodes]
        else:
            synonyms = []

        new_chemical = Chemical(
            chemical_id=chemical_id,
            dsstox_id=dsstox_id,
            casrn=casrn,
            jchem_inchi_key=jchem_inchi_key,
            indigo_inchi_key=indigo_inchi_key,
            synonyms=synonyms,
        )

        if not new_chemical.chemical_id in self.chemicals.keys():
            self.chemicals[new_chemical.chemical_id] = new_chemical
            return True
        else:
            print(f"Error: Duplicate chemical id {new_chemical.chemical_id}")
            print(f"(skipping for now")
            return False

    def add_all_aops(self):
        aops = self.get_all_elements_of_type('aop')

        for aop in aops:
            self.add_aop(aop)

    def add_all_kes(self):
        kes = self.get_all_elements_of_type('key-event')

        for ke in kes:
            self.add_ke(ke)

    def add_all_chemicals(self):
        chemicals = self.get_all_elements_of_type('chemical')

        for chem in chemicals:
            self.add_chemical(chem)

    def add_all_stressors(self):
        stressors = self.get_all_elements_of_type('stressor')

        for stressor in stressors:
            self.add_stressor(stressor)

    def link_key_event_relationships(self):
        """Link elements of `self.kes` via existing `'upstream-id'` and 
        `'downstream-id'` values pointing to adjacent key event nodes in the key
        event graph.

        Since key event relationships are not constrained to individual AOPs,
        the resulting data structure can be interpreted as a single (possibly
        unconnected) graph across which inferences can be performed. This graph
        is necessarily compliant with the axioms stated by ComptoxAI's ontology.
        """
        kers = self.get_all_elements_of_type('key-event-relationship')

        for k in kers:
            title = get_subtree_element(k,'title')
            
            upstream_id = get_subtree_element(title,'upstream-id').text
            downstream_id = get_subtree_element(title,'downstream-id').text

            self.kes[upstream_id].downstream_kes.append(downstream_id)
            self.kes[downstream_id].upstream_kes.append(upstream_id)

    def parse_wiki(self):
        """Algorithmically parse the contents of AOPWiki specified in the XML
        source loaded into `self.tree`.

        This method accepts no arguments and returns no values; the entire
        procedure is performed on data loaded during `self.init` and only
        modifies existing data members. 
        """
        # First we add the elements
        self.add_all_aops()
        self.add_all_kes()
        self.add_all_chemicals()
        self.add_all_stressors()

        # Then we link them together
        for _,a in self.aops.items():
            
            mie_ids = a.mie_ids
            if a.mie_ids:
                a.mies = [self.kes[x] for x in mie_ids]
            
            ke_ids = a.ke_ids
            if a.ke_ids:
                a.kes = [self.kes[y] for y in ke_ids]
            
            ao_ids = a.ao_ids
            if a.ao_ids:
                a.aos = [self.kes[z] for z in ao_ids]

        for _,k in self.kes.items():
            # Link to stressors
            stressor_ids = k.stressor_ids
            k.stressors = [self.stressors[x] for x in stressor_ids]

        for _,s in self.stressors.items():
            chemical_ids = s.chemical_ids
            s.chemicals = [self.chemicals[x] for x in chemical_ids]

        # Finally, we add key event relationships to key events
        self.link_key_event_relationships()

    def print_wiki_info(self):
        """Print statistics describing the parsed AOP-Wiki data, including node
        counts, relationship counts, and various other details.
        """
        aops = self.aops.values()
        kes = self.kes.values()

        rel_counts = {
            'AOP-(has_mie)--------->KeyEvent': sum([len(x.mies) for x in aops]),
            'AOP-(has_ke)---------->KeyEvent': sum([len(x.kes) for x in aops]),
            'AOP-(has_ao)---------->KeyEvent': sum([len(x.aos) for x in aops]),
            'KE--(has_stressor)---->Stressor': sum([len(x.stressors) for x in kes]),
            'KE<-(ke_relationship)->KE': sum([len(x.downstream_kes) for x in kes]),
        }

        print(f"AOP WIKI")
        print("--------")
        print()
        print(f"Counts of element types:")
        print(f"  - AOPs:       {len(self.aops)}")
        print(f"  - Key Events: {len(self.kes)}")
        print(f"  - Stressors:  {len(self.stressors)}")
        print(f"  - Chemicals:  {len(self.chemicals)}")
        print()
        print(f"Counts of relationships by type:")
        [print(f"  - {k}: {v}") for k, v in rel_counts.items()]

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    wiki_xml_fname = os.path.join(script_dir, '..', 'data', 'external',
                                  'aopwiki', 'aop-wiki-xml-2019-07-01.xml')

    if os.path.exists(wiki_xml_fname):
        wiki = AopWiki(xml_fname=wiki_xml_fname)
        wiki.print_wiki_info()

    else:
        sys.exit(1)
