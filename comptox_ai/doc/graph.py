"""
ComptoxAI's graph database is meant to completely replace traditional
relational databases used for computational toxicology data. Rather
than storing data in tables with keys linking rows of one table to
rows of another, a graph database stores entities as **nodes** and the
relationships that join entities as **edges**, resulting in a
network-like data structure known to computer scientists as a
**graph**.

Building and installing the database locally
============================================

*(These instructions are incomplete - stay tuned for more info)*

First, make sure you have the prerequisites installed.

Building the complete database consists of 4 steps:

1. Populating the ComptoxAI ontology with individuals for the core
   graph node types.
2. Importing the OWL file into Neo4j.
3. Cleaning up the imported data.
4. Merging other data into the graph database from external sources.

We'll walk through these steps individually:

Populating the ontology with individuals
----------------------------------------

The core ontology for ComptoxAI is already provided as part of the
main code distribution, and can be found at ``data/comptox.owl``. We
use the ontology in the graph database build process because doing so
lets us control the consistency of node labels, data types, and
relationship labels in the final graph database (Neo4j provides no
out-of-box methods for doing so, which is both a strength and a
limitation of the software). The process relies upon the following
rough equivalencies between a populated OWL ontology and a Neo4j-style
graph database:

.. list-table:: :header-rows: 1

    * - OWL Ontology
      - Neo4j-style graph database

    * - Ontology
      - Graph database

    * - Class
      - Node label

    * - Individual
      - Node

    * - Object property
      - Relationship

    * - Data property
      - Node data

Importing the ontology into Neo4j
---------------------------------

Now that we have the ontology (preliminarily) populated with
individuals and object properties that will become nodes and
relationships in the graph database, we can use utility functions from
APOC (Neo4j's standard library) to actually parse the OWL file and
load individuals into the (currently empty) graph database.

Connecting to our instance of the database
==========================================

For users who don't need (or want) to install the full copy of the
database on their own computer, they can access a (possibly slightly
out-of-date) version of the database hosted on our server and
available for public use. This can be done by tweaking your
configuration file to point to our public IP address:

.. admonition:: Hosted database configuration settings

   Contents of `CONFIG.cfg`:

   ::

     [NEO4J]
     Username = neo4j
     Password = neo4j
     Hostname = XXX.XXX.XXX.XXX  <--- we'll update this soon!
     Protocol = bolt
     Port = 7687

API Documentation
=================


"""
from __future__ import division, absolute_import, print_function