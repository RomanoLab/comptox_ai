"""
ComptoxAI's python package is a toolkit for interacting with and manipulating
ComptoxAI data. The package has two main goals:

1. Make it easier for users to load, query, and interact with graph data in
   various formats.
2. Provide a simplified interface to AI tools and machine learning models
   intended to be used on ComptoxAI.

This section of the documentation shows a brief, simplified workflow that
illustrates many of the major features of the Python package.

.. note::

    This page assumes you have already installed ComptoxAI, built the Neo4j
    database, and created a configuration file. If you have yet to do these
    three tasks, please read the
    :ref:`installation instructions<guide_installing>`.

Usage example
*************

Connect to Neo4j
----------------

Assuming ComptoxAI's graph database is installed, populated, and correctly
configured, it's easy to connect to the database from Python:

.. code-block:: python
   
   from comptox_ai.graph import Graph

   # The "config_file" attribute can be omitted if yours is installed in the
   # default location
   G = Graph.from_neo4j(config_file="./CONFIG.cfg")
   
   print(G)

Convert the data to a different format
--------------------------------------

Neo4j is incredibly powerful for many use cases, but it doesn't provide the
most flexible interface for analyzing graph structure or building machine
learning algorithms. To that end, we'll convert the data to NetworkX:

.. code-block:: python

   G = G.convert(to='networkx')

However, you should always be aware of the capabilities of the formats you are
converting from/to. Not every format can represent all aspects of the graph
database, and certain methods will fail when you try to run them on instances
of `comptox_ai.Graph` in certain formats. For example, there is currently no
way to access node features for heterogeneous graphs when the graph is in
``'graphsage'`` format - you would need to convert it to a format like DGL to
make a command like ``G.node_features`` work without raising an error.

Check basic graph metrics
-------------------------
"""