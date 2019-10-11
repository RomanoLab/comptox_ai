.. _graph:

*******************************************************************************
Graph database of computational toxicology concepts (:class:`comptox_ai.Graph`)
*******************************************************************************

ComptoxAI's graph database is meant to completely replace traditional
relational databases used for computational toxicology data. Rather than
storing data in tables - with keys linking rows of one table to rows of another
- a graph database stores entities as **nodes** and the relationships that join
entities as **edges**, resulting in a network-like data structure known to
computer scientists as a **graph**.

Installing the database locally
===============================

*(Instructions coming soon)*

Connecting to our instance of the database
==========================================

For users who don't need (or want) to install the full copy of the database on
their own computer, they can access a (possibly slightly out-of-date) version
of the database hosted on our server and available for public use. This can be
done by tweaking your configuration file to point to our public IP address:

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

.. automodule:: comptox_ai.graph
   :members:
