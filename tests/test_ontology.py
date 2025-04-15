import os
from owlready2 import get_ontology

import pytest

ONTOLOGY_FNAME = "../comptox.rdf" if os.path.exists("../comptox.rdf") else "comptox.rdf"
ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"


class TestOntology:
    def test_ontology_loads_from_file(self):
        ont = get_ontology(ONTOLOGY_FNAME).load()
        assert ont is not None
