"""
Graph databases have many advantages - both theoretical and practical - over traditional relational databases. Many good descriptions of graph database concepts are available on the internet, but users will probably find it helpful to hear this information from the perspective of biomedical knowledge representation and AI (and, of course, ComptoxAI in particular).

Behavior of Neo4j
=================

Induced Subgraphs
-----------------

An induced subgraph :math:`G[S]` is a subgraph consisting of a set of (user-specified) vertices :math:`S` and all edges that have both endpoints in :math:`S`. Induced subgraphs provide a very convenient way to focus on only the relevant structures of a graph in the context of a set of vertices (which generally share some useful properties you are interested in analyzing).

Neo4j implicitly (and efficiently) constructs induced subgraphs when a query performs a match on multiple nodes unless you tell it to do otherwise. This feature simplifies data extraction tasks used for studying local topologies and building data structures used for machine learning. 

This feature is usually only beneficial, and it will make your life easier when working with ComptoxAI's graph database, but users need to be aware of the potential risks this can lead to. One of these is related to performance - if you are only interested in studying the vertices returned by a certain query, and the induced subgraph on those vertices is densely connected, the size of the query response can grow extremely rapidly. If you only need to store the nodes, use `RETURN n`, where `n` is a variable pointing to a node.
"""

from __future__ import division, absolute_import, print_function