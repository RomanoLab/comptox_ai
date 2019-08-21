# Comptox ontology
A modern bioontology for computational toxicology.

- - -

This is a temporary repository that I'm using to build an ontology to support computational toxicology. Shortly, when it is built out enough to support useful inference, discovery, and graph machine learning, I'll merge it into a larger computational toxicology framework. In the meantime, check out another incomplete comptox repository of mine: http://github.com/JDRomano2/aop_neo4j.

- - -

## Using the ontology

There are two ontologies packaged in this repository:

- `comptox.rdf`: The core ontology, consisting of a class polyhierarchy

- `comptox_populated.rdf`: The same ontology, but populated with individuals for all currently supported classes.

`comptox.rdf` was created by manually building out a class hierarchy and properties in Protégé. Only manually-defined named individuals (e.g., all instances of `Database`) are in the core ontology. `comptox_populated.rdf` was created by running the script `build/add_individuals.py`, which parses the core ontology, places individuals sourced from external data resources, attaches data properties, and links entities where appropriate using object properties.

- - -

## Planned features (an incomplete list)

- Simple import/export integration between Neo4j and OWL
- Support for feature vectors on ontology individuals (for graph machine learning applications)

- - -

## External data sources

When data types are defined multiple times below, I try to merge them in the best way possible. At some point I will clearly enumerate the procedures used to merge equivalent data elements from multiple sources.

- [Hetionet](het.io) (v1.0, with minor tweaks for compatibility reasons)
  - Adverse effects ('side effects' in hetionet)
  - Chemicals ('compounds' in hetionet)
  - Diseases
  - Genes
  - Phenotype ('symptom' in hetionet)
  - StructuralEntity ('anatomy' in hetionet)
- [CTD](ctdbase.org)
  - Chemicals
  - Pathways
  - Diseases
  - Exposure studies
  - Genes
  - Phenotypes (CTD considers GO terms to be phenotypes---this will have to be reconsidered)
- [TOXLINE](https://toxnet.nlm.nih.gov/newtoxnet/toxline.htm)
  - Toxicology literature, including exposure studies and chemical safety reports
- [TRI (Toxic Release Inventory)](https://toxnet.nlm.nih.gov/newtoxnet/tri.htm)
  - Records documenting environmental releases of toxic chemicals from US factories
- [DSSTox](https://comptox.epa.gov/dashboard)
  - Chemicals
  - Product/Use Categories (i.e., a utilitarian type of chemical classification)
  - Assay (labeled as "Assay/Gene" because genes are often the assay endpoint)

- - -

## How to import the ontology into Neo4j:

1. Install Neo4j and switch to a new (empty) graph database
2. [Install the NSMNTX plugin](http://jbarrasa.github.io/neosemantics/#Install)
3. From the Neo4j browser or Cypher shell, import the RDF file:
```
CALL semantics.importRDF("file:///path/to/ontology/comptox_populated.rdf", "RDF/XML");
```