from owlready2 import get_ontology

import pytest

ONTOLOGY_FNAME = "comptox.rdf"
POPULATED_ONTOLOGY_FNAME = "comptox_aop.rdf"
ONTOLOGY_IRI = "http://jdr.bio/ontologies/comptox.owl#"

class TestOntology:
    def test_ontology_loads_from_file(self):
        ont = get_ontology(ONTOLOGY_FNAME).load()
        assert ont is not None

    def test_populated_ontology_loads(self):
        ont = get_ontology(POPULATED_ONTOLOGY_FNAME).load()
        assert ont is not None
