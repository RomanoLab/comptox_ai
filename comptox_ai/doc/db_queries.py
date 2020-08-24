r'''
================
Database Queries
================

Introduction
============

ComptoxAI is largely built around two databases:

1. A *graph database* of entities, their semantic types, and the relationships
   that link these entities. This is implemented using Neo4j.
2. A *feature database* that maps the entities in the graph database to
   structured documents describing various aspects of those entities. This is
   implemented using MongoDB.

This document is meant to show how you can interact with these two databases to
learn meaningful things about computational toxicology data. We'll start by
taking at how these data are formatted in the source database, and then we'll
discuss how to retrieve and manipulate them using ComptoxAI.

.. tip::
   ComptoxAI uses two separate databases because current graph database
   implementations aren't especially good at handling large amounts of feature
   data efficiently. It turns out that analyses can be conducted *faster* when
   you isolate graph data into a graph database and quantitative feature data
   into a document store (like MongoDB).

   A major goal of the ComptoxAI Python package is to make the integration of these two databases as painless as possible to the end user. We're keeping
   an eye out for new graph database technologies that would allow us to
   integrate the databases into a single resource without having to sacrifice
   performance.

Example - Hydroxychloroquine
============================

Graph database representation
-----------------------------

For example, consider the chemical *hydroxychloroquine* (118-42-3 |
DTXSID8023135). Hydroxychloroquine's node in the graph database looks like::

  {
    "identity": 32519,
    "labels": [
      "Chemical",
      "NamedIndividual",
      "Resource"
    ],
    "properties": {
      "commonName": "Hydroxychloroquine",
      "inchiKey": "XXSMGPRMXLTPCZ-UHFFFAOYSA-N",
      "inchi": "InChI=1S/C18H26ClN3O/c1-3-22(11-12-23)10-4-5-14(2)21-17-8-9-20-18-13-15(19)6-7-16(17)18/h6-9,13-14,23H,3-5,10-12H2,1-2H3,(H,20,21)",
      "xrefDrugbank": "DB01611",
      "xrefMeSHUI": "D006886",
      "xrefPubchemSID": 315673741,
      "xrefCasRN": "118-42-3",
      "uri": "http://jdr.bio/ontologies/comptox.owl#chem_hydroxychloroquine",
      "chemicalIsInCTD": true,
      "chemicalIsDrug": true,
      "xrefPubchemCID": 3652,
      "xrefDtxsid": "DTXSID8023135"
    }
  }

These are mainly just identifiers, but things get more interesting when we look
at relationships to other nodes in the graph database. At the time of writing,
the node is directly linked to 480 other nodes in the database. Here is one of
those relationships::

  {
    "identity": 1210864,
    "start": 32519,
    "end": 19842,
    "type": "CHEMICALASSOCIATESWITHDISEASE",
    "properties": {}
  }

In this case, the start node (32519) is hydroxychloroquine, the end node
(22421) is *spinal cord compression*::

  {
    "identity": 19842,
    "labels": [
      "Resource",
      "NamedIndividual",
      "Disease"
    ],
    "properties": {
      "commonName": "Spinal Cord Compression",
      "uri": "http://jdr.bio/ontologies/comptox.owl#dis_spinalcordcompression",
      "xrefMeSH": "D013117"
    }
  }

Or in other words:

.. math:: \langle\textit{hydroxychloroquine}\rangle\,\texttt{CHEMICAL\_ASSOCIATES\_WITH\_DISEASE}\,\langle\textit{spinal cord compression}\rangle

Feature database representation
-------------------------------

Quantitative feature data are stored in MongoDB as *structured documents* that
look similar to JSON documents. These documents include fields such as chemical
molecular descriptors, assay measurements, gene loci, literature references,
biochemical values, miscellaneous free text, and others.
'''
