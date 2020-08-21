

*******************
ComptoxAI Databases
*******************

ComptoxAI relies mainly on two databases:

1. A *graph database*, implemented in Neo4j
2. A *feature database*, implemented in MongoDB

Briefly, the *graph database* is designed to show the relationships between
entities that are relevant to ComptoxAI, comprising a large, complex network
structure. The *feature database* contains quantitative data tied to the
entities that make up the graph database. We separate these into two databases
largely for performance reasons - graph databases aren't especially good at
storing large quantities of numerical data for each entity, while relational
and NoSQL databases (like MongoDB) don't provide easy interaction with complex
network structures.

The ``comptox_ai.db.GraphDB`` and ``comptox_ai.db.FeatureDB`` classes aim to
make interacting with the two relatively painless. For example, you can extract
a graph from the graph database, and in a single command, fetch the feature
data corresponding to the entities in that graph.

Graph database software is changing constantly. We're more than willing to
consider migrating to a single database solution when a good option is
available. If you think you know of a good alternative, let us know `on GitHub
<https://github.com/JDRomano2/comptox_ai/issues>`_.

.. automodule:: comptox_ai.db
   :members: