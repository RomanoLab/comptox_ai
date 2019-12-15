.. _ontology:

*************************************************
The ComptoxAI Ontology (:class:`ComptoxOntology`)
*************************************************

The ontology is the main point of interaction with both the knowledge
representation and the knowledge base that---together---comprise
Comptox Ontology. The implementation makes heavy use of ontology, RDF,
and Neo4j libraries to provide rich functionality without the need for
extensive boilerplate code.

Populating the OWL Ontology
===========================

All distributions of ComptoxAI should come bundled with an RDF file named
``comptox.rdf``, which is an OWL2-formatted ontology file containing all
classes, properties, relationships, and other annotations that are part of core
class polyhierarchy. This file is produced by the developers of ComptoxAI and
should not be modified by users in most situations. Subsequent scripts
(described in following paragraphs) are dependent upon this file, and any
changes made could break the build process. If there is an issue with the core
ontology (which can be interacted with via Protege or other ontology viewing
software), we strongly encourage you to contact us (see
http://comptox.ai/contact.html).

The ``comptox_ai/scripts/build/`` directory contains the code needed to populate
the ontology's class polyhierarchy with individuals. Currently, two scripts are
included:

1. ``1_add_individuals.py``: Adds individuals for all ontology classes that are
   not related to Adverse Outcome Pathways, including data from Hetionet, the
   Comparative Toxicogenomics Database, and other external sources.
2. ``2_merge_aopwiki.py``: Parses the AOP-Wiki's XML distribution and builds it
   into the ontology, linking it to previously processed nodes where
   appropriate.

We are considering merging these into a single script, but due to the amount of
time it takes to construct the ontology, we currently prefer breaking it into
two standalone stages that can be run separately.

Importing the OWL Ontology into Neo4j
=====================================

We use the `NSMNTX package <http://neo4j-labs.github.io/neosemantics/>`_ to
import the final ontology containing individuals into a (previously empty) Neo4j
graph database. You should follow the instructions for NSMNTX in order to
install this plugin. Once the plugin is installed and functioning, you can
import the OWL ontology using a command similar to the following (i.e., change
the path of the RDF file as necessary:

::

  CALL semantics.importRDF(
      "file:///some/path/goes/here/comptox_aop.rdf",
      "RDF/XML"
  );

At this point, the contents of the ontology are now loaded into Neo4j as a graph
database. We encourage you to next read the contents of :class:`Graph` to learn
how to interact with the data originally sourced from the ontology.

API Documentation
=================

.. automodule:: comptox_ai.ontology
   :members:
