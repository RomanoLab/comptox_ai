"""
Graph data formats
******************

ComptoxAI manages the interchange of data in a number of disparate formats. To
do this dynamically, its critically important to ensure that all of the
datatype handlers write to and read from a well-specified intermediate format.

Here, we describe the (Python-centric) specification for this format.

.. topic:: What's up with the ``ns0__`` and ``owl__`` prefixes?

  These prefixes indicate the namespace that each entity in ComptoxAI belongs
  to. They can be used to determine if an entity (e.g., a node, a relationship,
  a label) was defined exclusively for use in ComptoxAI, or if it is an
  externally defined entity being 'reused' by ComptoxAI.

Graph
-----

The graph object is a wrapper around any descendant of
comptox_ai.graph.GraphDataMixin. It provides a consistent interface for
accessing members of the actual GraphDataMixin objects. The graph itself is
stored in the private attribute _data, which should only be accessed directly
by experienced users who aren't afraid to potentially screw up their data.

See the API reference for a complete description of the methods provided by
the comptox_ai.Graph class.

.. seealso:: :ref:`Graph`

Nodes
-----

Nodes are 3-tuples, where the first element is an integer node ID, the
second element is a node label, and the third element is a dictionary of node
properties::

  (3, 'ns0__Gene', {'ns0__commonName': 'SCARA3', ...})

The node ID is automatically assigned by Neo4j upon node creation. If the data
are created in another format prior to loading in Neo4j, any (unique) value may
be used in its stead. If the data are subsequently loaded and then retrieved
from Neo4j, the newly assigned Neo4j node ID will take the place of the old
placeholder.

The properties dictionary may be left empty, but an effort should be made to
populate node properties with whichever data are available and defined for the
current node type.

Relationships
-------------

Relationships are 4-tuples, where the first element is the ID for the starting
node :math:`u`, the second element is a string relationship type, the third
element is the ending node :math:`v`, and the fourth element is a dictionary of
(optional) relationship properties::

  (18288, 'ns0__anatomyUpregulatesGene', 3, {})

The use of relationship properties is encouraged, but ultimately less important
to current models than node properties.

"""
