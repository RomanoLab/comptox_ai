"""
==============================================
ComptoxAI's Graph versus other graph libraries
==============================================

The :class:`comptox_ai.Graph` class is not meant to replace existing graph data
libraries (such as `NetworkX`_, `SNAP`_, `DGL`_, and others). Instead, it
serves as a wrapper for these and other formats. For each of the supported
internal datatypes, :class:`comptox_ai.Graph` provides access to common graph
properties, metrics, and utility functions, as well as a single point-of-entry
for conversion between these types.

.. _NetworkX: https://networkx.github.io/
.. _SNAP: http://snap.stanford.edu/snappy/index.html
.. _DGL: https://www.dgl.ai/

For example, the following code loads ComptoxAI's graph database from Neo4j,
converts its internal data representation to a NetworkX graph, and then exports
it to a JSON file::

   > from comptox_ai import Graph
   > G = Graph.from_neo4j()
   > G.convert(to_fmt='networkx')
   > print(G)
   > G.save_graph('comptoxai_networkx.json')


"""