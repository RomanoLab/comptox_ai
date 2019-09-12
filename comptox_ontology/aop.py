#!/usr/bin/env python3

"""
Pythonic implementation of Adverse Outcome Pathways
"""

class AdverseOutcomePathway(object):
    """Adverse Outcome Pathway---A framework for conceptualizing how
    toxic exposures result in downstream adverse phenotypic effects,
    especially in humans.

    AOPs basically constitute the "pinnacle" of toxicological
    knowledge, and are therefore one of the central components to the
    Comptox Ontology. Most of the algorithms and models applied to the
    data seek to either discover new AOPs or validate
    existing/proposed AOPs.
    """
    def __init__(self, name):
        """Construct an empty AdverseOutcomePathway.

        Rather than specify all of the components and their
        relationships in the default constructor, we rather build an
        empty AOP and construct its key event graph later.
        """
        self.name = name

    @classmethod
    def aop_from_owl(cls):
        pass

    @classmethod
    def aop_from_neo4j(cls, neo):
        pass

    def build_key_event_graph(self, mie, key_events, adverse_outcomes):
        if isinstance(mies, list):
            
            
        
